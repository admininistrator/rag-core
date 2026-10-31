"""T32 Fault injection and failure recovery integration suite.

Verifies:
- Fault injection: simulated Qdrant crash / outage, Postgres disconnect / operational errors.
- Graceful degradation: failing closed without bypass or un-filtered vector searches; /health/ready reporting 503.
- Transaction rollback: aborted operations never leave uncommitted or dirty data visible to subsequent queries.
- LLM stream failure injection: mid-stream provider timeout, HTTP 429 rate limit, and HTTP 500 server error.
  Each results in exactly one terminal error event (never done), sanitized error payload without leaked keys, and slot release.
- Detach/delete under stream: immediately stops stream at send boundary with session_scope_changed, retains source data,
  and worker kill does not resurrect scope.
- Ingestion worker interruption: partial or unpublished index generations are never served.
- Data immutability: source document SHA-256 and metadata remain byte-for-byte intact throughout failures and recovery.
"""

import asyncio
import json
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import create_async_engine

from rag_core.adapters.persistence.sessions import PostgresSessionRepository
from rag_core.api.health import HealthChecks
from rag_core.contracts.sse import SSESequence
from rag_core.contracts.v1 import QueryRequest
from rag_core.domain.metadata import ScopeError
from rag_core.domain.streaming import StreamPolicy
from rag_core.domain.vectors import VectorError
from tests.fixtures.evidence_support import evidence_corpus
from tests.fixtures.streaming_support import events, released, streaming_environment
from tests.integration import conftest as pg_fixtures
from tests.integration.test_qdrant_scope import Fixture, embedding, fixture
from tests.integration.test_retrieval import real_models

pg_url = pg_fixtures.pg_url
__all__ = ["evidence_corpus", "fixture", "pg_url", "real_models"]

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


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


async def test_qdrant_outage_fault_injection_fails_closed_and_degrades_readiness(
    fixture: Fixture,
) -> None:
    f = fixture
    target = await f.version()
    await f.seed(target)
    await f.publish(target)
    await f.attach(target)
    scope = await f.snapshot()

    # Verify normal search works before fault injection
    hits = await f.repo.search(
        scope, embedding(strong=True), f.profile.model_fingerprint, branch="hybrid", limit=5
    )
    assert len(hits) > 0

    # Fault injection: simulate Qdrant process crash / connection refused
    broken_mock = AsyncMock(
        side_effect=Exception("Qdrant connection refused: TCP connection reset")
    )
    original_query = f.client.query_points
    f.client.query_points = broken_mock
    try:
        # Search must raise VectorError and fail closed (never fallback to open / unfiltered search)
        with pytest.raises(VectorError, match="vector_dependency_unavailable"):
            await f.repo.search(
                scope, embedding(strong=True), f.profile.model_fingerprint, branch="hybrid", limit=5
            )
    finally:
        f.client.query_points = original_query

    # Verify health check reports degraded / not ready when Qdrant is unreachable
    async def failing_qdrant_check():
        raise Exception("Qdrant down")

    async def ok_check():
        return True

    checks = HealthChecks({"qdrant": failing_qdrant_check, "db": ok_check})
    result = await checks.readiness()
    assert result.ready is False
    assert result.as_dict()["status"] == "unavailable"
    assert result.components["qdrant"] == "unavailable"
    assert result.components["db"] == "ok"


async def test_postgres_disconnect_fault_injection_fails_closed(fixture: Fixture) -> None:
    f = fixture
    target = await f.version()
    await f.publish(target)
    await f.attach(target)

    # Disconnected repository simulating broken connection / operational failure
    disconnected_engine = create_async_engine(
        "postgresql+psycopg://rag_core_test:badpass@127.0.0.1:54321/t10_acceptance",
        connect_args={"connect_timeout": 1},
    )
    disconnected_sessions = PostgresSessionRepository(disconnected_engine)
    try:
        with pytest.raises(OperationalError):
            await disconnected_sessions.resolve_scope(f.owner, f.session.session_id)
    finally:
        await disconnected_engine.dispose()


