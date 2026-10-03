"""Scoped vector repository contract; raw SDK/filter/collection access is not exposed."""

from contextlib import AbstractAsyncContextManager
from typing import Protocol
from uuid import UUID

from rag_core.domain.metadata import ScopeSnapshot
from rag_core.domain.models import Embedding
from rag_core.domain.vectors import (
    GenerationOperation,
    GenerationScope,
    SearchBranch,
    VectorHit,
    VectorWrite,
)


class GenerationAuthority(Protocol):
    def access(
        self, scope: GenerationScope, index_fingerprint: str, operation: GenerationOperation
    ) -> AbstractAsyncContextManager[None]: ...


class VectorRepository(Protocol):
    async def ensure_collection(self) -> None: ...

    async def upsert(
        self, scope: GenerationScope, points: tuple[VectorWrite, ...], model_fingerprint: str
    ) -> None: ...

    async def search(
        self,
        scope: ScopeSnapshot,
        query: Embedding,
        model_fingerprint: str,
        *,
        branch: SearchBranch = "hybrid",
        limit: int = 30,
        languages: tuple[str, ...] | None = None,
    ) -> tuple[VectorHit, ...]: ...

    async def fetch(
        self,
        scope: ScopeSnapshot,
        chunk_ids: tuple[UUID, ...],
        *,
        languages: tuple[str, ...] | None = None,
    ) -> tuple[VectorHit, ...]: ...

    async def fetch_neighbors(
        self,
        scope: ScopeSnapshot,
        anchor_id: UUID,
        *,
        radius: int = 1,
        languages: tuple[str, ...] | None = None,
    ) -> tuple[VectorHit, ...]: ...

    async def count_generation(self, scope: GenerationScope) -> int: ...

    async def cleanup_generation(self, scope: GenerationScope) -> None: ...
