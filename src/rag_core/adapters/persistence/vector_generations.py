"""PG owns vector write/cleanup authority; locks serialize with generation publication."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from rag_core.domain.vectors import GenerationOperation, GenerationScope, VectorError


class PostgresGenerationAuthority:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    @asynccontextmanager
    async def access(
        self, scope: GenerationScope, index_fingerprint: str, operation: GenerationOperation
    ) -> AsyncIterator[None]:
        if operation not in {"write", "count", "cleanup"}:
            raise VectorError("invalid_generation_operation")
        async with self._engine.begin() as conn:
            row = (
                (
                    await conn.execute(
                        text("""
                SELECT g.state, g.index_fingerprint, v.active_generation_id
                FROM document_versions v JOIN index_generations g
                    ON g.app_id=v.app_id AND g.owner_id=v.owner_id AND g.version_id=v.version_id
                WHERE v.app_id=:app AND v.owner_id=:owner AND v.document_id=:doc
                    AND v.version_id=:version AND g.generation_id=:generation
                FOR UPDATE OF v, g
            """),
                        {
                            "app": scope.principal.app_id,
                            "owner": scope.principal.user_id,
                            "doc": scope.pair.document_id,
                            "version": scope.pair.version_id,
                            "generation": scope.pair.generation_id,
                        },
                    )
                )
                .mappings()
                .first()
            )
            if row is None or row["index_fingerprint"] != index_fingerprint:
                raise VectorError("generation_not_authorized")
            if operation != "count" and row["active_generation_id"] == scope.pair.generation_id:
                raise VectorError("active_generation_immutable")
            if operation == "write" and row["state"] != "staging":
                raise VectorError("generation_not_staging")
            # Retain these locks through the bounded Qdrant wait=true acknowledgement.
            # T19 publication UPDATE of v/g necessarily waits on the same rows.
            yield
