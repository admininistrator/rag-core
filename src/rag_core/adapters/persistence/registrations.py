"""Owner-bound upload registration, job polling/retry, and durable outbox."""

import asyncio
import hashlib
import json
from typing import Any, Protocol, cast
from uuid import UUID, uuid4

from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from rag_core.adapters.persistence.sessions import PostgresSessionRepository
from rag_core.auth import Principal
from rag_core.contracts.v1 import DocumentRegisterRequest
from rag_core.domain.metadata import ScopeError, Session
from rag_core.domain.registration import Job, JobState, RegisteredUpload, SessionDocument
from rag_core.ports.storage import SourceObject, StorageReader


class RegistrationError(Exception):
    """Safe public error; never includes user input or provider exception text."""

    def __init__(self, code: str, status_code: int) -> None:
        self.code = code
        self.status_code = status_code
        super().__init__(code)


class JobPublisher(Protocol):
    async def publish(self, event_id: UUID, job_id: UUID) -> None: ...


def _job(row: RowMapping) -> Job:
    return Job(
        row["job_id"], row["document_id"], row["version_id"],
        cast(JobState, row["state"]), row["progress"], row["error_code"],
        row["attempts"], row["max_attempts"],
    )


def _registration(row: RowMapping) -> RegisteredUpload:
    return RegisteredUpload(
        Session(row["session_id"], row["external_session_id"], row["session_status"],
                row["scope_revision"]),
        row["document_id"], row["version_id"], row["filename"],
        row["link_status"], _job(row),
    )


_REGISTRATION_SELECT = """
    SELECT r.*, s.external_session_id, s.status AS session_status, s.scope_revision,
        d.filename, l.status AS link_status, j.state, j.progress, j.error_code,
        j.attempts, j.max_attempts
    FROM upload_registrations r
    JOIN sessions s ON (s.app_id,s.owner_id,s.session_id)=(r.app_id,r.owner_id,r.session_id)
    JOIN documents d ON (d.app_id,d.owner_id,d.document_id)=(r.app_id,r.owner_id,r.document_id)
    JOIN ingestion_jobs j ON (j.app_id,j.owner_id,j.job_id)=(r.app_id,r.owner_id,r.job_id)
    JOIN session_documents l ON l.app_id=r.app_id AND l.owner_id=r.owner_id
        AND l.session_id=r.session_id AND l.upload_registration_id=r.registration_id
"""


