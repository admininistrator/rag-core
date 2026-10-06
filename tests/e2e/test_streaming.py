"""T25 real HTTP/JWT/PG/Qdrant/CPU; native provider fixture HTTP is synthetic, NOT live LLM."""

import asyncio
import json
import re
from pathlib import Path

import pytest
from sqlalchemy import text

from rag_core.contracts.sse import SSESequence
from rag_core.contracts.v1 import QueryRequest, QueryResponse
from rag_core.domain.answers import AnswerPolicy
from rag_core.domain.streaming import StreamPolicy
from tests.fixtures.answer_support import good_answer
from tests.fixtures.evidence_support import evidence_corpus
from tests.fixtures.streaming_support import events, released, streaming_environment
from tests.integration.test_qdrant_scope import fixture
from tests.integration.test_retrieval import real_models

__all__ = ["evidence_corpus", "fixture", "real_models"]
pytestmark = [pytest.mark.e2e, pytest.mark.asyncio]


def query(e, labels=("capital-en",)):
    return QueryRequest(
        session_id=e.f.session.session_id,
        domain="document",
        document_ids=[e.targets[k].pair.document_id for k in labels],
        question="Thủ đô của Việt Nam?",
        answer_language="vi",
    )


def checked(trace, terminal):
    assert SSESequence.model_validate(trace).root[-1].event == terminal, [
        item["data"]["error"]["code"] for item in trace if item["event"] == "error"
    ]
    assert sum(item["event"] in {"done", "error"} for item in trace) == 1
    assert [item["id"] for item in trace] == list(range(1, len(trace) + 1))


@pytest.mark.parametrize("provider", ["deepseek", "anthropic"])
async def test_event_order_real_http_utf8_split_frames_and_done(
    evidence_corpus, tmp_path, provider
):
    e = evidence_corpus
    _, _, selector = await e.query("Vietnam capital?", labels=("capital-en",))
    async with streaming_environment(e, selector, tmp_path, provider=provider) as env:
        async with env.client.stream(
            "POST", "/v1/query/stream", json=query(e).model_dump(mode="json")
        ) as response:
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("text/event-stream")
            assert response.headers["cache-control"] == "no-store"
            trace = [item async for item in events(response)]
        checked(trace, "done")
        assert [item["event"] for item in trace[:2]] == ["meta", "evidence"]
        final = QueryResponse.model_validate(trace[-1]["data"])
        assert (
            "".join(item["data"]["text"] for item in trace if item["event"] == "answer_delta")
            == final.answer
        )
        assert "Hà Nội" in final.answer and final.usage.input_tokens == 11
        assert all(len(fragment) == 1 for fragment in env.wire.raw_fragments)
        assert b"\xc3\xa0" in b"".join(env.wire.raw_fragments)
        assert len(env.wire.generation) == 1
        await released(env)
        print(
            f"T25 REAL HTTP/JWT/PG/Qdrant/CPU {provider} synthetic native wire: meta/evidence/delta/done UTF-8 PASS"
        )


@pytest.mark.parametrize("provider", ["deepseek", "anthropic"])
async def test_heartbeat_partial_provider_failure_exactly_one_error(
    evidence_corpus, tmp_path, provider
):
    e = evidence_corpus
    _, _, selector = await e.query("Vietnam capital?", labels=("capital-en",))
    async with streaming_environment(e, selector, tmp_path, provider=provider) as env:
        env.wire.hold = env.wire.failure = True
        comments = []
        trace = []
        async with env.client.stream(
            "POST", "/v1/query/stream", json=query(e).model_dump(mode="json")
        ) as response:
            parsed = events(response, comments=comments)
            async for item in parsed:
                trace.append(item)
                if item["event"] == "answer_delta":
                    await asyncio.sleep(0.13)
                    env.wire.gate.set()
        checked(trace, "error")
        assert comments and any(item["event"] == "answer_delta" for item in trace)
        assert trace[-1]["data"]["error"]["code"] == "provider_error"
        assert "PRIVATE UPSTREAM ERROR" not in json.dumps(trace)
        assert len(env.wire.generation) == 1
        await released(env)
        print(
            f"T25 REAL HTTP {provider}: provisional answer + heartbeat + one technical error/no replay PASS"
        )


@pytest.mark.parametrize("phase", ["retrieval", "provider", "delta"])
async def test_client_disconnect_releases_upstream_and_slot(evidence_corpus, tmp_path, phase):
    e = evidence_corpus
    _, _, selector = await e.query("Vietnam capital?", labels=("capital-en",))
    policy = StreamPolicy(concurrency=1, queue_size=0, heartbeat_seconds=0.05)
    async with streaming_environment(e, selector, tmp_path, policy=policy) as env:
        env.wire.hold = True
        env.wire.delay = 0.2 if phase == "provider" else 0.0
        async with env.client.stream(
            "POST", "/v1/query/stream", json=query(e).model_dump(mode="json")
        ) as response:
            async for item in events(response):
                if (
                    item["event"]
                    == {"retrieval": "meta", "provider": "evidence", "delta": "answer_delta"}[phase]
                ):
                    break
        await released(env)
        assert env.admission.active == env.admission.waiting == env.wire.active == 0
        env.wire.hold = False
        env.wire.delay = 0
        async with env.client.stream(
            "POST", "/v1/query/stream", json=query(e).model_dump(mode="json")
        ) as next_response:
            trace = [item async for item in events(next_response)]
        checked(trace, "done")
        print(
            f"T25 REAL HTTP disconnect at {phase}; native upstream/slot closed; next request admitted PASS"
        )


