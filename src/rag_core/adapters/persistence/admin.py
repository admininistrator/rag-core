"""Explicit metadata projections and audited, fenced administration transactions.

No storage, model, LLM, vector or raw-chunk capability is exposed here.
"""

import html
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from rag_core.adapters.persistence.ingestion import PostgresIngestionRepository
from rag_core.adapters.persistence.registrations import PostgresRegistrationRepository
from rag_core.adapters.persistence.sessions import PostgresSessionRepository
from rag_core.admin.auth import AdminError, audit
from rag_core.auth import Principal

# Server constants only. Identifiers never come from a request.
PROJECTIONS = {
    "documents": (
        "document_versions v JOIN documents d USING (app_id,owner_id,document_id)",
        "v.version_id",
        "v.version_id,v.document_id,v.app_id,v.owner_id,d.filename,"
        "v.content_type,v.size_bytes,v.state,v.active_generation_id,v.created_at",
        "v.state",
    ),
    "jobs": (
        "ingestion_jobs j",
        "j.job_id",
        "j.job_id,j.version_id,j.app_id,j.owner_id,j.state,j.progress,j.attempts,"
        "j.max_attempts,(j.error_code IS NOT NULL) AS has_error,j.updated_at",
        "j.state",
    ),
    "sessions": (
        "sessions s",
        "s.session_id",
        "s.session_id,s.app_id,s.owner_id,s.external_session_id,s.status,s.scope_revision,"
        "s.created_at,s.deleted_at",
        "s.status",
    ),
    "index": (
        "index_generations g",
        "g.generation_id",
        "g.generation_id,g.version_id,g.app_id,g.owner_id,g.state,g.chunk_count,"
        "g.index_fingerprint,g.pipeline_fingerprint,g.created_at",
        "g.state",
    ),
    "audit": (
        "audit_events a",
        "a.event_id",
        "a.event_id,a.actor,a.action,a.target_id,a.related_id,a.request_id,a.outcome,a.created_at",
        "a.outcome",
    ),
}


def safe_value(key: str, value: Any) -> Any:
    if isinstance(value, UUID | datetime):
        return str(value) if isinstance(value, UUID) else value.isoformat()
    if isinstance(value, str):
        # Arbitrary pipeline error text/fingerprints are never reflected as metadata.
        if key.endswith("fingerprint") and (
            len(value) != 64 or any(c not in "0123456789abcdef" for c in value)
        ):
            return None
        return html.escape("".join(c for c in value[:1024] if ord(c) >= 32), quote=True)
    return value


async def metadata_page(
    conn: AsyncConnection,
    resource: str,
    *,
    cursor: UUID | None,
    limit: int,
    app: str | None,
    owner: str | None,
    state: str | None,
    content_type: str | None = None,
) -> dict[str, Any]:
    if resource not in PROJECTIONS:
        raise AdminError("not_found", 404)
    table, identity, columns, status = PROJECTIONS[resource]
    filters = [f"(CAST(:cursor AS uuid) IS NULL OR {identity}>:cursor)"]
    params: dict[str, Any] = {"cursor": cursor, "limit": limit + 1}
    if resource == "audit" and (app is not None or owner is not None or content_type is not None):
        raise AdminError("invalid_request", 422)
    for key, value, column in [
        ("app", app, "app_id"),
        ("owner", owner, "owner_id"),
        ("state", state, status),
        ("content_type", content_type, "v.content_type"),
    ]:
        if value is not None:
            if key == "content_type" and resource != "documents":
                raise AdminError("invalid_request", 422)
            # Qualify owner fields to avoid ambiguity in the documents join.
            if key in {"app", "owner"}:
                column = identity.split(".")[0] + "." + column
            filters.append(f"{column}=:{key}")
            params[key] = value
    rows = (
        (
            await conn.execute(
                text(
                    f"SELECT {columns} FROM {table} WHERE "
                    + " AND ".join(filters)
                    + f" ORDER BY {identity} LIMIT :limit"
                ),
                params,
            )
        )
        .mappings()
        .all()
    )
    page = rows[:limit]
    id_column = identity.split(".")[1]
    return {
        "items": [{k: safe_value(k, v) for k, v in row.items()} for row in page],
        "next_cursor": str(page[-1][id_column]) if len(rows) > limit else None,
    }


