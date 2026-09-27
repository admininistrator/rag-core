"""Metadata and exact authorization snapshots, without database/framework imports."""

from dataclasses import dataclass
from typing import Literal
from uuid import UUID

from rag_core.auth import Principal

SessionStatus = Literal["active", "deleted"]
ScopeCode = Literal[
    "not_found",
    "session_deleted",
    "no_session_documents",
    "documents_not_ready",
    "session_scope_changed",
    "invalid_request",
    "idempotency_conflict",
]


class ScopeError(Exception):
    """Safe business error; never includes source identifiers or database details."""

    def __init__(self, code: ScopeCode) -> None:
        self.code = code
        self.status_code = {
            "not_found": 404,
            "session_deleted": 410,
            "invalid_request": 422,
        }.get(code, 409)
        super().__init__(code)


@dataclass(frozen=True)
class Session:
    session_id: UUID
    external_session_id: str
    status: SessionStatus
    scope_revision: int


@dataclass(frozen=True)
class VersionGeneration:
    document_id: UUID
    version_id: UUID
    generation_id: UUID


@dataclass(frozen=True)
class ScopeSnapshot:
    principal: Principal
    session_id: UUID
    scope_revision: int
    requested_document_ids: tuple[UUID, ...] | None
    pairs: tuple[VersionGeneration, ...]