async def test_busy_response_does_not_allocate_query_or_leak_slots(evidence_corpus, tmp_path):
    e = evidence_corpus
    _, _, selector = await e.query("Vietnam capital?", labels=("capital-en",))
    policy = StreamPolicy(concurrency=1, queue_size=0, heartbeat_seconds=0.05)
    async with streaming_environment(e, selector, tmp_path, policy=policy) as env:
        env.wire.hold = True
        body = query(e).model_dump(mode="json")
        async with env.client.stream("POST", "/v1/query/stream", json=body) as response:
            async for item in events(response):
                if item["event"] == "answer_delta":
                    break
            busy = await env.client.post("/v1/query/stream", json=body)
            assert busy.status_code == 429 and busy.headers["retry-after"] == "1"
            assert busy.json()["error"]["code"] == "busy"
            assert len(env.wire.generation) == 1
        await released(env)


@pytest.mark.parametrize(
    "action,phase",
    [
        ("detach", "evidence"),
        ("detach", "answer_delta"),
        ("delete", "answer_delta"),
        ("delete", "evidence"),
    ],
)
async def test_scope_change_detach_delete_between_events_no_done(
    evidence_corpus, tmp_path, action, phase
):
    e = evidence_corpus
    _, _, selector = await e.query("Vietnam capital?", labels=("capital-en",))
    async with streaming_environment(e, selector, tmp_path) as env:
        env.wire.hold = True
        env.wire.delay = 0.2 if phase == "evidence" else 0
        trace = []
        async with env.client.stream(
            "POST", "/v1/query/stream", json=query(e).model_dump(mode="json")
        ) as response:
            async for item in events(response):
                trace.append(item)
                if item["event"] == phase:
                    if action == "detach":
                        await e.f.sessions.detach_document(
                            e.f.owner,
                            e.f.session.session_id,
                            e.targets["capital-en"].pair.document_id,
                        )
                    else:
                        await e.f.sessions.delete_session(e.f.owner, e.f.session.session_id)
                    # Keep provider idle. Heartbeat validation must catch invalidation.
        checked(trace, "error")
        assert trace[-1]["data"]["error"]["code"] == "session_scope_changed"
        assert trace[-2]["event"] == phase
        await released(env)
        async with e.f.engine.connect() as conn:
            retained = await conn.scalar(
                text("SELECT count(*) FROM chunks WHERE chunk_id=:id"),
                {"id": e.chunks["capital-en"].id},
            )
        assert retained == 1
        print(
            f"T25 REAL HTTP/PG {action} after {phase}: scope_changed/no done; upstream/slot closed; retained chunk PASS"
        )


@pytest.mark.parametrize("provider", ["deepseek", "anthropic"])
async def test_allowlist_subset_and_json_sse_final_equivalence(evidence_corpus, tmp_path, provider):
    e = evidence_corpus
    _, _, selector = await e.query("Vietnam capital?", labels=("capital-en", "capital-vi"))
    async with streaming_environment(e, selector, tmp_path, provider=provider) as env:
        body = query(e, ("capital-en", "capital-vi"))
        async with env.client.stream(
            "POST", "/v1/query/stream", json=body.model_dump(mode="json")
        ) as response:
            trace = [item async for item in events(response)]
        checked(trace, "done")
        final = QueryResponse.model_validate(trace[-1]["data"])
        assert len(trace[1]["data"]["citations"]) >= 2
        assert len(final.citations) == len(final.contexts) == 1
        json_final = await env.pipeline.answer(e.f.owner, body, final.request_id)
        assert final.model_dump(exclude={"timings_ms"}) == json_final.model_dump(
            exclude={"timings_ms"}
        )
        print(
            f"T25 {provider} REAL stack: early allowlist >=2/final referenced subset1; JSON/SSE final schema+fields equal PASS"
        )


@pytest.mark.parametrize("fault", ["invalid-id", "wrong-quote", "malformed-final"])
async def test_bad_output_after_delta_no_repair_or_success(evidence_corpus, tmp_path, fault):
    e = evidence_corpus
    _, _, selector = await e.query("Vietnam capital?", labels=("capital-en",))
    async with streaming_environment(e, selector, tmp_path) as env:

        def invalid(data):
            result = good_answer(data)
            result["answer"] = "Đây là bản tạm. " + result["answer"]
            if fault == "invalid-id":
                result["answer"] += " Invalid [c999]. "
            elif fault == "wrong-quote":
                result["citations"][0]["quote"] = "forged"
            else:
                return json.dumps(result, ensure_ascii=False)[:-1]
            return result

        env.wire.responses = [invalid]
        async with env.client.stream(
            "POST", "/v1/query/stream", json=query(e).model_dump(mode="json")
        ) as response:
            trace = [item async for item in events(response)]
        checked(trace, "error")
        assert trace[-1]["data"]["error"]["code"] == "invalid_citation"
        assert any(item["event"] == "answer_delta" for item in trace)
        assert "c999" not in json.dumps(trace)
        assert len(env.wire.generation) == 1
        await released(env)


