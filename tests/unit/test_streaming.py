"""Bounds and unsafe partial citations/Unicode, without replacing HTTP/service gates."""

import asyncio
import json
from types import SimpleNamespace
from uuid import uuid4

import pytest

from rag_core.api.streaming import QueryStreamResponse
from rag_core.application.admission import QueryAdmission, QueryBusy
from rag_core.contracts.sse import AnswerDeltaEvent, DeltaData, MetaData, MetaEvent
from rag_core.contracts.v1 import HistoryMetadata
from rag_core.domain.answers import AnswerError
from rag_core.domain.metadata import ScopeError
from rag_core.domain.streaming import ProvisionalAnswer, StreamPolicy

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("escaped", [False, True])
def test_split_json_unicode_escapes_and_citation_batch(escaped):
    text = "Hà Nội 🐈 là thủ đô [c1]. Tiếp theo.\n"
    wire = json.dumps({"answer": text, "citations": []}, ensure_ascii=escaped)
    decoder = ProvisionalAnswer({"c1"})
    batches = []
    for char in wire:
        batches.extend(decoder.feed(char))
    batches.extend(decoder.finish())
    assert "".join(batches) == decoder.text == text
    assert json.loads(decoder.raw)["answer"] == text


@pytest.mark.parametrize("marker", ["c999", "C1", "c0", "e1", "c 1"])
def test_unknown_or_malformed_citation_never_leaves_batch(marker):
    decoder = ProvisionalAnswer({"c1"})
    with pytest.raises(AnswerError, match="invalid_citation"):
        decoder.feed(json.dumps({"answer": f"Secret claim [{marker}]. "}))


def test_open_citation_sentence_is_held_and_sentence_and_wire_limits_fail():
    decoder = ProvisionalAnswer({"c1"}, 64)
    assert decoder.feed('{"answer":"Fact [c') == []
    assert decoder.feed("1]. ") == ["Fact [c1]. "]
    with pytest.raises(AnswerError):
        decoder.feed("x" * 65)
    with pytest.raises(AnswerError):
        ProvisionalAnswer(set()).feed("x" * 65537)
    incomplete = ProvisionalAnswer({"c1"})
    incomplete.feed('{"answer":"Fact [c1')
    with pytest.raises(AnswerError):
        incomplete.finish()


@pytest.mark.parametrize("escape", ['\\ud800"', "\\udc00", "\\ud800x", "\\q"])
def test_invalid_unicode_or_json_escape_fails(escape):
    with pytest.raises(AnswerError):
        ProvisionalAnswer(set()).feed('{"answer":"' + escape)


@pytest.mark.asyncio
async def test_bounded_admission_timeout_cancel_release_and_no_queue_bypass():
    admission = QueryAdmission(1, 1, 0.03)
    first = await admission.acquire()
    waiting = asyncio.create_task(admission.acquire())
    await asyncio.sleep(0)
    assert (admission.active, admission.waiting) == (1, 1)
    with pytest.raises(QueryBusy):
        await admission.acquire()
    with pytest.raises(QueryBusy):
        await waiting
    waiting = asyncio.create_task(admission.acquire())
    await asyncio.sleep(0)
    waiting.cancel()
    with pytest.raises(asyncio.CancelledError):
        await waiting
    assert admission.waiting == 0
    first.release()
    first.release()
    second = await admission.acquire()
    assert admission.active == 1
    second.release()
    assert admission.active == admission.waiting == 0


class FlowStream:
    def __init__(self):
        self.request_id = uuid4()
        self.count = 0
        self.closed = False
        self.stale = False
        self.close_delay = 0
        self.closing = asyncio.Event()

    async def validate_scope(self):
        if self.stale:
            raise ScopeError("session_scope_changed")

    async def events(self):
        try:
            self.count += 1
            yield MetaEvent(
                event="meta",
                id=1,
                data=MetaData(
                    request_id=self.request_id,
                    session_id=uuid4(),
                    scope_revision=1,
                    domain="default",
                    history=HistoryMetadata(
                        received_messages=0,
                        retained_messages=0,
                        received_tokens=0,
                        retained_tokens=0,
                        truncated=False,
                    ),
                ),
            )
            for index in range(10000):
                self.count += 1
                yield AnswerDeltaEvent(
                    event="answer_delta", id=index + 2, data=DeltaData(text="batch")
                )
        finally:
            self.closing.set()
            if self.close_delay:
                await asyncio.sleep(self.close_delay)
            self.closed = True


@pytest.mark.asyncio
async def test_slow_send_bounds_producer_and_cleanup_within_send_timeout():
    stream = FlowStream()
    admission = QueryAdmission(1, 0, 0.05)
    response = QueryStreamResponse(
        stream, admission, StreamPolicy(send_timeout=0.03, buffer_events=2)
    )
    writes = []

    async def send(message):
        writes.append(message)
        if message["type"] == "http.response.body":
            await asyncio.Event().wait()

    async def receive():
        await asyncio.Event().wait()

    async with asyncio.timeout(1):
        await response({"type": "http"}, receive, send)
    assert stream.count <= 4  # two queued, one producer-held, one sender-held event
    assert stream.closed and admission.active == admission.waiting == 0
    assert sum(b"event: error" in item.get("body", b"") for item in writes) <= 1


@pytest.mark.asyncio
async def test_send_boundary_discards_already_queued_stale_events():
    stream = FlowStream()
    admission = QueryAdmission(1, 0, 0.05)
    response = QueryStreamResponse(stream, admission, StreamPolicy())
    writes = []

    async def send(message):
        writes.append(message)
        if b"event: meta" in message.get("body", b""):
            await asyncio.sleep(0)
            stream.stale = True

    async def receive():
        await asyncio.Event().wait()

    await response({"type": "http"}, receive, send)
    wire = b"".join(message.get("body", b"") for message in writes)
    assert b"event: answer_delta" not in wire and b"event: done" not in wire
    assert wire.count(b"event: error") == 1 and b"session_scope_changed" in wire
    assert stream.closed and admission.active == 0


@pytest.mark.asyncio
async def test_disconnect_cancels_bounded_admission_waiter():
    admission = QueryAdmission(1, 1, 1)
    held = await admission.acquire()
    stream = FlowStream()
    response = QueryStreamResponse(stream, admission, StreamPolicy())
    signal = asyncio.Event()
    state = SimpleNamespace(writes=0)

    async def receive():
        await signal.wait()
        return {"type": "http.disconnect"}

    async def send(message):
        state.writes += 1

    task = asyncio.create_task(response({"type": "http"}, receive, send))
    async with asyncio.timeout(1):
        while not admission.waiting:
            await asyncio.sleep(0)
        signal.set()
        await task
    assert admission.waiting == 0 and admission.active == 1 and state.writes == 0
    held.release()


@pytest.mark.asyncio
async def test_disconnect_racing_scope_error_does_not_interrupt_upstream_close():
    stream = FlowStream()
    stream.close_delay = 0.05
    admission = QueryAdmission(1, 0, 0.05)
    response = QueryStreamResponse(stream, admission, StreamPolicy())

    async def send(message):
        if b"event: meta" in message.get("body", b""):
            stream.stale = True

    async def receive():
        await stream.closing.wait()
        return {"type": "http.disconnect"}

    async with asyncio.timeout(1):
        await response({"type": "http"}, receive, send)
    assert stream.closed and admission.active == admission.waiting == 0
