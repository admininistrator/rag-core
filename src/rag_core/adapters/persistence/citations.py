"""Exact-owner, exact-ready-pair citation reads; retained UUIDs never grant access."""

from uuid import UUID

from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from rag_core.adapters.persistence.evidence import PostgresEvidenceRepository
from rag_core.domain.answers import CitationSource
from rag_core.domain.evidence import EvidenceError
from rag_core.domain.metadata import ScopeError, ScopeSnapshot
from rag_core.domain.vectors import VectorChunk
from rag_core.ports.metadata import SessionRepository


class PostgresCitationRepository:
    def __init__(self, engine: AsyncEngine, sessions: SessionRepository) -> None:
        self._engine = engine
        self._sessions = sessions
        self._evidence = PostgresEvidenceRepository(engine, sessions)

    async def load(
        self, scope: ScopeSnapshot, chunk_ids: tuple[UUID, ...]
    ) -> tuple[CitationSource, ...]:
        await self._sessions.validate_snapshot(scope)
        if len(chunk_ids) > 20 or len(set(chunk_ids)) != len(chunk_ids):
            raise ScopeError("invalid_request")
        # Bind all three IDs together; never independent version/generation lists.
        pairs = []
        parameters: dict[str, object] = {
            "app": scope.principal.app_id,
            "owner": scope.principal.user_id,
        }
        for i, pair in enumerate(scope.pairs):
            pairs.append(f"(v.document_id=:d{i} AND c.version_id=:v{i} AND c.generation_id=:g{i})")
            parameters.update(
                {f"d{i}": pair.document_id, f"v{i}": pair.version_id, f"g{i}": pair.generation_id}
            )
        if not pairs:
            raise ScopeError("session_scope_changed")
        sql = text(
            """
            SELECT c.*,v.document_id,d.filename FROM chunks c
            JOIN document_versions v ON
              (v.app_id,v.owner_id,v.version_id)=(c.app_id,c.owner_id,c.version_id)
            JOIN documents d ON
              (d.app_id,d.owner_id,d.document_id)=(v.app_id,v.owner_id,v.document_id)
            JOIN index_generations g ON
              (g.app_id,g.owner_id,g.version_id,g.generation_id)=
              (c.app_id,c.owner_id,c.version_id,c.generation_id)
            WHERE c.app_id=:app AND c.owner_id=:owner AND c.chunk_id=:chunk
              AND v.state='ready' AND g.state='ready'
              AND v.active_generation_id=c.generation_id AND (
        """
            + " OR ".join(pairs)
            + ")"
        )
        candidates = []
        names = []
        async with self._engine.connect() as conn:
            for chunk_id in chunk_ids:
                row = (
                    (await conn.execute(sql, {**parameters, "chunk": chunk_id}))
                    .mappings()
                    .one_or_none()
                )
                if row is None:
                    raise ScopeError("not_found")
                # Evidence reader revalidates checksum, source segments, owner and pairs.
                try:
                    candidate = VectorChunk(
                        document_id=row["document_id"],
                        document_version_id=row["version_id"],
                        index_generation=row["generation_id"],
                        chunk_id=row["chunk_id"],
                        ordinal=row["ordinal"],
                        language=row["language"],
                        unit_id=row["unit_id"],
                        locator=row["source_map"]["segments"][0]["locator"],
                    )
                except (KeyError, IndexError, TypeError, ValidationError):
                    raise EvidenceError("evidence_mapping_mismatch") from None
                candidates.append(candidate)
                names.append(row["filename"])
        chunks = await self._evidence.hydrate(scope, tuple(candidates))
        await self._sessions.validate_snapshot(scope)
        return tuple(CitationSource(c, name) for c, name in zip(chunks, names, strict=True))
