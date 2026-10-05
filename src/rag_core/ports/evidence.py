"""Read-only session-authorized chunk hydration; no unscoped content read."""

from typing import Protocol

from rag_core.domain.chunking import Chunk
from rag_core.domain.metadata import ScopeSnapshot
from rag_core.domain.vectors import VectorChunk


class EvidenceRepository(Protocol):
    async def hydrate(
        self, scope: ScopeSnapshot, candidates: tuple[VectorChunk, ...]
    ) -> tuple[Chunk, ...]: ...
