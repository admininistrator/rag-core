"""Storage -> parse/OCR -> chunks -> shared model -> reconciled atomic publication."""

import asyncio
import threading
from contextlib import suppress
from uuid import UUID

from rag_core.domain.chunking import ChunkingError, StructuralChunker
from rag_core.domain.documents import ParsedDocument, ParseError, SourceIdentity
from rag_core.domain.ingestion import IngestionError, IngestionLease, chunk_manifest
from rag_core.domain.models import InferenceError, InferenceRequest
from rag_core.domain.vectors import IndexProfile, VectorChunk, VectorError, VectorWrite
from rag_core.ports.ingestion import IngestionRepository
from rag_core.ports.models import ModelInference
from rag_core.ports.parsers import DocumentParser
from rag_core.ports.storage import StorageError, StorageReader
from rag_core.ports.vectors import VectorRepository

# Transient technical failures retry through the PG outbox, never unbounded Celery retry.
_RETRYABLE = {"storage_unavailable", "model_unavailable", "model_busy", "model_timeout",
              "vector_dependency_unavailable", "ingestion_timeout"}


class IngestionPipeline:
    def __init__(
        self, repository: IngestionRepository, storage: StorageReader, parser: DocumentParser,
        chunker: StructuralChunker, inference: ModelInference, vectors: VectorRepository,
        profile: IndexProfile, *, extraction_fingerprint: str, pipeline_fingerprint: str,
        heartbeat_seconds: float = 5, timeout_seconds: float = 1800,
    ) -> None:
        if not 0.1 <= heartbeat_seconds <= 30 or not 1 <= timeout_seconds <= 3600:
            raise ValueError("invalid worker limits")
        self.repo, self.storage, self.parser = repository, storage, parser
        self.chunker, self.inference, self.vectors = chunker, inference, vectors
        self.profile = profile
        self.extraction_fingerprint = extraction_fingerprint
        self.pipeline_fingerprint = pipeline_fingerprint
        self.heartbeat_seconds, self.timeout_seconds = heartbeat_seconds, timeout_seconds

    async def run(self, job_id: UUID) -> str:
        lease = await self.repo.claim(job_id, self.profile.fingerprint, self.pipeline_fingerprint)
        if lease is None:
            return "not_claimed"
        cancel = threading.Event()
        work = asyncio.create_task(self._work(lease, cancel))
        heartbeat = asyncio.create_task(self._heartbeat(lease))
        try:
            async with asyncio.timeout(self.timeout_seconds):
                done, _ = await asyncio.wait({work, heartbeat}, return_when=asyncio.FIRST_COMPLETED)
                # Work may already have atomically published and cleared the lease.
                if work in done:
                    await work
                else:
                    await heartbeat
            return "ready"
        except (StorageError, ParseError, ChunkingError, InferenceError, VectorError,
                IngestionError) as exc:
            code = exc.code if hasattr(exc, "code") else str(exc)
            await self.repo.fail(lease, code, retryable=code in _RETRYABLE)
            return code
        except TimeoutError:
            await self.repo.fail(lease, "ingestion_timeout", retryable=True)
            return "ingestion_timeout"
        except asyncio.CancelledError:
            # Normal process shutdown leaves recovery to the expired-lease watchdog.
            raise
        except Exception:
            await self.repo.fail(lease, "ingestion_failed", retryable=False)
            return "ingestion_failed"
        finally:
            cancel.set()
            heartbeat.cancel()
            work.cancel()
            await asyncio.gather(work, heartbeat, return_exceptions=True)

    async def _heartbeat(self, lease: IngestionLease) -> None:
        while True:
            await asyncio.sleep(self.heartbeat_seconds)
            await self.repo.heartbeat(lease)

    async def _extract(self, lease: IngestionLease, cancel: threading.Event) -> ParsedDocument:
        # Context entry/download and parser are blocking; hold the file until the
        # cancelled parser has killed/reaped its children, then release storage temp.
        context = self.storage.read(lease.principal.app_id, lease.source)
        fetch = asyncio.create_task(asyncio.to_thread(context.__enter__))
        try:
            downloaded = await asyncio.shield(fetch)
        except asyncio.CancelledError:
            with suppress(Exception):
                await fetch
                await asyncio.to_thread(context.__exit__, None, None, None)
            raise
        try:
            if downloaded.sha256 != lease.source.sha256 or downloaded.size != lease.size_bytes:
                raise IngestionError("source_changed")
            await self.repo.advance(lease, "parsing", 20)
            parse = asyncio.create_task(asyncio.to_thread(
                self.parser.parse, downloaded.path, filename=lease.filename,
                content_type=lease.content_type, source=SourceIdentity(
                    document_id=lease.scope.pair.document_id, version_id=lease.scope.pair.version_id,
                    sha256=downloaded.sha256), cancel=cancel,
            ))
            try:
                return await asyncio.shield(parse)
            except asyncio.CancelledError:
                cancel.set()
                with suppress(Exception):
                    await parse
                raise
        finally:
            await asyncio.to_thread(context.__exit__, None, None, None)

    async def _work(self, lease: IngestionLease, cancel: threading.Event) -> None:
        from rag_core.domain.ingestion import vector_unit_id

        parsed = await self._extract(lease, cancel)
        await self.repo.advance(lease, "chunking", 40)
        chunks = await asyncio.to_thread(self.chunker.chunk, parsed,
            generation_id=lease.scope.pair.generation_id,
            extraction_fingerprint=self.extraction_fingerprint)
        await self.repo.stage_chunks(lease, chunks)
        await self.repo.advance(lease, "embedding", 55)
        for offset in range(0, len(chunks), 32):
            await self.repo.heartbeat(lease)
            batch = chunks[offset:offset+32]
            result = await self.inference.infer(InferenceRequest(
                operation="embed", priority="index", texts=[c.text for c in batch],
                timeout_seconds=120.0,
            ))
            if result.fingerprint != self.profile.model_fingerprint or len(result.embeddings) != len(batch):
                raise IngestionError("model_revision_mismatch")
            points = tuple(VectorWrite(VectorChunk(
                document_id=c.source.document_id, document_version_id=c.source.version_id,
                index_generation=c.generation_id, chunk_id=c.id, language="und",
                ordinal=c.ordinal, unit_id=vector_unit_id(c), locator=c.segments[0].locator,
            ), embedding) for c, embedding in zip(batch, result.embeddings, strict=True))
            # Progress stays indexing while later batches alternate embedding and writes.
            await self.repo.advance(lease, "indexing", 80 + int(15 * offset / len(chunks)))
            await self.vectors.upsert(lease.scope, points, result.fingerprint)
            await self.vectors.verify_generation(lease.scope, points)
        if await self.vectors.count_generation(lease.scope) != len(chunks):
            raise IngestionError("ingestion_vector_count_mismatch")
        await self.repo.publish(lease, len(chunks), chunk_manifest(chunks),
                                self.extraction_fingerprint)
