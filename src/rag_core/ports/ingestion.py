"""Durable worker persistence boundary; no SQL/Celery dependencies."""

from typing import Protocol
from uuid import UUID

from rag_core.domain.chunking import Chunk
from rag_core.domain.ingestion import IngestionLease


class IngestionRepository(Protocol):
    async def claim(
        self, job_id: UUID, index_fingerprint: str, pipeline_fingerprint: str
    ) -> IngestionLease | None: ...

    async def heartbeat(self, lease: IngestionLease) -> None: ...

    async def advance(self, lease: IngestionLease, state: str, progress: int) -> None: ...

    async def stage_chunks(self, lease: IngestionLease, chunks: tuple[Chunk, ...]) -> None: ...

    async def publish(
        self, lease: IngestionLease, expected_count: int, expected_manifest: str,
        extraction_fingerprint: str,
    ) -> None: ...

    async def fail(self, lease: IngestionLease, code: str, *, retryable: bool) -> None: ...
