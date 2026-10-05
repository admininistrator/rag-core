"""Bounded owner/exact-pair chunk SQL, with authoritative session revalidation."""

import hashlib

from pydantic import TypeAdapter, ValidationError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from rag_core.domain.chunking import Chunk
from rag_core.domain.evidence import EvidenceError
from rag_core.domain.ingestion import vector_unit_id
from rag_core.domain.metadata import ScopeError, ScopeSnapshot
from rag_core.domain.vectors import VectorChunk
from rag_core.ports.metadata import SessionRepository

_CHUNK = TypeAdapter(Chunk)


class PostgresEvidenceRepository:
    def __init__(self, engine: AsyncEngine, sessions: SessionRepository) -> None:
        self._engine = engine
        self._sessions = sessions

    async def hydrate(
        self, scope: ScopeSnapshot, candidates: tuple[VectorChunk, ...]
    ) -> tuple[Chunk, ...]:
        await self._sessions.validate_snapshot(scope)
        if len(candidates) > 20 or len({c.chunk_id for c in candidates}) != len(candidates):
            raise EvidenceError("invalid_evidence_candidates")
        if any(c.pair not in scope.pairs for c in candidates):
            raise ScopeError("session_scope_changed")
        output = []
        # At most 20 indexed point reads. Never query a whole document/library.
        async with self._engine.connect() as conn:
            for candidate in candidates:
                row = (
                    (
                        await conn.execute(
                            text("""
                    SELECT c.*, v.document_id,v.source_sha256
                    FROM chunks c JOIN document_versions v ON
                        (v.app_id,v.owner_id,v.version_id)=(c.app_id,c.owner_id,c.version_id)
                    JOIN index_generations g ON
                        (g.app_id,g.owner_id,g.version_id,g.generation_id)=
                        (c.app_id,c.owner_id,c.version_id,c.generation_id)
                    WHERE c.app_id=:app AND c.owner_id=:owner AND c.chunk_id=:chunk
                        AND v.document_id=:document AND c.version_id=:version
                        AND c.generation_id=:generation AND v.active_generation_id=c.generation_id
                        AND v.state='ready' AND g.state='ready'
                """),
                            {
                                "app": scope.principal.app_id,
                                "owner": scope.principal.user_id,
                                "chunk": candidate.chunk_id,
                                "document": candidate.document_id,
                                "version": candidate.document_version_id,
                                "generation": candidate.index_generation,
                            },
                        )
                    )
                    .mappings()
                    .one_or_none()
                )
                if row is None:
                    raise EvidenceError("evidence_chunk_missing")
                try:
                    chunk = _CHUNK.validate_python({**row["source_map"], "text": row["text"]})
                except (ValidationError, TypeError, ValueError):
                    raise EvidenceError("evidence_mapping_mismatch") from None
                if (
                    not chunk.segments
                    or chunk.id != candidate.chunk_id
                    or chunk.source.document_id != candidate.document_id
                    or chunk.source.version_id != candidate.document_version_id
                    or chunk.source.sha256 != row["source_sha256"]
                    or chunk.generation_id != candidate.index_generation
                    or chunk.ordinal != candidate.ordinal
                    or chunk.ordinal != row["ordinal"]
                    or vector_unit_id(chunk) != candidate.unit_id
                    or row["unit_id"] != candidate.unit_id
                    or row["language"] != candidate.language
                    or chunk.checksum != row["checksum"]
                    or hashlib.sha256(chunk.text.encode()).hexdigest() != chunk.checksum
                    or chunk.token_count != row["token_count"]
                    or not 1 <= chunk.token_count <= 512
                    or len(chunk.text) > 32768
                    or chunk.segments[0].locator != candidate.locator
                    or any(
                        not 0 <= s.start < s.end <= len(chunk.text)
                        or s.source_start < 0
                        or s.source_end - s.source_start != s.end - s.start
                        for s in chunk.segments
                    )
                ):
                    raise EvidenceError("evidence_mapping_mismatch")
                output.append(chunk)
        await self._sessions.validate_snapshot(scope)
        return tuple(output)