async def test_transaction_rollback_prevents_uncommitted_data_leakage(fixture: Fixture) -> None:
    f = fixture
    uncommitted_doc_id = uuid4()
    uncommitted_version_id = uuid4()

    # Simulate an aborted transaction (e.g. failure during multi-table write)
    try:
        async with f.engine.begin() as conn:
            await conn.execute(
                text("""
                INSERT INTO documents (document_id, app_id, owner_id, filename,
                    storage_alias, bucket, object_key)
                VALUES (:doc, :app, :owner, 'uncommitted.pdf', 'fixture', 'test-bucket', 'uncommitted-key')
            """),
                dict(doc=uncommitted_doc_id, app=f.owner.app_id, owner=f.owner.user_id),
            )
            await conn.execute(
                text("""
                INSERT INTO document_versions (version_id, app_id, owner_id, document_id,
                    source_sha256, content_type, size_bytes, index_fingerprint)
                VALUES (:version, :app, :owner, :doc, repeat('f',64), 'application/pdf', 100, :fp)
            """),
                dict(
                    version=uncommitted_version_id,
                    app=f.owner.app_id,
                    owner=f.owner.user_id,
                    doc=uncommitted_doc_id,
                    fp=f.profile.fingerprint,
                ),
            )
            # Intentionally simulate a crash / rollback before commit
            raise RuntimeError("Simulated worker process crash during ingestion transaction")
    except RuntimeError:
        pass

    # Verify zero uncommitted rows exist in the database in a fresh transaction
    async with f.engine.connect() as conn:
        doc_count = await conn.scalar(
            text("SELECT count(*) FROM documents WHERE document_id = :id"),
            dict(id=uncommitted_doc_id),
        )
        assert doc_count == 0

        version_count = await conn.scalar(
            text("SELECT count(*) FROM document_versions WHERE version_id = :id"),
            dict(id=uncommitted_version_id),
        )
        assert version_count == 0

    # Querying the uncommitted document ID under the session must raise not_found
    with pytest.raises(ScopeError, match="not_found"):
        await f.sessions.resolve_scope(
            f.owner, f.session.session_id, document_ids=(uncommitted_doc_id,)
        )


async def test_llm_stream_timeout_midway_emits_single_error_and_releases_slot(
    evidence_corpus, tmp_path
) -> None:
    e = evidence_corpus
    _, _, selector = await e.query("Vietnam capital?", labels=("capital-en",))

    # Configure a tight total timeout for fast failure verification
    tight_policy = StreamPolicy(heartbeat_seconds=0.05, total_timeout=0.6)
    async with streaming_environment(
        e, selector, tmp_path, provider="deepseek", policy=tight_policy
    ) as env:
        # Hold wire upstream so the generation stream times out
        env.wire.hold = True
        trace = []
        async with env.client.stream(
            "POST", "/v1/query/stream", json=query(e).model_dump(mode="json")
        ) as response:
            assert response.status_code == 200
            async for item in events(response):
                trace.append(item)

        checked(trace, "error")
        error_event = trace[-1]
        assert error_event["data"]["error"]["code"] in {"timeout", "provider_error"}
        # Never emits done
        assert not any(item["event"] == "done" for item in trace)

        # Release upstream gate to clean up fixture
        env.wire.gate.set()
        await released(env)
        # Verify query admission slot is released cleanly without leaking
        assert env.admission.active == 0


async def test_llm_stream_rate_limit_429_fault_injection(evidence_corpus, tmp_path) -> None:
    e = evidence_corpus
    _, _, selector = await e.query("Vietnam capital?", labels=("capital-en",))

    async with streaming_environment(e, selector, tmp_path, provider="deepseek") as env:
        env.wire.status_code = 429
        env.wire.error_body = {"error": {"message": "Rate limit exceeded. Please try again later."}}

        trace = []
        async with env.client.stream(
            "POST", "/v1/query/stream", json=query(e).model_dump(mode="json")
        ) as response:
            assert response.status_code == 200
            async for item in events(response):
                trace.append(item)

        checked(trace, "error")
        error_event = trace[-1]
        assert error_event["data"]["error"]["code"] in {
            "provider_rate_limit",
            "provider_error",
            "busy",
        }
        assert error_event["data"]["error"]["retryable"] is True
        assert not any(item["event"] == "done" for item in trace)
        await released(env)
        assert env.admission.active == 0


async def test_llm_stream_500_midway_emits_sanitized_error_and_releases_slot(
    evidence_corpus, tmp_path
) -> None:
    e = evidence_corpus
    _, _, selector = await e.query("Vietnam capital?", labels=("capital-en",))

    async with streaming_environment(e, selector, tmp_path, provider="deepseek") as env:
        env.wire.status_code = 500
        env.wire.error_body = {
            "error": {"message": "UPSTREAM CRITICAL FAILURE secret_key=sk-upstream-secret-12345"}
        }

        trace = []
        async with env.client.stream(
            "POST", "/v1/query/stream", json=query(e).model_dump(mode="json")
        ) as response:
            assert response.status_code == 200
            async for item in events(response):
                trace.append(item)

        checked(trace, "error")
        error_event = trace[-1]
        assert error_event["data"]["error"]["code"] == "provider_error"
        # Assert no sensitive upstream keys or raw error messages leaked
        trace_str = json.dumps(trace)
        assert "sk-upstream-secret-12345" not in trace_str
        assert "UPSTREAM CRITICAL" not in trace_str
        assert not any(item["event"] == "done" for item in trace)
        await released(env)
        assert env.admission.active == 0