class PostgresRegistrationRepository:
    def __init__(self, engine: AsyncEngine, storage: StorageReader) -> None:
        self.engine = engine
        self.storage = storage
        self.sessions = PostgresSessionRepository(engine)

    @staticmethod
    def _key(key: str) -> str:
        if not (1 <= len(key) <= 256) or any(ord(c) < 33 or ord(c) > 126 for c in key):
            raise RegistrationError("invalid_request", 422)
        return key

    @staticmethod
    def _request(body: DocumentRegisterRequest) -> tuple[str, SourceObject]:
        try:
            validated = DocumentRegisterRequest.model_validate(body)
        except ValidationError:
            raise RegistrationError("invalid_request", 422) from None
        canonical = json.dumps(validated.model_dump(mode="json", exclude_none=True),
                               sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        source = validated.source
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest(), SourceObject(
            source.storage_alias, source.bucket, source.key, source.version_id, source.sha256
        )

    async def _existing(self, conn: AsyncConnection, params: dict[str, Any]) -> RowMapping | None:
        rows = (
            (await conn.execute(text(_REGISTRATION_SELECT + """
                WHERE r.app_id=:app AND r.owner_id=:owner AND r.session_id=:session
                  AND (r.idempotency_key=:key OR r.external_upload_id=:upload)
                FOR UPDATE OF r
            """), params)).mappings().all()
        )
        if len(rows) > 1:
            raise ScopeError("idempotency_conflict")
        return rows[0] if rows else None

    async def register(
        self, principal: Principal, session_id: UUID, key: str,
        body: DocumentRegisterRequest,
    ) -> RegisteredUpload:
        key = self._key(key)
        request_hash, source = self._request(body)
        params: dict[str, Any] = {
            "app": principal.app_id, "owner": principal.user_id,
            "session": session_id, "key": key, "upload": body.external_upload_id,
        }
        # Check ownership before touching storage. A reattempt of an existing key
        # succeeds even if the original object was subsequently removed by the app.
        await self.sessions.get_session(principal, session_id)
        async with self.engine.begin() as conn:
            row = await self._existing(conn, params)
            if row is not None:
                if row["request_hash"] != request_hash or row["idempotency_key"] != key:
                    raise ScopeError("idempotency_conflict")
                return _registration(row)

        def measure() -> tuple[int, str, str | None]:
            with self.storage.read(principal.app_id, source) as downloaded:
                if downloaded.size <= 0:
                    raise RegistrationError("invalid_request", 422)
                return downloaded.size, downloaded.sha256, downloaded.version_id

        size, digest, storage_version = await asyncio.to_thread(measure)
        params.update({
            "registration": uuid4(), "document": uuid4(), "version": uuid4(),
            "job": uuid4(), "event": uuid4(), "hash": request_hash,
            "filename": body.filename, "alias": source.storage_alias,
            "bucket": source.bucket, "object_key": source.key,
            "source_version": storage_version, "sha": digest,
            "content_type": body.content_type, "size": size,
        })
        params["fingerprint"] = hashlib.sha256(
            f"registration-v1:{params['version']}:{digest}".encode()
        ).hexdigest()
        async with self.engine.begin() as conn:
            # Session row lock serializes duplicate requests, detach and delete.
            session = await self.sessions._lock_session(conn, params)
            if session["status"] == "deleted":
                raise ScopeError("session_deleted")
            row = await self._existing(conn, params)
            if row is not None:
                if row["request_hash"] != request_hash or row["idempotency_key"] != key:
                    raise ScopeError("idempotency_conflict")
                return _registration(row)
            await conn.execute(text("""
                INSERT INTO documents (document_id,app_id,owner_id,filename,storage_alias,bucket,object_key)
                VALUES (:document,:app,:owner,:filename,:alias,:bucket,:object_key)
            """), params)
            await conn.execute(text("""
                INSERT INTO document_versions
                    (version_id,app_id,owner_id,document_id,source_version_id,source_sha256,
                     content_type,size_bytes)
                VALUES (:version,:app,:owner,:document,:source_version,:sha,:content_type,:size)
            """), params)
            await conn.execute(text("""
                INSERT INTO ingestion_jobs
                    (job_id,app_id,owner_id,version_id,task_fingerprint)
                VALUES (:job,:app,:owner,:version,:fingerprint)
            """), params)
            await conn.execute(text("""
                INSERT INTO upload_registrations
                    (registration_id,app_id,owner_id,session_id,idempotency_key,request_hash,
                     external_upload_id,document_id,version_id,job_id)
                VALUES (:registration,:app,:owner,:session,:key,:hash,:upload,:document,:version,:job)
            """), params)
            attached = await self.sessions.attach_version(
                conn, principal, session_id, params["version"], params["registration"]
            )
            await conn.execute(text("""
                INSERT INTO outbox_events
                    (event_id,app_id,owner_id,job_id,event_type,payload)
                VALUES (:event,:app,:owner,:job,'ingest_requested','{}'::jsonb)
            """), params)
            return RegisteredUpload(
                attached, params["document"], params["version"], body.filename,
                "attached", Job(params["job"], params["document"], params["version"],
                                "queued", 0, None, 0, 3),
            )

    async def list_documents(
        self, principal: Principal, session_id: UUID,
        *, cursor: UUID | None = None, limit: int = 50,
    ) -> tuple[Session, tuple[SessionDocument, ...], UUID | None]:
        if not 1 <= limit <= 50:
            raise RegistrationError("invalid_request", 422)
        async with self.engine.begin() as conn:
            locked = await self.sessions._lock_session(conn, {
                "app": principal.app_id, "owner": principal.user_id, "session": session_id,
            })
            if locked["status"] == "deleted":
                raise ScopeError("session_deleted")
            session = Session(locked["session_id"], locked["external_session_id"],
                              "active", locked["scope_revision"])
            rows = (await conn.execute(text(_REGISTRATION_SELECT + """
                WHERE r.app_id=:app AND r.owner_id=:owner AND r.session_id=:session
                  AND l.status='attached' AND
                      (CAST(:cursor AS uuid) IS NULL OR r.registration_id > CAST(:cursor AS uuid))
                ORDER BY r.registration_id LIMIT :count
            """), {"app": principal.app_id, "owner": principal.user_id,
                    "session": session_id, "cursor": cursor, "count": limit + 1})).mappings().all()
        page = rows[:limit]
        documents = tuple(SessionDocument(
            row["document_id"], row["version_id"], row["filename"],
            row["link_status"], _job(row),
        ) for row in page)
        return session, documents, page[-1]["registration_id"] if len(rows) > limit else None

    async def detach_document(
        self, principal: Principal, session_id: UUID, document_id: UUID,
    ) -> Session:
        return await self.sessions.detach_document(principal, session_id, document_id)

    async def get_job(self, principal: Principal, job_id: UUID) -> Job:
        async with self.engine.connect() as conn:
            row = (await conn.execute(text(_REGISTRATION_SELECT + """
                WHERE r.app_id=:app AND r.owner_id=:owner AND r.job_id=:job
            """), {"app": principal.app_id, "owner": principal.user_id,
                    "job": job_id})).mappings().one_or_none()
        if row is None:
            raise ScopeError("not_found")
        return _job(row)

    async def retry_job(self, principal: Principal, job_id: UUID) -> Job:
        params = {"app": principal.app_id, "owner": principal.user_id, "job": job_id,
                  "event": uuid4()}
        async with self.engine.begin() as conn:
            row = (await conn.execute(text(_REGISTRATION_SELECT + """
                WHERE r.app_id=:app AND r.owner_id=:owner AND r.job_id=:job
                FOR UPDATE OF s, j
            """), params)).mappings().one_or_none()
            if row is None:
                raise ScopeError("not_found")
            if row["session_status"] != "active" or row["link_status"] != "attached":
                raise RegistrationError("job_not_retryable", 409)
            if row["state"] == "queued":
                return _job(row)
            if row["state"] != "failed" or row["attempts"] >= row["max_attempts"]:
                raise RegistrationError("job_not_retryable", 409)
            await conn.execute(text("""
                UPDATE ingestion_jobs SET state='queued',progress=0,error_code=NULL,
                    lease_owner=NULL,lease_until=NULL,updated_at=now()
                WHERE app_id=:app AND owner_id=:owner AND job_id=:job
            """), params)
            await conn.execute(text("""
                INSERT INTO outbox_events
                    (event_id,app_id,owner_id,job_id,event_type,payload)
                VALUES (:event,:app,:owner,:job,'ingest_requested','{}'::jsonb)
            """), params)
            return Job(job_id, row["document_id"], row["version_id"],
                       "queued", 0, None, row["attempts"], row["max_attempts"])

    async def claim_job(self, job_id: UUID, worker_id: str) -> bool:
        """T19 consumer gate: duplicate deliveries may claim a queued job once."""
        if not worker_id or len(worker_id) > 128:
            raise ValueError("invalid worker ID")
        async with self.engine.begin() as conn:
            row = (await conn.execute(text(_REGISTRATION_SELECT + """
                WHERE r.job_id=:job FOR UPDATE OF s, j
            """), {"job": job_id})).mappings().one_or_none()
            if row is None or row["state"] != "queued":
                return False
            params = {"job": job_id, "app": row["app_id"], "owner": row["owner_id"],
                      "worker": worker_id}
            if row["session_status"] != "active" or row["link_status"] != "attached":
                await conn.execute(text("""
                    UPDATE ingestion_jobs SET state='cancelled',updated_at=now()
                    WHERE job_id=:job AND app_id=:app AND owner_id=:owner
                """), params)
                return False
            await conn.execute(text("""
                UPDATE ingestion_jobs SET state='fetching',attempts=attempts+1,
                    lease_owner=:worker,lease_until=now()+interval '5 minutes',updated_at=now()
                WHERE job_id=:job AND app_id=:app AND owner_id=:owner
            """), params)
            return True


class OutboxDispatcher:
    def __init__(self, engine: AsyncEngine, publisher: JobPublisher) -> None:
        self.engine = engine
        self.publisher = publisher

    async def dispatch_one(self) -> bool:
        """Publish under the row lock, then mark sent. A crash can redeliver, never lose."""
        async with self.engine.begin() as conn:
            event = (await conn.execute(text("""
                SELECT event_id,job_id FROM outbox_events
                WHERE dispatched_at IS NULL AND available_at<=now()
                ORDER BY available_at,event_id LIMIT 1 FOR UPDATE SKIP LOCKED
            """))).mappings().one_or_none()
            if event is None:
                return False
            job_id = event["job_id"]
            row = (await conn.execute(text(_REGISTRATION_SELECT + """
                WHERE r.job_id=:job FOR UPDATE OF s, j
            """), {"job": job_id})).mappings().one_or_none()
            if row is None:
                raise RuntimeError("outbox job lacks registration")
            if row["session_status"] != "active" or row["link_status"] != "attached":
                await conn.execute(text("""
                    UPDATE ingestion_jobs SET state='cancelled',updated_at=now()
                    WHERE job_id=:job AND state='queued'
                """), {"job": job_id})
            elif row["state"] == "queued":
                await self.publisher.publish(event["event_id"], job_id)
            await conn.execute(text("""
                UPDATE outbox_events SET dispatched_at=now(),attempts=attempts+1
                WHERE event_id=:event
            """), {"event": event["event_id"]})
            return True