async def overview(conn: AsyncConnection) -> dict[str, Any]:
    counts = {}
    for name, table in [
        ("documents", "documents"),
        ("sessions", "sessions"),
        ("generations", "index_generations"),
        ("chunks", "chunks"),
    ]:
        counts[name] = (await conn.execute(text(f"SELECT count(*) FROM {table}"))).scalar_one()
    jobs = (
        (
            await conn.execute(
                text(
                    "SELECT state,count(*) AS count FROM ingestion_jobs "
                    "GROUP BY state ORDER BY state"
                )
            )
        )
        .mappings()
        .all()
    )
    counts["pending_outbox"] = (
        await conn.execute(text("SELECT count(*) FROM outbox_events WHERE dispatched_at IS NULL"))
    ).scalar_one()
    sizes = (
        (
            await conn.execute(
                text("""
        SELECT pg_database_size(current_database()) AS metadata_database_bytes,
            coalesce(sum(size_bytes),0) AS registered_source_bytes FROM document_versions
    """)
            )
        )
        .mappings()
        .one()
    )
    return {
        "counts": counts,
        "jobs": [dict(row) for row in jobs],
        "sizes": {k: int(v) for k, v in sizes.items()},
    }


async def session_action(
    conn: AsyncConnection,
    sessions: PostgresSessionRepository,
    action: str,
    session_id: UUID,
    document_id: UUID | None,
) -> None:
    row = (
        (
            await conn.execute(
                text("SELECT * FROM sessions WHERE session_id=:session FOR UPDATE"),
                {"session": session_id},
            )
        )
        .mappings()
        .one_or_none()
    )
    if row is None:
        raise AdminError("not_found", 404)
    params: dict[str, Any] = {
        "app": row["app_id"],
        "owner": row["owner_id"],
        "session": session_id,
        "document": document_id,
    }
    if action == "session_detach":
        if row["status"] == "deleted":
            raise AdminError("session_deleted", 410)
        links = (
            (
                await conn.execute(
                    text("""
            SELECT status FROM session_documents WHERE session_id=:session
                AND document_id=:document AND app_id=:app AND owner_id=:owner
        """),
                    params,
                )
            )
            .scalars()
            .all()
        )
        if not links:
            raise AdminError("not_found", 404)
        if "attached" not in links:
            return
    elif row["status"] == "deleted":
        return
    await conn.execute(
        text(
            """
        UPDATE session_documents SET status='detached',detached_at=now()
        WHERE session_id=:session AND app_id=:app AND owner_id=:owner AND status='attached'
    """
            + (" AND document_id=:document" if action == "session_detach" else "")
        ),
        params,
    )
    if action == "session_tombstone":
        await conn.execute(
            text("""
            UPDATE sessions SET status='deleted',deleted_at=now()
            WHERE session_id=:session AND app_id=:app AND owner_id=:owner
        """),
            params,
        )
    await sessions._bump(conn, params)


async def job_action(
    conn: AsyncConnection, ingestion: PostgresIngestionRepository, action: str, job_id: UUID
) -> None:
    row = await ingestion._row(conn, job_id)
    if row is None:
        raise AdminError("not_found", 404)
    principal = Principal(row["app_id"], row["owner_id"])
    if action == "job_retry":
        await PostgresRegistrationRepository.retry_job_in_transaction(conn, principal, job_id)
    elif action == "job_reindex":
        await ingestion.reindex_in_transaction(conn, principal, job_id)
    else:
        if row["state"] == "cancelled":
            return
        if row["state"] in {"ready", "failed"}:
            raise AdminError("invalid_transition", 409)
        params = {"job": job_id, "version": row["version_id"]}
        await conn.execute(
            text("""
            UPDATE index_generations SET state='failed' WHERE job_id=:job AND state='staging'
        """),
            params,
        )
        await conn.execute(
            text("""
            UPDATE ingestion_jobs SET state='cancelled',lease_owner=NULL,lease_until=NULL,
                error_code=NULL,updated_at=now() WHERE job_id=:job
        """),
            params,
        )
        await conn.execute(
            text("""
            UPDATE document_versions SET state='cancelled'
            WHERE version_id=:version AND active_generation_id IS NULL
        """),
            params,
        )


async def audited_action(
    conn: AsyncConnection,
    request_id: UUID,
    action: str,
    target: UUID,
    engine: AsyncEngine,
    document_id: UUID | None = None,
) -> None:
    if action.startswith("session_"):
        await session_action(conn, PostgresSessionRepository(engine), action, target, document_id)
    else:
        await job_action(conn, PostgresIngestionRepository(engine), action, target)
    await audit(conn, action, request_id, target=target, related=document_id)
