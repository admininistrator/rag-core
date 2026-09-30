"""Registration results and safe job state independent of transport adapters."""

from dataclasses import dataclass
from typing import Literal
from uuid import UUID

from rag_core.domain.metadata import Session

JobState = Literal[
    "queued", "fetching", "parsing", "chunking", "embedding", "indexing",
    "ready", "failed", "cancelled",
]


@dataclass(frozen=True)
class Job:
    job_id: UUID
    document_id: UUID
    version_id: UUID
    state: JobState
    progress: int
    error_code: str | None
    attempts: int
    max_attempts: int

    @property
    def retryable(self) -> bool:
        return self.state == "failed" and self.attempts < self.max_attempts


@dataclass(frozen=True)
class RegisteredUpload:
    session: Session
    document_id: UUID
    version_id: UUID
    filename: str
    link_status: Literal["attached", "detached"]
    job: Job


@dataclass(frozen=True)
class SessionDocument:
    document_id: UUID
    version_id: UUID
    filename: str
    link_status: Literal["attached", "detached"]
    job: Job
