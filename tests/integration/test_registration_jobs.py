"""T12 acceptance with real PostgreSQL, Redis broker and versioned MinIO."""

import asyncio
import hashlib
import os
import subprocess
import sys
from collections.abc import AsyncIterator
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID, uuid4

import boto3
import pytest
import pytest_asyncio
import redis
from kombu.exceptions import OperationalError
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine

from rag_core.adapters.broker.celery import CeleryJobPublisher
from rag_core.adapters.persistence.database import build_engine
from rag_core.adapters.persistence.registrations import (
    OutboxDispatcher,
    PostgresRegistrationRepository,
)
from rag_core.adapters.storage.s3 import S3StorageReader, StorageLocation, StorageRegistry
from rag_core.auth import Principal
from rag_core.contracts.v1 import DocumentRegisterRequest
from rag_core.domain.metadata import ScopeError
from rag_core.ports.storage import StorageError

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]
BUCKET = "rag-core-storage-test"
BROKER = "redis://127.0.0.1:16379/15"
SECRETS = Path(".local/secrets")


def secret(name: str) -> str:
    path = SECRETS / name
    if not path.is_file():
        pytest.fail(f"Missing ignored {path}; run scripts/bootstrap_storage_test.ps1")
    return path.read_text(encoding="ascii").strip()


@dataclass
class Fixture:
    engine: AsyncEngine
    repo: PostgresRegistrationRepository
    principal: Principal
    session_id: UUID
    body: DocumentRegisterRequest
    broker: redis.Redis
    baseline_queue: int
    uploader: object
    key: str

    async def counts(self) -> tuple[int, int, int, int]:
        async with self.engine.connect() as conn:
            counts = []
            for table in ("upload_registrations", "session_documents",
                          "ingestion_jobs", "outbox_events"):
                count = (await conn.execute(
                    text(f"SELECT count(*) FROM {table} WHERE app_id=:app"),
                    {"app": self.principal.app_id},
                )).scalar_one()
                counts.append(int(count))
            return tuple(counts)  # type: ignore[return-value]


@pytest_asyncio.fixture
async def fixture(pg_url: URL, tmp_path: Path) -> AsyncIterator[Fixture]:
    broker = redis.Redis.from_url(BROKER, socket_connect_timeout=2, socket_timeout=2)
    assert broker.ping()  # Real broker; never skip or replace with a fake.
    baseline_queue = broker.llen("rag_core_ingestion")
    principal = Principal("t12-" + uuid4().hex, "owner")
    engine = build_engine(pg_url)
    reader = S3StorageReader(StorageRegistry(locations=(StorageLocation(
        app_id=principal.app_id, alias="test-store", endpoint="http://127.0.0.1:9000",
        region="us-east-1", bucket=BUCKET, prefix="allowed/",
        access_key_file=SECRETS / "minio_reader_user",
        secret_key_file=SECRETS / "minio_reader_password",
        allow_loopback_http=True, max_bytes=1024,
    ),)), temp_dir=tmp_path)
    uploader = boto3.client(
        "s3", endpoint_url="http://127.0.0.1:9000", region_name="us-east-1",
        aws_access_key_id=secret("minio_uploader_user"),
        aws_secret_access_key=secret("minio_uploader_password"),
    )
    key = "allowed/t12-" + uuid4().hex + ".txt"
    payload = b"T12 verified immutable source\n"
    version = uploader.put_object(Bucket=BUCKET, Key=key, Body=payload)["VersionId"]
    body = DocumentRegisterRequest.model_validate({
        "external_upload_id": "app-upload-1",
        "source": {"storage_alias": "test-store", "bucket": BUCKET, "key": key,
                   "version_id": version, "sha256": hashlib.sha256(payload).hexdigest()},
        "filename": "source.txt", "content_type": "text/plain",
    })
    repo = PostgresRegistrationRepository(engine, reader)
    session = await repo.sessions.create_session(principal, "chat-1")
    try:
        yield Fixture(engine, repo, principal, session.session_id, body, broker,
                      baseline_queue, uploader, key)
    finally:
        async with engine.begin() as conn:
            for table in ("outbox_events", "session_documents", "upload_registrations",
                          "ingestion_jobs", "document_versions", "documents", "sessions"):
                await conn.execute(text(f"DELETE FROM {table} WHERE app_id=:app"),
                                   {"app": principal.app_id})
        versions = uploader.list_object_versions(Bucket=BUCKET, Prefix=key)
        for entry in (*versions.get("Versions", []), *versions.get("DeleteMarkers", [])):
            if entry["Key"] == key:
                uploader.delete_object(Bucket=BUCKET, Key=key, VersionId=entry["VersionId"])
        await engine.dispose()
        broker.close()


