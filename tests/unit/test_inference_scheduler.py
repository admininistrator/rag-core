"""Deterministic scheduler faults; real weight/transport acceptance is separate."""

import asyncio
import threading
from uuid import uuid4

import pytest
from pydantic import ValidationError

from rag_core.domain.models import InferenceError, InferenceRequest, InferenceResult
from rag_core.inference.scheduler import InferenceScheduler

pytestmark = pytest.mark.unit


class BlockingBackend:
    fingerprint = "scheduler-test-only"

    def __init__(self):
        self.started = threading.Event()
        self.release = threading.Event()
        self.calls = []
        self.threads = set()

    def infer(self, request):
        self.threads.add(threading.get_ident())
        self.calls.append(request.texts)
        self.started.set()
        assert self.release.wait(5)
        if request.texts[0] == "fail":
            raise RuntimeError("PRIVATE upstream text")
        return InferenceResult(fingerprint=self.fingerprint, scores=tuple(1.0 for _ in request.texts))


def request(text="index", *, priority="index", count=1, timeout=2):
    return InferenceRequest(operation="rerank", query="query", priority=priority,
                            texts=[text]*count, timeout_seconds=float(timeout))


async def admitted(scheduler, request_id):
    for _ in range(1000):
        if request_id in scheduler.jobs:
            return
        await asyncio.sleep(0.001)
    raise AssertionError("request not admitted")


def test_query_preempts_index_between_batches_and_single_executor():
    async def run():
        backend = BlockingBackend()
        scheduler = InferenceScheduler(backend, capacity=4, index_capacity=3)
        index_id, query_id = uuid4(), uuid4()
        index = asyncio.create_task(scheduler.infer(index_id, request(count=4)))
        await admitted(scheduler, index_id)
        while not backend.started.is_set():
            await asyncio.sleep(0.001)
        query = asyncio.create_task(scheduler.infer(query_id, request("query", priority="query")))
        await admitted(scheduler, query_id)
        backend.release.set()
        try:
            assert len((await index).scores) == 4
            assert len((await query).scores) == 1
            assert backend.calls == [["index", "index"], ["query"], ["index", "index"]]
            assert len(backend.threads) == 1
        finally:
            await scheduler.close()
    asyncio.run(run())


def test_reserved_query_capacity_bounded_admission_and_queued_cancel():
    async def run():
        backend = BlockingBackend()
        scheduler = InferenceScheduler(backend, capacity=3, index_capacity=2)
        first_id, queued_id, query_id = uuid4(), uuid4(), uuid4()
        first = asyncio.create_task(scheduler.infer(first_id, request()))
        await admitted(scheduler, first_id)
        while not backend.started.is_set():
            await asyncio.sleep(0.001)
        queued = asyncio.create_task(scheduler.infer(queued_id, request("queued")))
        await admitted(scheduler, queued_id)
        with pytest.raises(InferenceError, match="model_busy"):
            await scheduler.infer(uuid4(), request())
        query = asyncio.create_task(scheduler.infer(query_id, request("query", priority="query")))
        await admitted(scheduler, query_id)
        with pytest.raises(InferenceError, match="model_busy"):
            await scheduler.infer(uuid4(), request("query", priority="query"))
        scheduler.cancel(queued_id)
        with pytest.raises(InferenceError, match="model_cancelled"):
            await queued
        assert len(scheduler.jobs) == 2
        backend.release.set()
        try:
            await asyncio.gather(first, query)
            assert backend.calls == [["index"], ["query"]]
        finally:
            await scheduler.close()
    asyncio.run(run())


def test_running_timeout_holds_slot_failure_is_sanitized_and_recovers():
    async def run():
        backend = BlockingBackend()
        scheduler = InferenceScheduler(backend, capacity=2, index_capacity=1)
        timed_id = uuid4()
        timed = asyncio.create_task(scheduler.infer(timed_id, request(timeout=0.05)))
        await admitted(scheduler, timed_id)
        with pytest.raises(InferenceError, match="model_timeout"):
            await timed
        assert timed_id in scheduler.jobs  # native work still owns slot
        with pytest.raises(InferenceError, match="model_busy"):
            await scheduler.infer(uuid4(), request())
        backend.release.set()
        while scheduler.jobs:
            await asyncio.sleep(0.001)
        try:
            with pytest.raises(InferenceError) as failure:
                await scheduler.infer(uuid4(), request("fail"))
            assert str(failure.value) == "model_failed"
            assert len((await scheduler.infer(uuid4(), request("recover"))).scores) == 1
        finally:
            await scheduler.close()
    asyncio.run(run())


def test_duplicate_id_and_shutdown_reject_new_work():
    async def run():
        backend = BlockingBackend()
        scheduler = InferenceScheduler(backend)
        request_id = uuid4()
        task = asyncio.create_task(scheduler.infer(request_id, request()))
        await admitted(scheduler, request_id)
        with pytest.raises(InferenceError, match="duplicate_inference_id"):
            await scheduler.infer(request_id, request())
        backend.release.set()
        await task
        await scheduler.close()
        with pytest.raises(InferenceError, match="model_unavailable"):
            await scheduler.infer(uuid4(), request())
    asyncio.run(run())


@pytest.mark.parametrize("payload", [
    {"operation":"embed", "texts":[]},
    {"operation":"embed", "texts":["x"]*33},
    {"operation":"embed", "texts":[" "]},
    {"operation":"embed", "texts":["x"*32769]},
    {"operation":"embed", "texts":["x"], "query":"q"},
    {"operation":"rerank", "texts":["x"]},
    {"operation":"rerank", "texts":["x"]*21, "query":"q"},
    {"operation":"embed", "texts":["x"], "timeout_seconds":121.0},
    {"operation":"embed", "texts":["x"], "user_id":"owner"},
])
def test_request_bounds_before_admission(payload):
    with pytest.raises(ValidationError):
        InferenceRequest.model_validate(payload)
