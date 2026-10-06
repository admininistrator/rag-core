"""Stateless current-session chunk resolution, without public object URLs or caches."""

from uuid import UUID

from rag_core.auth import Principal
from rag_core.contracts.v1 import CitationResolveResponse
from rag_core.domain.answers import source_citations
from rag_core.ports.citations import CitationRepository
from rag_core.ports.metadata import SessionRepository


class CitationResolver:
    def __init__(self, repository: CitationRepository, sessions: SessionRepository) -> None:
        self._repository = repository
        self._sessions = sessions

    async def resolve(
        self,
        principal: Principal,
        session_id: UUID,
        chunk_id: UUID,
        request_id: UUID,
        *,
        document_ids: tuple[UUID, ...] | None = None,
    ) -> CitationResolveResponse:
        scope = await self._sessions.resolve_scope(principal, session_id, document_ids)
        sources = await self._repository.load(scope, (chunk_id,))
        citation = source_citations(sources[0])[0]
        response = CitationResolveResponse(
            request_id=request_id,
            session_id=session_id,
            scope_revision=scope.scope_revision,
            citation=citation,
        )
        await self._sessions.validate_snapshot(scope)
        return response