async def test_idempotency_concurrency_owner_and_broker_recovery(
    fixture: Fixture, pg_url: URL,
) -> None:
    f = fixture
    first = await f.repo.register(f.principal, f.session_id, "same-key", f.body)
    assert first.job.state == "queued" and first.session.scope_revision == 1
    assert await f.repo.register(f.principal, f.session_id, "same-key", f.body) == first
    different = f.body.model_copy(update={"filename": "changed.txt"})
    with pytest.raises(ScopeError, match="idempotency_conflict"):
        await f.repo.register(f.principal, f.session_id, "same-key", different)
    with pytest.raises(ScopeError, match="idempotency_conflict"):
        await f.repo.register(f.principal, f.session_id, "different-key", f.body)
    attempts = await asyncio.gather(*(
        f.repo.register(f.principal, f.session_id, "same-key", f.body) for _ in range(6)
    ))
    assert all(item == first for item in attempts)
    assert await f.counts() == (1, 1, 1, 1)
    assert (await f.repo.list_documents(f.principal, f.session_id))[1][0].document_id == first.document_id
    assert (await f.repo.get_job(f.principal, first.job.job_id)).state == "queued"
    for stranger in (Principal(f.principal.app_id, "other"), Principal("other", "owner")):
        for operation in (
            f.repo.register(stranger, f.session_id, "same-key", f.body),
            f.repo.list_documents(stranger, f.session_id),
            f.repo.get_job(stranger, first.job.job_id),
            f.repo.retry_job(stranger, first.job.job_id),
        ):
            with pytest.raises(ScopeError, match="not_found"):
                await operation
    assert (await f.repo.retry_job(f.principal, first.job.job_id)).state == "queued"
    assert await f.counts() == (1, 1, 1, 1)

    unavailable = OutboxDispatcher(f.engine, CeleryJobPublisher("redis://127.0.0.1:16378/15"))
    with pytest.raises(OperationalError):
        await unavailable.dispatch_one()
    assert await f.counts() == (1, 1, 1, 1)
    async with f.engine.connect() as conn:
        assert (await conn.execute(text("SELECT dispatched_at FROM outbox_events WHERE app_id=:app"),
                                   {"app": f.principal.app_id})).scalar_one() is None
    recovered = OutboxDispatcher(f.engine, CeleryJobPublisher(BROKER))
    assert await recovered.dispatch_one()
    assert not await recovered.dispatch_one()
    assert f.broker.llen("rag_core_ingestion") == f.baseline_queue + 1
    env = os.environ.copy()
    env["DATABASE_URL"] = pg_url.render_as_string(hide_password=False)
    env.pop("DATABASE_PASSWORD_FILE", None)
    env["REDIS_URL"] = BROKER
    command = subprocess.run(
        [sys.executable, "-m", "rag_core.adapters.broker.dispatcher", "--once"],
        env=env, capture_output=True, text=True, timeout=15, check=False,
    )
    assert command.returncode == 0 and command.stdout == "" and command.stderr == ""
    print("PASS real PG/MinIO/Redis: idempotency, concurrent duplicate, owner, broker recovery")


