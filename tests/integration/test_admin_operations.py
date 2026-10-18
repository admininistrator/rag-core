"""T27 real PostgreSQL actions and actual MinIO/Qdrant retained-source canaries."""

import asyncio
import hashlib
import os
from pathlib import Path
from uuid import UUID, uuid4

import boto3
import httpx
import pytest
from qdrant_client import QdrantClient, models
from sqlalchemy import text

from rag_core.adapters.persistence.ingestion import PostgresIngestionRepository
from rag_core.adapters.persistence.sessions import PostgresSessionRepository
from rag_core.api.health import build_health_checks
from rag_core.auth import Principal
from rag_core.config import Settings
from rag_core.domain.ingestion import IngestionError
from rag_core.domain.metadata import ScopeError
from tests.fixtures.admin_support import AdminFixture
from tests.fixtures.admin_support import admin_fixture as shared_admin_fixture

admin_fixture = shared_admin_fixture

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


async def state(f, table, column, identity, value):
    async with f.engine.connect() as conn:
        return (
            await conn.execute(
                text(f"SELECT {column} FROM {table} WHERE {identity}=:id"), {"id": value}
            )
        ).scalar_one()


async def test_paginated_filtered_escaped_metadata_and_real_counts(
    admin_fixture: AdminFixture, caplog
):
    f = admin_fixture
    await f.login()
    app = "metadata-" + uuid4().hex
    for _ in range(3):
        await f.seed("ready", app=app)
    ids = []
    cursor = None
    for _ in range(3):
        response = await f.client.get(
            "/v1/admin/documents",
            params={
                "app": app,
                "owner": "test-owner",
                "state": "ready",
                "content_type": "text/plain",
                "limit": 1,
                **({"cursor": cursor} if cursor else {}),
            },
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert len(body["items"]) == 1
        row = body["items"][0]
        assert row["filename"] == "&lt;img src=x onerror=alert(1)&gt;.txt"
        assert row["app_id"] == app
        ids.append(row["version_id"])
        cursor = body["next_cursor"]
    assert len(set(ids)) == 3 and cursor is None
    for resource in ["jobs", "sessions", "index", "audit"]:
        response = await f.client.get("/v1/admin/" + resource, params={"limit": 1})
        assert response.status_code == 200
        assert len(response.json()["items"]) <= 1
        for private in [
            "PRIVATE_CHUNK_ANSWER",
            "PRIVATE_SOURCE_KEY",
            "private-storage-alias",
            "private-bucket",
            "PRIVATE_ERROR_WITH_SECRET_AND_ANSWER",
            f.password,
        ]:
            assert private not in response.text + caplog.text
    session = (await f.client.get("/v1/admin/sessions", params={"app": app})).json()["items"][0]
    assert "<script>" not in session["external_session_id"]
    for params in [{"limit": 0}, {"limit": 101}, {"cursor": "bad-PRIVATE_SECRET"}]:
        response = await f.client.get("/v1/admin/documents", params=params)
        assert response.status_code == 422 and "PRIVATE_SECRET" not in response.text
    assert (await f.client.get("/v1/admin/documents", params={"app": "' OR 1=1 --"})).json()[
        "items"
    ] == []
    summary = (await f.client.get("/v1/admin/overview")).json()
    async with f.engine.connect() as conn:
        assert (
            summary["counts"]["documents"]
            == (await conn.execute(text("SELECT count(*) FROM documents"))).scalar_one()
        )
    assert summary["health"]["components"]["postgres"] == "ok"
    assert summary["broker_queue_depth"] is None and summary["vector_bytes"] is None
    assert summary["sizes"]["metadata_database_bytes"] > 0
    assert (await f.client.get("/v1/admin/chunks")).status_code == 404
    # Admin cookies carry no public app/user or factual-retrieval authority.
    assert (await f.client.post("/v1/query", json={})).status_code == 503
    print("T27 metadata: actual counts/keyset pagination/filters/escaping/privacy PASS")


async def test_concurrent_retry_and_illegal_transitions_are_audited(admin_fixture: AdminFixture):
    f = admin_fixture
    headers = await f.login()
    row = await f.seed("failed")
    path = f"/v1/admin/jobs/{row['job']}/retry"
    responses = await asyncio.gather(*(f.client.post(path, headers=headers) for _ in range(2)))
    assert all(r.status_code == 200 for r in responses)
    assert await state(f, "ingestion_jobs", "state", "job_id", row["job"]) == "queued"
    async with f.engine.connect() as conn:
        assert (
            await conn.execute(
                text("SELECT count(*) FROM outbox_events WHERE job_id=:job"), {"job": row["job"]}
            )
        ).scalar_one() == 1
        assert (
            await conn.execute(
                text(
                    "SELECT count(*) FROM audit_events WHERE target_id=:job "
                    "AND action='job_retry' AND outcome='success'"
                ),
                {"job": row["job"]},
            )
        ).scalar_one() == 2
    for job_state, operation in [
        ("ready", "retry"),
        ("ready", "cancel"),
        ("failed", "cancel"),
        ("cancelled", "retry"),
        ("queued", "reindex"),
    ]:
        bad = await f.seed(job_state)
        response = await f.client.post(f"/v1/admin/jobs/{bad['job']}/{operation}", headers=headers)
        assert response.status_code == 409, response.text
        assert await state(f, "ingestion_jobs", "state", "job_id", bad["job"]) == job_state
    exhausted = await f.seed("failed")
    async with f.engine.begin() as conn:
        await conn.execute(
            text("UPDATE ingestion_jobs SET attempts=max_attempts WHERE job_id=:job"),
            {"job": exhausted["job"]},
        )
    assert (
        await f.client.post(f"/v1/admin/jobs/{exhausted['job']}/retry", headers=headers)
    ).status_code == 409
    missing = await f.client.post(f"/v1/admin/jobs/{uuid4()}/cancel", headers=headers)
    assert missing.status_code == 404
    print("T27 jobs: concurrent retry/one outbox/illegal transitions/denied audits PASS")


async def test_cancel_fences_worker_and_reindex_preserves_ready_generation(
    admin_fixture: AdminFixture,
):
    f = admin_fixture
    headers = await f.login()
    ingestion = PostgresIngestionRepository(f.engine)
    row = await f.seed()
    lease = await ingestion.claim(row["job"], "c" * 64, "d" * 64)
    assert lease is not None
    path = f"/v1/admin/jobs/{row['job']}/cancel"
    assert (await f.client.post(path, headers=headers)).status_code == 200
    assert (await f.client.post(path, headers=headers)).status_code == 200
    for operation in [ingestion.heartbeat(lease), ingestion.advance(lease, "parsing", 20)]:
        with pytest.raises(IngestionError, match="ingestion_lease_lost"):
            await operation
    await ingestion.fail(lease, "late_failure", retryable=True)
    assert await ingestion.claim(row["job"], "c" * 64, "d" * 64) is None
    assert (
        await state(
            f, "index_generations", "state", "generation_id", lease.scope.pair.generation_id
        )
        == "failed"
    )
    ready = await f.seed("ready")
    session_repo = PostgresSessionRepository(f.engine)
    principal = Principal(ready["app"], ready["owner"])
    before = await session_repo.resolve_scope(principal, ready["session"])
    path = f"/v1/admin/jobs/{ready['job']}/reindex"
    assert (await f.client.post(path, headers=headers)).status_code == 200
    assert (await f.client.post(path, headers=headers)).status_code == 409
    assert await session_repo.resolve_scope(principal, ready["session"]) == before
    replacement = await ingestion.claim(ready["job"], "e" * 64, "f" * 64)
    assert replacement is not None
    assert (
        await f.client.post(f"/v1/admin/jobs/{ready['job']}/cancel", headers=headers)
    ).status_code == 200
    assert await session_repo.resolve_scope(principal, ready["session"]) == before
    print("T27 cancellation/reindex: actual PG lease fence and old ready generation retained PASS")


async def test_detach_tombstone_revision_no_resurrection_and_link_pagination(
    admin_fixture: AdminFixture,
):
    f = admin_fixture
    headers = await f.login()
    row = await f.seed("ready")
    sessions = PostgresSessionRepository(f.engine)
    principal = Principal(row["app"], row["owner"])
    snapshot = await sessions.resolve_scope(principal, row["session"])
    links = await f.client.get(
        f"/v1/admin/sessions/{row['session']}/documents", params={"limit": 1}
    )
    assert len(links.json()["items"]) == 1
    assert links.json()["next_cursor"] is None
    detach = f"/v1/admin/sessions/{row['session']}/documents/{row['doc']}"
    assert (await f.client.delete(detach, headers=headers)).status_code == 200
    assert (await f.client.delete(detach, headers=headers)).status_code == 200
    with pytest.raises(ScopeError, match="session_scope_changed"):
        await sessions.validate_snapshot(snapshot)
    assert (
        await state(f, "sessions", "scope_revision", "session_id", row["session"])
        == snapshot.scope_revision + 1
    )
    assert (
        await f.client.post(f"/v1/admin/jobs/{row['job']}/reindex", headers=headers)
    ).status_code == 409
    tombstone = f"/v1/admin/sessions/{row['session']}"
    assert (await f.client.delete(tombstone, headers=headers)).status_code == 200
    assert (await f.client.delete(tombstone, headers=headers)).status_code == 200
    assert (
        await state(f, "sessions", "scope_revision", "session_id", row["session"])
        == snapshot.scope_revision + 2
    )
    assert (await f.client.delete(detach, headers=headers)).status_code == 410
    assert await state(f, "document_versions", "state", "version_id", row["version"]) == "ready"
    async with f.engine.connect() as conn:
        audit_rows = (
            await conn.execute(
                text(
                    "SELECT action,target_id,request_id FROM audit_events WHERE target_id=:target"
                ),
                {"target": row["session"]},
            )
        ).all()
        assert len(audit_rows) >= 4
        assert all(isinstance(r.request_id, UUID) for r in audit_rows)
    print("T27 session detach/tombstone: revision/idempotence/scope invalidation/retention PASS")


async def test_audit_failure_rolls_back_action_and_sanitizes_errors(
    admin_fixture: AdminFixture, caplog
):
    f = admin_fixture
    headers = await f.login()
    row = await f.seed()
    async with f.engine.begin() as conn:
        await conn.execute(
            text("""CREATE FUNCTION reject_admin_audit() RETURNS trigger LANGUAGE plpgsql AS $$
            BEGIN IF NEW.action='job_cancel' THEN RAISE EXCEPTION 'PRIVATE_DATABASE_SECRET';
            END IF; RETURN NEW; END $$""")
        )
        await conn.execute(
            text(
                "CREATE TRIGGER reject_admin_audit BEFORE INSERT ON audit_events "
                "FOR EACH ROW EXECUTE FUNCTION reject_admin_audit()"
            )
        )
    try:
        response = await f.client.post(f"/v1/admin/jobs/{row['job']}/cancel", headers=headers)
        assert response.status_code == 503
        assert await state(f, "ingestion_jobs", "state", "job_id", row["job"]) == "queued"
        assert "PRIVATE_DATABASE_SECRET" not in response.text + caplog.text
    finally:
        async with f.engine.begin() as conn:
            await conn.execute(text("DROP TRIGGER reject_admin_audit ON audit_events"))
            await conn.execute(text("DROP FUNCTION reject_admin_audit()"))
    print("T27 atomicity: actual PG audit INSERT failure rolls back action, error/log private PASS")


async def test_real_source_vector_and_chunk_retention(admin_fixture: AdminFixture):
    f = admin_fixture
    headers = await f.login()
    endpoint = os.environ.get("RAG_ADMIN_TEST_STORAGE_URL")
    vector_url = os.environ.get("RAG_ADMIN_TEST_QDRANT_URL")
    assert endpoint == "http://127.0.0.1:19007" and vector_url == "http://127.0.0.1:56337", (
        "Explicit isolated T27 MinIO/Qdrant URLs required; no mocks or application endpoints"
    )
    secrets_dir = Path(".local/secrets")
    f.app.state.admin_health_checks = build_health_checks(
        Settings(
            _env_file=None,
            database_url=f.url.set(drivername="postgresql").render_as_string(hide_password=False),
            redis_url="redis://127.0.0.1:16387/0",
            qdrant_url=vector_url,
        )
    )
    report = (await f.client.get("/v1/admin/overview")).json()["health"]
    assert report == {
        "status": "ready",
        "components": {"postgres": "ok", "redis": "ok", "qdrant": "ok"},
    }
    uploader = boto3.client(
        "s3",
        endpoint_url=endpoint,
        region_name="us-east-1",
        aws_access_key_id=(secrets_dir / "minio_uploader_user").read_text().strip(),
        aws_secret_access_key=(secrets_dir / "minio_uploader_password").read_text().strip(),
    )
    vectors = QdrantClient(url=vector_url, timeout=5, trust_env=False)
    collection = "t27_" + uuid4().hex
    key = "allowed/t27-" + uuid4().hex + ".txt"
    payload = b"T27 synthetic app-owned immutable source."
    source = await asyncio.to_thread(
        uploader.put_object, Bucket="rag-core-storage-test", Key=key, Body=payload
    )
    before = await asyncio.to_thread(uploader.head_object, Bucket="rag-core-storage-test", Key=key)
    await asyncio.to_thread(
        vectors.create_collection,
        collection,
        vectors_config=models.VectorParams(size=2, distance=models.Distance.COSINE),
    )
    point_id = str(uuid4())
    await asyncio.to_thread(
        vectors.upsert,
        collection,
        points=[
            models.PointStruct(id=point_id, vector=[1.0, 0.0], payload={"fixture": "retained"})
        ],
        wait=True,
    )
    row = await f.seed("ready")
    async with f.engine.begin() as conn:
        await conn.execute(
            text("UPDATE documents SET object_key=:key WHERE document_id=:doc"),
            {"key": key, "doc": row["doc"]},
        )
    try:
        # Replacement staging is cancelled; old source/chunks/vector must remain.
        assert (
            await f.client.post(f"/v1/admin/jobs/{row['job']}/reindex", headers=headers)
        ).status_code == 200
        assert (
            await f.client.post(f"/v1/admin/jobs/{row['job']}/cancel", headers=headers)
        ).status_code == 200
        assert (
            await f.client.delete(
                f"/v1/admin/sessions/{row['session']}/documents/{row['doc']}", headers=headers
            )
        ).status_code == 200
        assert (
            await f.client.delete(f"/v1/admin/sessions/{row['session']}", headers=headers)
        ).status_code == 200
        after = await asyncio.to_thread(
            uploader.head_object, Bucket="rag-core-storage-test", Key=key
        )
        assert (after["VersionId"], after["ETag"], after["ContentLength"]) == (
            source["VersionId"],
            before["ETag"],
            len(payload),
        )
        downloaded = await asyncio.to_thread(
            uploader.get_object, Bucket="rag-core-storage-test", Key=key
        )
        with downloaded["Body"] as body:
            assert hashlib.sha256(body.read()).digest() == hashlib.sha256(payload).digest()
        points = await asyncio.to_thread(
            vectors.retrieve, collection, ids=[point_id], with_vectors=True
        )
        assert len(points) == 1 and points[0].vector == [1.0, 0.0]
        assert (
            await state(f, "chunks", "text", "version_id", row["version"]) == "PRIVATE_CHUNK_ANSWER"
        )
        async with httpx.AsyncClient(trust_env=False) as client:
            assert (await client.get(vector_url + "/readyz")).status_code == 200
        print(
            "T27 actual MinIO HEAD/GET version/ETag/SHA + Qdrant point/vector + PG chunk retained PASS"
        )
    finally:
        # Retain source fixture until isolated tmpfs stack stop. Never source-delete via admin.
        await asyncio.to_thread(vectors.delete_collection, collection)
        vectors.close()
