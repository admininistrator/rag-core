"""Fenced PG jobs, staged chunks, lease recovery and atomic ready publication."""

import hashlib
import json
from typing import Any
from uuid import UUID, uuid4

from pydantic import TypeAdapter
from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from rag_core.auth import Principal
from rag_core.domain.chunking import Chunk
from rag_core.domain.ingestion import (
    IngestionError,
    IngestionLease,
    chunk_manifest,
    digest,
    vector_unit_id,
)
from rag_core.domain.metadata import VersionGeneration
from rag_core.domain.vectors import GenerationScope
from rag_core.ports.storage import SourceObject

_CHUNK = TypeAdapter(Chunk)
_SELECT = """
    SELECT j.*, r.session_id, d.document_id, d.filename, d.storage_alias,d.bucket,d.object_key,
        v.source_sha256,v.source_version_id,v.size_bytes,v.content_type,v.active_generation_id,
        s.status AS session_status,l.status AS link_status,
        (j.lease_until > now()) AS lease_valid
    FROM ingestion_jobs j JOIN upload_registrations r
        ON (r.app_id,r.owner_id,r.job_id)=(j.app_id,j.owner_id,j.job_id)
    JOIN sessions s ON (s.app_id,s.owner_id,s.session_id)=(r.app_id,r.owner_id,r.session_id)
    JOIN session_documents l ON (l.app_id,l.owner_id,l.upload_registration_id)=
        (r.app_id,r.owner_id,r.registration_id) AND l.session_id=r.session_id
    JOIN document_versions v ON (v.app_id,v.owner_id,v.version_id)=
        (j.app_id,j.owner_id,j.version_id)
    JOIN documents d ON (d.app_id,d.owner_id,d.document_id)=(v.app_id,v.owner_id,v.document_id)
"""
_STAGES = {"fetching": 5, "parsing": 20, "chunking": 40, "embedding": 55, "indexing": 80}


def _params(lease: IngestionLease) -> dict[str, Any]:
    return {"job": lease.job_id, "app": lease.principal.app_id,
            "owner": lease.principal.user_id, "worker": lease.owner,
            "version": lease.scope.pair.version_id, "generation": lease.scope.pair.generation_id}