async def test_crash_redelivery_delete_and_retry_are_safe(fixture: Fixture) -> None:
    f = fixture
    result = await f.repo.register(f.principal, f.session_id, "event-key", f.body)
    real = CeleryJobPublisher(BROKER)

    class CrashAfterPublish:
        async def publish(self, event_id, job_id):
            await real.publish(event_id, job_id)
            raise RuntimeError("simulated process crash after Redis publish")

    with pytest.raises(RuntimeError, match="simulated process crash"):
        await OutboxDispatcher(f.engine, CrashAfterPublish()).dispatch_one()
    async with f.engine.connect() as conn:
        assert (await conn.execute(text("SELECT dispatched_at FROM outbox_events WHERE app_id=:app"),
                                   {"app": f.principal.app_id})).scalar_one() is None
    assert f.broker.llen("rag_core_ingestion") == f.baseline_queue + 1
    assert await OutboxDispatcher(f.engine, real).dispatch_one()
    assert f.broker.llen("rag_core_ingestion") == f.baseline_queue + 2
    assert await f.repo.claim_job(result.job.job_id, "worker-1")
    assert not await f.repo.claim_job(result.job.job_id, "worker-2")
    assert await f.counts() == (1, 1, 1, 1)
    async with f.engine.begin() as conn:
        await conn.execute(text("""
            UPDATE ingestion_jobs SET state='failed',error_code='source_changed',
                lease_owner=NULL,lease_until=NULL WHERE job_id=:job
        """), {"job": result.job.job_id})
    retried = await f.repo.retry_job(f.principal, result.job.job_id)
    assert retried.state == "queued" and retried.attempts == 1
    assert (await f.repo.retry_job(f.principal, result.job.job_id)).state == "queued"
    assert await f.counts() == (1, 1, 1, 2)
    await f.repo.sessions.delete_session(f.principal, f.session_id)
    before = f.broker.llen("rag_core_ingestion")
    assert await OutboxDispatcher(f.engine, real).dispatch_one()
    assert f.broker.llen("rag_core_ingestion") == before
    assert not await f.repo.claim_job(result.job.job_id, "worker-3")
    assert (await f.repo.get_job(f.principal, result.job.job_id)).state == "cancelled"
    assert await f.counts() == (1, 1, 1, 2)
    with pytest.raises(ScopeError, match="session_deleted"):
        await f.repo.register(f.principal, f.session_id, "new-key", f.body)
    print("PASS real PG/Redis: crash redelivery claim-once; tombstone blocks reattach/publish")


async def test_source_validation_detach_and_new_registration(fixture: Fixture) -> None:
    f = fixture
    bad = f.body.model_copy(update={"source": f.body.source.model_copy(update={"key": "outside/x"})})
    with pytest.raises(StorageError, match="storage_forbidden"):
        await f.repo.register(f.principal, f.session_id, "bad-key", bad)
    assert await f.counts() == (0, 0, 0, 0)
    first = await f.repo.register(f.principal, f.session_id, "first", f.body)
    detached = await f.repo.detach_document(f.principal, f.session_id, first.document_id)
    assert detached.scope_revision == 2
    assert (await f.repo.detach_document(f.principal, f.session_id, first.document_id)) == detached
    replay = await f.repo.register(f.principal, f.session_id, "first", f.body)
    assert replay.job.job_id == first.job.job_id and replay.link_status == "detached"
    assert (await f.repo.list_documents(f.principal, f.session_id))[1] == ()
    second_body = f.body.model_copy(update={"external_upload_id": "app-upload-2"})
    second = await f.repo.register(f.principal, f.session_id, "second", second_body)
    assert second.document_id != first.document_id
    assert second.session.scope_revision == 3
    assert len((await f.repo.list_documents(f.principal, f.session_id))[1]) == 1
    next_session = await f.repo.sessions.create_session(f.principal, "chat-2")
    assert (await f.repo.list_documents(f.principal, next_session.session_id))[1] == ()
    third = await f.repo.register(f.principal, next_session.session_id, "first", f.body)
    assert third.document_id != first.document_id and third.session.scope_revision == 1
    assert len((await f.repo.list_documents(f.principal, f.session_id))[1]) == 1
    assert len((await f.repo.list_documents(f.principal, next_session.session_id))[1]) == 1
    assert await f.counts() == (3, 3, 3, 3)
    print("PASS real MinIO/PG: invalid prefix rollback; detached replay; fresh session upload binding")
