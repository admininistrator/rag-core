"""Transactional session lifecycle and one-statement authorization snapshots.

Only trusted backend registration may call attach_version; storage validation and
registration/job/outbox atomicity belong to T12. No method lists a user's library.
"""

from typing import cast
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from rag_core.auth import Principal
from rag_core.domain.metadata import (
    ScopeError,
    ScopeSnapshot,
    Session,
    SessionStatus,
    VersionGeneration,
)


def _owner(principal: Principal, session_id: UUID) -> dict[str, object]:
    return {"app": principal.app_id, "owner": principal.user_id, "session": session_id}


def _session(row: RowMapping) -> Session:
    return Session(
        row["session_id"],
        row["external_session_id"],
        cast(SessionStatus, row["status"]),
        row["scope_revision"],
    )


def _active(row: RowMapping | None) -> RowMapping:
    if row is None:
        raise ScopeError("not_found")
    if row["status"] == "deleted":
        raise ScopeError("session_deleted")
    return row


class PostgresSessionRepository:
    def __init__(self, engine: AsyncEngine) -> None:
        self.engine = engine

    async def create_session(self, principal: Principal, external_session_id: str) -> Session:
        if not external_session_id.strip():
            raise ScopeError("invalid_request")
        params = {**_owner(principal, uuid4()), "external": external_session_id}
        async with self.engine.begin() as conn:
            await conn.execute(
                text("""
                INSERT INTO sessions (session_id, app_id, owner_id, external_session_id)
                VALUES (:session, :app, :owner, :external)
                ON CONFLICT (app_id, owner_id, external_session_id) DO NOTHING
            """),
                params,
            )
            row = (
                (
                    await conn.execute(
                        text("""
                SELECT * FROM sessions WHERE app_id=:app AND owner_id=:owner
                AND external_session_id=:external FOR UPDATE
            """),
                        params,
                    )
                )
                .mappings()
                .one()
            )
            return _session(_active(row))

    async def get_session(self, principal: Principal, session_id: UUID) -> Session:
        async with self.engine.connect() as conn:
            row = (
                (
                    await conn.execute(
                        text("""
                SELECT * FROM sessions
                WHERE app_id=:app AND owner_id=:owner AND session_id=:session
            """),
                        _owner(principal, session_id),
                    )
                )
                .mappings()
                .one_or_none()
            )
            return _session(_active(row))

    async def _lock_session(
        self,
        conn: AsyncConnection,
        params: dict[str, object],
    ) -> RowMapping:
        row = (
            (
                await conn.execute(
                    text("""
            SELECT * FROM sessions
            WHERE app_id=:app AND owner_id=:owner AND session_id=:session FOR UPDATE
        """),
                    params,
                )
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            raise ScopeError("not_found")
        return row

    async def delete_session(self, principal: Principal, session_id: UUID) -> Session:
        params = _owner(principal, session_id)
        async with self.engine.begin() as conn:
            row = await self._lock_session(conn, params)
            if row["status"] == "deleted":
                return _session(row)
            await conn.execute(
                text("""
                UPDATE session_documents SET status='detached', detached_at=now()
                WHERE app_id=:app AND owner_id=:owner AND session_id=:session
                AND status='attached'
            """),
                params,
            )
            row = (
                (
                    await conn.execute(
                        text("""
                UPDATE sessions SET status='deleted', deleted_at=now(),
                    scope_revision=scope_revision+1
                WHERE app_id=:app AND owner_id=:owner AND session_id=:session RETURNING *
            """),
                        params,
                    )
                )
                .mappings()
                .one()
            )
            return _session(row)

    async def detach_document(
        self,
        principal: Principal,
        session_id: UUID,
        document_id: UUID,
    ) -> Session:
        params = {**_owner(principal, session_id), "document": document_id}
        async with self.engine.begin() as conn:
            row = _active(await self._lock_session(conn, params))
            links = (
                (
                    await conn.execute(
                        text("""
                SELECT status FROM session_documents
                WHERE app_id=:app AND owner_id=:owner AND session_id=:session
                    AND document_id=:document
            """),
                        params,
                    )
                )
                .scalars()
                .all()
            )
            if not links:
                raise ScopeError("not_found")
            if "attached" not in links:
                return _session(row)
            await conn.execute(
                text("""
                UPDATE session_documents SET status='detached', detached_at=now()
                WHERE app_id=:app AND owner_id=:owner AND session_id=:session
                    AND document_id=:document AND status='attached'
            """),
                params,
            )
            return await self._bump(conn, params)

    async def _bump(self, conn: AsyncConnection, params: dict[str, object]) -> Session:
        row = (
            (
                await conn.execute(
                    text("""
            UPDATE sessions SET scope_revision=scope_revision+1
            WHERE app_id=:app AND owner_id=:owner AND session_id=:session RETURNING *
        """),
                    params,
                )
            )
            .mappings()
            .one()
        )
        return _session(row)

    async def attach_version(
        self,
        conn: AsyncConnection,
        principal: Principal,
        session_id: UUID,
        version_id: UUID,
        upload_registration_id: UUID,
    ) -> Session:
        """Internal registration primitive in the caller's transaction (T12).

        A registration UUID is provenance, never proof of permission. Caller must
        verify app upload/storage and commit registration/job/outbox with this link.
        Reusing a detached registration never resurrects it.
        """
        if not conn.in_transaction():
            raise ValueError("attach_version requires a caller-owned transaction")
        params = {
            **_owner(principal, session_id),
            "version": version_id,
            "registration": upload_registration_id,
            "link": uuid4(),
        }
        row = _active(await self._lock_session(conn, params))
        version = (
            (
                await conn.execute(
                    text("""
            SELECT document_id FROM document_versions
            WHERE app_id=:app AND owner_id=:owner AND version_id=:version
        """),
                    params,
                )
            )
            .mappings()
            .one_or_none()
        )
        if version is None:
            raise ScopeError("not_found")
        prior = (
            (
                await conn.execute(
                    text("""
            SELECT version_id, status FROM session_documents
            WHERE app_id=:app AND owner_id=:owner AND session_id=:session
                AND upload_registration_id=:registration
        """),
                    params,
                )
            )
            .mappings()
            .one_or_none()
        )
        if prior is not None:
            if prior["version_id"] != version_id:
                raise ScopeError("idempotency_conflict")
            return _session(row)
        params["document"] = version["document_id"]
        attached = (
            (
                await conn.execute(
                    text("""
            SELECT document_id FROM session_documents
            WHERE app_id=:app AND owner_id=:owner AND session_id=:session AND status='attached'
        """),
                    params,
                )
            )
            .scalars()
            .all()
        )
        if params["document"] in attached:
            raise ScopeError("idempotency_conflict")
        if len(attached) >= 50:
            raise ScopeError("invalid_request")
        await conn.execute(
            text("""
            INSERT INTO session_documents
                (link_id, app_id, owner_id, session_id, document_id, version_id,
                 upload_registration_id)
            VALUES (:link, :app, :owner, :session, :document, :version, :registration)
        """),
            params,
        )
        return await self._bump(conn, params)

    async def resolve_scope(
        self,
        principal: Principal,
        session_id: UUID,
        document_ids: tuple[UUID, ...] | None = None,
    ) -> ScopeSnapshot:
        if document_ids is not None and (
            not document_ids
            or len(document_ids) > 50
            or len(set(document_ids)) != len(document_ids)
        ):
            raise ScopeError("invalid_request")
        # One READ COMMITTED statement: revision and links cannot straddle a commit.
        # Keep nonready rows so readiness never silently reduces selected scope.
        async with self.engine.connect() as conn:
            rows = (
                (
                    await conn.execute(
                        text("""
                SELECT s.session_id, s.status, s.scope_revision,
                    l.document_id, l.version_id, v.state AS version_state,
                    v.active_generation_id, g.state AS generation_state
                FROM sessions s
                LEFT JOIN session_documents l ON l.app_id=s.app_id AND l.owner_id=s.owner_id
                    AND l.session_id=s.session_id AND l.status='attached'
                LEFT JOIN document_versions v ON v.app_id=l.app_id AND v.owner_id=l.owner_id
                    AND v.document_id=l.document_id AND v.version_id=l.version_id
                LEFT JOIN index_generations g ON g.app_id=v.app_id AND g.owner_id=v.owner_id
                    AND g.version_id=v.version_id AND g.generation_id=v.active_generation_id
                WHERE s.app_id=:app AND s.owner_id=:owner AND s.session_id=:session
                ORDER BY l.document_id
            """),
                        _owner(principal, session_id),
                    )
                )
                .mappings()
                .all()
            )
        session = _active(rows[0] if rows else None)
        available = {r["document_id"]: r for r in rows if r["document_id"] is not None}
        if document_ids is not None and not set(document_ids).issubset(available):
            raise ScopeError("not_found")
        if not available:
            raise ScopeError("no_session_documents")
        selected = [available[key] for key in sorted(document_ids or available)]
        if any(
            r["version_state"] != "ready"
            or r["generation_state"] != "ready"
            or r["active_generation_id"] is None
            for r in selected
        ):
            raise ScopeError("documents_not_ready")
        return ScopeSnapshot(
            principal,
            session_id,
            session["scope_revision"],
            tuple(sorted(document_ids)) if document_ids is not None else None,
            tuple(
                VersionGeneration(r["document_id"], r["version_id"], r["active_generation_id"])
                for r in selected
            ),
        )

    async def validate_snapshot(self, snapshot: ScopeSnapshot) -> None:
        try:
            current = await self.resolve_scope(
                snapshot.principal,
                snapshot.session_id,
                snapshot.requested_document_ids,
            )
        except ScopeError:
            raise ScopeError("session_scope_changed") from None
        if current != snapshot:
            raise ScopeError("session_scope_changed")