class PostgresIngestionRepository:
    def __init__(self, engine: AsyncEngine, *, lease_seconds: int = 120) -> None:
        if not 10 <= lease_seconds <= 600:
            raise ValueError("invalid lease duration")
        self.engine = engine
        self.lease_seconds = lease_seconds

    async def _row(
        self, conn: AsyncConnection, job_id: UUID, *, version_lock: bool = True
    ) -> RowMapping | None:
        locks = "s,j,v" if version_lock else "s,j"
        return (await conn.execute(text(_SELECT +
            f" WHERE j.job_id=:job FOR UPDATE OF {locks}"),
            {"job": job_id})).mappings().one_or_none()

    async def _fenced(
        self, conn: AsyncConnection, lease: IngestionLease, *, generation_lock: bool = True
    ) -> RowMapping:
        row = await self._row(conn, lease.job_id, version_lock=generation_lock)
        if (row is None or row["app_id"] != lease.principal.app_id
            or row["owner_id"] != lease.principal.user_id
            or row["version_id"] != lease.scope.pair.version_id
            or row["document_id"] != lease.scope.pair.document_id
            or row["lease_owner"] != lease.owner or not row["lease_valid"]
            or row["state"] not in _STAGES):
            raise IngestionError("ingestion_lease_lost")
        if row["session_status"] != "active" or row["link_status"] != "attached":
            raise IngestionError("ingestion_cancelled")
        generation = (await conn.execute(text("""
            SELECT state FROM index_generations WHERE app_id=:app AND owner_id=:owner
                AND version_id=:version AND generation_id=:generation
                AND job_id=:job AND lease_owner=:worker
        """ + (" FOR UPDATE" if generation_lock else "")),
            _params(lease))).scalar_one_or_none()
        if generation != "staging":
            raise IngestionError("ingestion_lease_lost")
        return row

    async def claim(
        self, job_id: UUID, index_fingerprint: str, pipeline_fingerprint: str
    ) -> IngestionLease | None:
        async with self.engine.begin() as conn:
            # Redelivery must not wait for Qdrant's version lock for an already
            # claimed job. The locked check below still arbitrates concurrent claims.
            state = (await conn.execute(text("SELECT state FROM ingestion_jobs WHERE job_id=:job"),
                                        {"job": job_id})).scalar_one_or_none()
            if state != "queued":
                return None
            row = await self._row(conn, job_id)
            if row is None or row["state"] != "queued":
                return None
            params: dict[str, Any] = {
                "job": job_id, "worker": uuid4().hex, "generation": uuid4(),
                "app": row["app_id"], "owner": row["owner_id"], "version": row["version_id"],
                "index": index_fingerprint, "pipeline": pipeline_fingerprint,
                "duration": self.lease_seconds,
                "task": digest([row["source_sha256"], pipeline_fingerprint]),
            }
            if (row["session_status"] != "active" or row["link_status"] != "attached"
                or row["attempts"] >= row["max_attempts"]):
                params["terminal"] = "cancelled" if (
                    row["session_status"] != "active" or row["link_status"] != "attached"
                ) else "failed"
                await conn.execute(text("""
                    UPDATE ingestion_jobs SET state=:terminal,lease_owner=NULL,lease_until=NULL,
                        updated_at=now() WHERE job_id=:job
                """), params)
                return None
            await conn.execute(text("""
                UPDATE ingestion_jobs SET state='fetching',progress=5,attempts=attempts+1,
                    lease_owner=:worker,lease_until=now()+(:duration*interval '1 second'),
                    updated_at=now(),error_code=NULL,task_fingerprint=:task WHERE job_id=:job
            """), params)
            await conn.execute(text("""
                INSERT INTO index_generations
                    (generation_id,app_id,owner_id,version_id,index_fingerprint,
                     pipeline_fingerprint,job_id,lease_owner)
                VALUES (:generation,:app,:owner,:version,:index,:pipeline,:job,:worker)
            """), params)
            return IngestionLease(
                job_id, Principal(row["app_id"], row["owner_id"]), row["session_id"],
                GenerationScope(Principal(row["app_id"], row["owner_id"]), VersionGeneration(
                    row["document_id"], row["version_id"], params["generation"])),
                params["worker"], SourceObject(row["storage_alias"], row["bucket"], row["object_key"],
                    row["source_version_id"], row["source_sha256"]),
                row["filename"], row["content_type"], row["size_bytes"],
            )

    async def heartbeat(self, lease: IngestionLease) -> None:
        async with self.engine.begin() as conn:
            # Heartbeat shares only session/job locks, so slow bounded Qdrant I/O
            # cannot block renewal behind its version/generation lock.
            await self._fenced(conn, lease, generation_lock=False)
            await conn.execute(text("""
                UPDATE ingestion_jobs SET lease_until=now()+(:duration*interval '1 second'),
                    updated_at=now() WHERE job_id=:job
            """), {**_params(lease), "duration": self.lease_seconds})

    async def advance(self, lease: IngestionLease, state: str, progress: int) -> None:
        if state not in _STAGES or not _STAGES[state] <= progress < 100:
            raise IngestionError("invalid_ingestion_transition")
        async with self.engine.begin() as conn:
            row = await self._fenced(conn, lease)
            if _STAGES[state] < _STAGES[row["state"]] or progress < row["progress"]:
                raise IngestionError("invalid_ingestion_transition")
            await conn.execute(text("""
                UPDATE ingestion_jobs SET state=:state,progress=:progress,updated_at=now()
                WHERE job_id=:job
            """), {**_params(lease), "state": state, "progress": progress})
            # Reindex must keep the published version ready until replacement succeeds.
            await conn.execute(text("""
                UPDATE document_versions SET state=:state
                WHERE version_id=:version AND active_generation_id IS NULL
            """), {**_params(lease), "state": state})

    async def stage_chunks(self, lease: IngestionLease, chunks: tuple[Chunk, ...]) -> None:
        if (not chunks or len(chunks) > 100_000
            or sum(len(c.text) for c in chunks) > 32 * 1024 * 1024
            or any(c.source.document_id != lease.scope.pair.document_id
                   or c.source.version_id != lease.scope.pair.version_id
                   or c.source.sha256 != lease.source.sha256
                   or c.generation_id != lease.scope.pair.generation_id
                   or c.ordinal != i or not 1 <= c.token_count <= 512
                   or hashlib.sha256(c.text.encode()).hexdigest() != c.checksum
                   for i, c in enumerate(chunks))):
            raise IngestionError("invalid_chunk_manifest")
        async with self.engine.begin() as conn:
            row = await self._fenced(conn, lease)
            if row["state"] != "chunking":
                raise IngestionError("invalid_ingestion_transition")
            params = _params(lease)
            records = []
            for c in chunks:
                data = _CHUNK.dump_python(c, mode="json", exclude={"text"})
                records.append({**params, "chunk": c.id, "ordinal": c.ordinal, "text": c.text,
                    "sha": c.checksum, "tokens": c.token_count, "unit": vector_unit_id(c),
                    "map": json.dumps(data, ensure_ascii=False)})
            await conn.execute(text("""
                INSERT INTO chunks (chunk_id,app_id,owner_id,version_id,generation_id,ordinal,
                    text,checksum,token_count,language,unit_id,source_map)
                VALUES (:chunk,:app,:owner,:version,:generation,:ordinal,:text,:sha,:tokens,
                    'und',:unit,CAST(:map AS jsonb))
            """), records)
            await conn.execute(text("""
                UPDATE index_generations SET chunk_count=:count,manifest_sha256=:manifest
                WHERE generation_id=:generation AND state='staging' AND lease_owner=:worker
            """), {**params, "count": len(chunks), "manifest": chunk_manifest(chunks)})

    async def publish(
        self, lease: IngestionLease, expected_count: int, expected_manifest: str,
        extraction_fingerprint: str,
    ) -> None:
        async with self.engine.begin() as conn:
            row = await self._fenced(conn, lease)
            params = _params(lease)
            generation = (await conn.execute(text("""
                SELECT * FROM index_generations WHERE generation_id=:generation
                AND app_id=:app AND owner_id=:owner AND version_id=:version FOR UPDATE
            """), params)).mappings().one()
            chunks = (await conn.execute(text("""
                SELECT chunk_id,ordinal,checksum,text,source_map FROM chunks
                WHERE app_id=:app AND owner_id=:owner AND version_id=:version
                    AND generation_id=:generation ORDER BY ordinal
            """), params)).mappings().all()
            if (row["state"] != "indexing" or generation["state"] != "staging"
                or generation["lease_owner"] != lease.owner
                or generation["chunk_count"] != expected_count or len(chunks) != expected_count
                or generation["manifest_sha256"] != expected_manifest
                or digest([(str(c["chunk_id"]), c["ordinal"], c["checksum"],
                            digest(c["source_map"])) for c in chunks])
                    != expected_manifest
                or any(hashlib.sha256(c["text"].encode()).hexdigest() != c["checksum"]
                       or c["source_map"]["checksum"] != c["checksum"] for c in chunks)):
                raise IngestionError("ingestion_manifest_mismatch")
            await conn.execute(text("""
                UPDATE index_generations SET state='ready' WHERE generation_id=:generation
            """), params)
            await conn.execute(text("""
                UPDATE document_versions SET state='ready',active_generation_id=:generation,
                    index_fingerprint=:index,extraction_fingerprint=:extraction
                WHERE app_id=:app AND owner_id=:owner AND version_id=:version
            """), {**params, "index": generation["index_fingerprint"],
                    "extraction": extraction_fingerprint})
            await conn.execute(text("""
                UPDATE ingestion_jobs SET state='ready',progress=100,error_code=NULL,
                    lease_owner=NULL,lease_until=NULL,updated_at=now() WHERE job_id=:job
            """), params)
            # No SessionDocument INSERT/UPDATE: completion cannot resurrect a link.

    async def fail(self, lease: IngestionLease, code: str, *, retryable: bool) -> None:
        async with self.engine.begin() as conn:
            row = await self._row(conn, lease.job_id)
            if row is None or row["lease_owner"] != lease.owner or row["state"] not in _STAGES:
                return
            await self._finish_failure(conn, row, code, retryable)

    async def _finish_failure(
        self, conn: AsyncConnection, row: RowMapping, code: str, retryable: bool
    ) -> None:
        cancelled = row["session_status"] != "active" or row["link_status"] != "attached"
        retry = retryable and not cancelled and row["attempts"] < row["max_attempts"]
        state = "cancelled" if cancelled else "queued" if retry else "failed"
        params = {"job": row["job_id"], "worker": row["lease_owner"], "version": row["version_id"],
                  "state": state, "code": code, "event": uuid4(),
                  "app": row["app_id"], "owner": row["owner_id"], "backoff": 2**row["attempts"]}
        await conn.execute(text("""
            UPDATE index_generations SET state='failed'
            WHERE job_id=:job AND lease_owner=:worker AND state='staging'
        """), params)
        await conn.execute(text("""
            UPDATE ingestion_jobs SET state=:state,error_code=:code,progress=0,
                lease_owner=NULL,lease_until=NULL,updated_at=now() WHERE job_id=:job
        """), params)
        await conn.execute(text("""
            UPDATE document_versions SET state=:state
            WHERE version_id=:version AND active_generation_id IS NULL
        """), params)
        if retry:
            await conn.execute(text("""
                INSERT INTO outbox_events (event_id,app_id,owner_id,job_id,event_type,available_at)
                VALUES (:event,:app,:owner,:job,'ingest_requested',
                    now()+(:backoff*interval '1 second'))
            """), params)

    async def recover_one(self) -> bool:
        """Dispatcher watchdog: recover expired work even if the Redis message vanished."""
        async with self.engine.begin() as conn:
            job = (await conn.execute(text("""
                SELECT job_id FROM ingestion_jobs WHERE lease_until<=now()
                ORDER BY lease_until LIMIT 1
            """))).scalar_one_or_none()
            if job is None:
                # Re-publish queued events lost on broker restart, bounded at five minutes.
                event = (await conn.execute(text("""
                    SELECT e.event_id FROM outbox_events e JOIN ingestion_jobs j
                        ON j.job_id=e.job_id
                    WHERE j.state='queued' AND e.dispatched_at < now()-interval '5 minutes'
                        AND NOT EXISTS (SELECT 1 FROM outbox_events p
                            WHERE p.job_id=j.job_id AND p.dispatched_at IS NULL)
                    ORDER BY e.dispatched_at LIMIT 1 FOR UPDATE OF e SKIP LOCKED
                """))).scalar_one_or_none()
                if event is None:
                    return False
                await conn.execute(text("""
                    UPDATE outbox_events SET dispatched_at=NULL,available_at=now()
                    WHERE event_id=:event
                """), {"event": event})
                return True
            row = await self._row(conn, job)
            if row is None or row["lease_valid"] or row["state"] not in _STAGES:
                return False
            await self._finish_failure(conn, row, "ingestion_lease_expired", True)
            return True

    async def request_reindex(self, principal: Principal, job_id: UUID) -> None:
        """Trusted internal operation, requires the original active registration."""
        async with self.engine.begin() as conn:
            row = await self._row(conn, job_id)
            if (row is None or (row["app_id"], row["owner_id"]) !=
                (principal.app_id, principal.user_id) or row["state"] != "ready"
                or row["session_status"] != "active" or row["link_status"] != "attached"):
                raise IngestionError("reindex_not_authorized")
            await conn.execute(text("""
                UPDATE ingestion_jobs SET state='queued',attempts=0,progress=0,updated_at=now()
                WHERE job_id=:job
            """), {"job": job_id})
            await conn.execute(text("""
                INSERT INTO outbox_events (event_id,app_id,owner_id,job_id,event_type)
                VALUES (:event,:app,:owner,:job,'ingest_requested')
            """), {"event": uuid4(), "app": principal.app_id,
                    "owner": principal.user_id, "job": job_id})
