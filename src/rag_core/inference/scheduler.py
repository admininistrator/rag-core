"""One executor slot; bounded query-priority queues and cooperative batch cancellation."""

import asyncio
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from uuid import UUID

from rag_core.domain.models import Embedding, InferenceError, InferenceRequest, InferenceResult
from rag_core.ports.models import ModelBackend


@dataclass
class Job:
    request: InferenceRequest
    future: asyncio.Future[InferenceResult]
    deadline: float
    cancelled: bool = False
    offset: int = 0
    embeddings: list[Embedding] = field(default_factory=list)
    scores: list[float] = field(default_factory=list)


class InferenceScheduler:
    def __init__(self, backend: ModelBackend, *, capacity: int = 32, index_capacity: int = 24) -> None:
        if not 0 < index_capacity < capacity <= 128:
            raise ValueError("invalid_inference_capacity")
        self.backend = backend
        self.capacity = capacity
        self.index_capacity = index_capacity
        self.jobs: dict[UUID, Job] = {}
        self.queues: dict[str, deque[UUID]] = {"query": deque(), "index": deque()}
        self.wakeup = asyncio.Event()
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="shared-inference")
        self.closed = False
        self.runner = asyncio.create_task(self._run())

    def cancel(self, request_id: UUID) -> None:
        if job := self.jobs.get(request_id):
            job.cancelled = True
            if not job.future.done():
                job.future.set_exception(InferenceError("model_cancelled"))
            for queue in self.queues.values():
                if request_id in queue:
                    queue.remove(request_id)
                    self.jobs.pop(request_id)
                    break

    async def infer(self, request_id: UUID, request: InferenceRequest) -> InferenceResult:
        if self.closed:
            raise InferenceError("model_unavailable")
        if request_id in self.jobs:
            raise InferenceError("duplicate_inference_id")
        if len(self.jobs) >= self.capacity or (request.priority == "index"
            and sum(j.request.priority == "index" for j in self.jobs.values()) >= self.index_capacity):
            raise InferenceError("model_busy")
        future: asyncio.Future[InferenceResult] = asyncio.get_running_loop().create_future()
        self.jobs[request_id] = Job(request, future, time.monotonic() + request.timeout_seconds)
        self.queues[request.priority].append(request_id)
        self.wakeup.set()
        try:
            return await asyncio.wait_for(asyncio.shield(future), request.timeout_seconds)
        except TimeoutError as exc:
            self.cancel(request_id)
            raise InferenceError("model_timeout") from exc
        except asyncio.CancelledError:
            self.cancel(request_id)
            raise
        finally:
            # Consume late cancellation/error; never release a running native slot early.
            if future.done() and not future.cancelled():
                future.exception()

    async def _run(self) -> None:
        while not self.closed:
            await self.wakeup.wait()
            queue = self.queues["query"] or self.queues["index"]
            if not queue:
                self.wakeup.clear()
                continue
            request_id = queue.popleft()
            job = self.jobs[request_id]
            try:
                # At most two texts per nonpreemptible native call, matching model batch_size.
                if job.cancelled:
                    raise InferenceError("model_cancelled")
                if time.monotonic() >= job.deadline:
                    raise InferenceError("model_timeout")
                batch = job.request.model_copy(update={"texts": job.request.texts[job.offset:job.offset+2]})
                result = await asyncio.get_running_loop().run_in_executor(
                    self.executor, self.backend.infer, batch,
                )
                job.embeddings.extend(result.embeddings)
                job.scores.extend(result.scores)
                job.offset += len(batch.texts)
                if job.cancelled:
                    raise InferenceError("model_cancelled")
                if time.monotonic() >= job.deadline:
                    raise InferenceError("model_timeout")
                if job.offset < len(job.request.texts):
                    # Reconsider priority between batches; indexing cannot monopolize a request.
                    self.queues[job.request.priority].append(request_id)
                    continue
                if not job.future.done():
                    job.future.set_result(InferenceResult(fingerprint=self.backend.fingerprint,
                                                         embeddings=tuple(job.embeddings),
                                                         scores=tuple(job.scores)))
            except Exception as exc:
                error = exc if isinstance(exc, InferenceError) else InferenceError("model_failed")
                if not job.future.done():
                    job.future.set_exception(error)
            finally:
                if request_id not in self.queues[job.request.priority]:
                    self.jobs.pop(request_id, None)

    async def close(self) -> None:
        self.closed = True
        for request_id in list(self.jobs):
            self.cancel(request_id)
        self.wakeup.set()
        await self.runner
        self.executor.shutdown(wait=True)