async def test_total_timeout_during_idle_stream_cancels_upstream(evidence_corpus, tmp_path):
    e = evidence_corpus
    _, _, selector = await e.query("Vietnam capital?", labels=("capital-en",))
    policy = StreamPolicy(total_timeout=2.0, heartbeat_seconds=0.05)
    async with streaming_environment(e, selector, tmp_path, policy=policy) as env:
        env.wire.hold = True
        async with env.client.stream(
            "POST", "/v1/query/stream", json=query(e).model_dump(mode="json")
        ) as response:
            trace = [item async for item in events(response)]
        checked(trace, "error")
        assert trace[-1]["data"]["error"]["code"] == "timeout"
        await released(env)


async def test_insufficient_empty_evidence_usage_null_and_history_warning(
    evidence_corpus, tmp_path
):
    e = evidence_corpus
    _, _, selector = await e.query("Vietnam capital?", labels=("fish",))
    async with streaming_environment(e, selector, tmp_path) as env:
        env.wire.usage = False
        body = QueryRequest.model_validate(
            {
                **query(e, ("fish",)).model_dump(),
                "history": [{"role": "assistant", "content": "OLD OUTSIDE SESSION [c999]"}] * 21,
            }
        )
        async with env.client.stream(
            "POST", "/v1/query/stream", json=body.model_dump(mode="json")
        ) as response:
            trace = [item async for item in events(response)]
        checked(trace, "done")
        final = QueryResponse.model_validate(trace[-1]["data"])
        assert final.answerability == "insufficient_evidence"
        assert final.citations == final.contexts == []
        assert final.usage.input_tokens is final.usage.output_tokens is None
        assert (
            trace[0]["data"]["history"]["truncated"]
            and final.warnings[0].code == "history_truncated"
        )
        assert len(env.wire.generation) == 1 and "OLD OUTSIDE SESSION" not in str(
            env.wire.generation
        )


async def test_auth_input_and_scope_failure_pre_stream_http_errors(evidence_corpus, tmp_path):
    e = evidence_corpus
    _, _, selector = await e.query("Vietnam capital?", labels=("capital-en",))
    async with streaming_environment(e, selector, tmp_path) as env:
        body = query(e).model_dump(mode="json")
        missing = await env.client.post(
            "/v1/query/stream", json=body, headers={"Authorization": "Bearer invalid"}
        )
        assert missing.status_code == 401
        forged = await env.client.post("/v1/query/stream", json={**body, "user_id": "forged"})
        assert forged.status_code == 422
        empty = await e.f.sessions.create_session(e.f.owner, "empty-t25")
        unavailable = await env.client.post(
            "/v1/query/stream", json={**body, "session_id": str(empty.session_id)}
        )
        assert unavailable.status_code == 404
        assert unavailable.json()["error"]["code"] == "not_found"
        assert env.wire.generation == [] and env.admission.active == 0


async def test_bounded_repair_before_delta_still_validates_final(evidence_corpus, tmp_path):
    e = evidence_corpus
    _, _, selector = await e.query("Vietnam capital?", labels=("capital-en",))
    async with streaming_environment(
        e, selector, tmp_path, answer_policy=AnswerPolicy(timeout_seconds=10.0)
    ) as env:
        env.wire.responses = ["invalid JSON", good_answer]
        async with env.client.stream(
            "POST", "/v1/query/stream", json=query(e).model_dump(mode="json")
        ) as response:
            trace = [item async for item in events(response)]
        checked(trace, "done")
        assert len(env.wire.generation) == 2 and "repair" in env.wire.generation[1]
        assert QueryResponse.model_validate(trace[-1]["data"]).usage.input_tokens == 22


@pytest.mark.parametrize("failure", [False, True])
async def test_runbook_httpx_parser_over_real_http(evidence_corpus, tmp_path, failure):
    e = evidence_corpus
    _, _, selector = await e.query("Vietnam capital?", labels=("capital-en",))
    runbook = Path("RUNBOOK.md").read_text(encoding="utf-8")
    code = re.search(r"<!-- T25-client: python -->\s*```python\n(.*?)\n```", runbook, re.S)[1]
    namespace = {}
    exec(compile(code, "RUNBOOK.md:T25-client", "exec"), namespace)
    async with streaming_environment(e, selector, tmp_path) as env:
        env.wire.failure = failure
        if failure:
            with pytest.raises(RuntimeError, match="provider_error"):
                await namespace["read_answer"](env.client, query(e).model_dump(mode="json"))
        else:
            final = await namespace["read_answer"](env.client, query(e).model_dump(mode="json"))
            assert isinstance(final, QueryResponse) and "Hà Nội" in final.answer
        await released(env)
        print(f"T25 RUNBOOK exact HTTPX parser executed on real HTTP; failure={failure} PASS")
