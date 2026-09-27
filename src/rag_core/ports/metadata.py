"""Current-session metadata interface for future API/retrieval consumers."""

from typing import Protocol
from uuid import UUID

from rag_core.auth import Principal
from rag_core.domain.metadata import ScopeSnapshot, Session


class SessionRepository(Protocol):
    async def create_session(self, principal: Principal, external_session_id: str) -> Session: ...

    async def get_session(self, principal: Principal, session_id: UUID) -> Session: ...

    async def delete_session(self, principal: Principal, session_id: UUID) -> Session: ...

    async def detach_document(
        self, principal: Principal, session_id: UUID, document_id: UUID
    ) -> Session: ...

    async def resolve_scope(
        self,
        principal: Principal,
        session_id: UUID,
        document_ids: tuple[UUID, ...] | None = None,
    ) -> ScopeSnapshot: ...

    async def validate_snapshot(self, snapshot: ScopeSnapshot) -> None: ...