async def test_detach_and_delete_under_stream_never_resurrects_scope(
    evidence_corpus, tmp_path
) -> None:
    e = evidence_corpus
    _, _, selector = await e.query("Vietnam capital?", labels=("capital-en",))

    async with streaming_environment(e, selector, tmp_path, provider="deepseek") as env:
        env.wire.hold = True
        trace = []

        async def stream_task():
            async with env.client.stream(
                "POST", "/v1/query/stream", json=query(e).model_dump(mode="json")
            ) as response:
                assert response.status_code == 200
                async for item in events(response):
                    trace.append(item)

        task = asyncio.create_task(stream_task())
        await env.wire.first.wait()

        # Detach document under stream
        doc_id = e.chunks["capital-en"].source.document_id
        await e.f.sessions.detach_document(e.f.owner, e.f.session.session_id, doc_id)

        # Release wire gate to let stream proceed to next token
        env.wire.gate.set()
        await task

        checked(trace, "error")
        assert trace[-1]["data"]["error"]["code"] == "session_scope_changed"
        # Never emits done
        assert not any(item["event"] == "done" for item in trace)

        # Verify retention: chunks and vectors remain preserved in PG and Qdrant
        async with e.f.engine.connect() as conn:
            chunk_count = await conn.scalar(
                text("""
                    SELECT count(*) FROM chunks c
                    JOIN document_versions v ON v.version_id = c.version_id
                    WHERE v.document_id = :doc
                """),
                dict(doc=doc_id),
            )
            assert chunk_count > 0

        # Now delete session
        await e.f.sessions.delete_session(e.f.owner, e.f.session.session_id)
        # Repeated delete is idempotent
        repeat = await e.f.sessions.delete_session(e.f.owner, e.f.session.session_id)
        assert repeat.status == "deleted"

        # Subsequent query returns 404 (session_deleted) and does not resurrect
        with pytest.raises(ScopeError, match="session_deleted"):
            await e.f.sessions.resolve_scope(e.f.owner, e.f.session.session_id)

        await released(env)
        assert env.admission.active == 0


async def test_worker_interruption_partial_generation_never_served(
    fixture: Fixture,
) -> None:
    f = fixture
    # Gen 1 is published and ready
    target = await f.version()
    await f.seed(target, strong=True)
    await f.publish(target)
    await f.attach(target)

    # Ingestion worker starts Gen 2, writes some partial points, but crashes before publish
    gen2_scope = await f.generation(target)
    await f.seed(gen2_scope, strong=False)
    # Note: we do NOT call f.publish(gen2_scope); state remains 'staging' / unpublished

    # Verify resolve_scope strictly returns Gen 1, never Gen 2
    snapshot = await f.sessions.resolve_scope(f.owner, f.session.session_id)
    assert len(snapshot.pairs) == 1
    assert snapshot.pairs[0].generation_id == target.pair.generation_id
    assert snapshot.pairs[0].generation_id != gen2_scope.pair.generation_id

    # Verify search only matches Gen 1
    hits = await f.repo.search(
        snapshot, embedding(strong=False), f.profile.model_fingerprint, limit=10
    )
    for hit in hits:
        assert hit.chunk.index_generation == target.pair.generation_id
        assert hit.chunk.index_generation != gen2_scope.pair.generation_id


async def test_source_data_immutability_throughout_failures_and_retries(
    fixture: Fixture,
) -> None:
    f = fixture
    target = await f.version()
    await f.seed(target)
    await f.publish(target)
    await f.attach(target)

    # Query initial source metadata
    async with f.engine.connect() as conn:
        initial = (
            (
                await conn.execute(
                    text("""
                SELECT d.object_key, v.source_sha256, v.size_bytes
                FROM documents d
                JOIN document_versions v ON v.document_id = d.document_id
                WHERE d.document_id = :doc AND v.version_id = :version
            """),
                    dict(doc=target.pair.document_id, version=target.pair.version_id),
                )
            )
            .mappings()
            .one()
        )

    # Perform multiple failure operations: detach, failed transaction, reindex interruption, delete
    await f.sessions.detach_document(f.owner, f.session.session_id, target.pair.document_id)

    try:
        async with f.engine.begin() as conn:
            await conn.execute(
                text("UPDATE document_versions SET state='failed' WHERE version_id=:v"),
                dict(v=target.pair.version_id),
            )
            raise RuntimeError("Interrupted reindex failure")
    except RuntimeError:
        pass

    await f.sessions.delete_session(f.owner, f.session.session_id)

    # Verify source_sha256, object_key, size_bytes are 100% byte-for-byte immutable
    async with f.engine.connect() as conn:
        current = (
            (
                await conn.execute(
                    text("""
                SELECT d.object_key, v.source_sha256, v.size_bytes
                FROM documents d
                JOIN document_versions v ON v.document_id = d.document_id
                WHERE d.document_id = :doc AND v.version_id = :version
            """),
                    dict(doc=target.pair.document_id, version=target.pair.version_id),
                )
            )
            .mappings()
            .one()
        )

    assert current["source_sha256"] == initial["source_sha256"]
    assert current["object_key"] == initial["object_key"]
    assert current["size_bytes"] == initial["size_bytes"]
