"""Bounded, read-only source lookup under an authenticated current session snapshot."""

from typing import Protocol
from uuid import UUID

from rag_core.domain.answers import CitationSource
from rag_core.domain.metadata import ScopeSnapshot


class CitationRepository(Protocol):
    async def load(
        self, scope: ScopeSnapshot, chunk_ids: tuple[UUID, ...]
    ) -> tuple[CitationSource, ...]: ...
