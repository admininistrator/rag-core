"""Opt-in POST SSE router; T26 owns production composition and business route mounting."""

import asyncio
from contextlib import aclosing, suppress
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse, Response
from starlette.types import Receive, Scope, Send

from rag_core.api.auth import require_principal
from rag_core.application.admission import QueryAdmission, QueryBusy
from rag_core.application.streaming import ScopedAnswerStream, StreamingAnswerPipeline
from rag_core.auth import Principal
from rag_core.contracts.sse import ErrorEvent, MetaEvent, SSEEvent
from rag_core.contracts.v1 import ErrorEnvelope, QueryRequest
from rag_core.domain.answers import AnswerError
from rag_core.domain.llm import LlmError
from rag_core.domain.metadata import ScopeError
from rag_core.domain.streaming import StreamPolicy


class SlowClientError(Exception):
    """A blocked send ends as incomplete; attempting another terminal is unsafe."""


def stream_error(exc: Exception, request_id: UUID) -> tuple[int, ErrorEnvelope]:
    """Only code-based mappings; no exception text, provider body, query or credentials."""
    code: str
    if isinstance(exc, ScopeError):
        code, status, retryable = exc.code, exc.status_code, False
    elif isinstance(exc, QueryBusy):
        code, status, retryable = "busy", 429, True
    elif isinstance(exc, TimeoutError) or (
        isinstance(exc, LlmError) and exc.code in {"provider_timeout", "llm_timeout"}
    ):
        code, status, retryable = "timeout", 504, True
    elif isinstance(exc, LlmError):
        code, status, retryable = "provider_error", 502, exc.retryable
    elif isinstance(exc, AnswerError) and exc.code == "invalid_citation":
        code, status, retryable = "invalid_citation", 502, False
    else:
        code, status, retryable = "dependency_unavailable", 503, True
    messages = {
        "busy": "Query capacity is busy.",
        "timeout": "The query timed out.",
        "provider_error": "The generation provider failed.",
        "invalid_citation": "The generated answer did not reference valid evidence.",
        "dependency_unavailable": "A query dependency is unavailable.",
    }
    envelope = ErrorEnvelope.model_validate(
        {
            "request_id": request_id,
            "error": {
                "code": code,
                "message": messages.get(code, "The session scope is unavailable."),
                "retryable": retryable,
                "details": [],
            },
        }
    )
    return status, envelope


def encode_event(event: SSEEvent) -> bytes:
    return (
        f"id: {event.id}\nevent: {event.event}\ndata: {event.data.model_dump_json()}\n\n"
    ).encode()


class QueryStreamResponse(Response):
    media_type = "text/event-stream"

    def __init__(
        self,
        stream: ScopedAnswerStream,
        admission: QueryAdmission,
        policy: StreamPolicy,
    ) -> None:
        super().__init__(headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"})
        # Response base sets content-length=0; an SSE response has no fixed length.
        self.raw_headers = [
            (key, value) for key, value in self.raw_headers if key != b"content-length"
        ]
        self.stream = stream
        self.admission = admission
        self.policy = policy

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        async def disconnect() -> None:
            while (await receive())["type"] != "http.disconnect":
                pass

        worker = asyncio.create_task(self._run(scope, receive, send))
        watcher = asyncio.create_task(disconnect())
        try:
            completed, _ = await asyncio.wait(
                {worker, watcher}, return_when=asyncio.FIRST_COMPLETED
            )
            if worker in completed:
                await worker
        finally:
            worker.cancel()
            watcher.cancel()
            await asyncio.gather(worker, watcher, return_exceptions=True)

    async def _run(self, scope: Scope, receive: Receive, send: Send) -> None:
        lease = None
        producer: asyncio.Task[None] | None = None
        cleanup: asyncio.Task[None] | None = None
        started = False
        last_id = 0
        terminal = False
        queue: asyncio.Queue[SSEEvent | Exception] = asyncio.Queue(self.policy.buffer_events)

        async def produce() -> None:
            try:
                async with aclosing(self.stream.events()) as events:
                    async for event in events:
                        await queue.put(event)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                await queue.put(exc)

        async def write(body: bytes, *, more: bool = True) -> None:
            try:
                await asyncio.wait_for(
                    send({"type": "http.response.body", "body": body, "more_body": more}),
                    self.policy.send_timeout,
                )
            except TimeoutError:
                raise SlowClientError from None

        async def stop_producer() -> None:
            nonlocal producer, cleanup
            if producer is not None:
                task, producer = producer, None
                task.cancel()

                async def join() -> None:
                    await asyncio.gather(task, return_exceptions=True)

                cleanup = asyncio.create_task(join())
            if cleanup is not None:
                # A disconnect racing a terminal must not cancel upstream cleanup again.
                await asyncio.shield(cleanup)

        async def fail(exc: Exception) -> None:
            nonlocal terminal
            if terminal:
                return
            terminal = True
            # Finish upstream cleanup before final HTTP body makes Uvicorn report disconnect.
            await stop_producer()
            status, envelope = stream_error(exc, self.stream.request_id)
            if not started:
                response = JSONResponse(
                    status_code=status,
                    content=envelope.model_dump(mode="json"),
                    headers={
                        "Cache-Control": "no-store",
                        **({"Retry-After": "1"} if status == 429 else {}),
                    },
                )
                await asyncio.wait_for(response(scope, receive, send), self.policy.send_timeout)
            else:
                event = ErrorEvent(event="error", id=last_id + 1, data=envelope)
                await write(encode_event(event))
                await write(b"", more=False)

        try:
            async with asyncio.timeout(self.policy.total_timeout):
                lease = await self.admission.acquire()
                producer = asyncio.create_task(produce())
                # Preparation/auth scope errors retain their HTTP status before SSE headers.
                item = await queue.get()
                if isinstance(item, Exception):
                    await fail(item)
                    return
                if not isinstance(item, MetaEvent):
                    raise RuntimeError("invalid_stream_start")
                await self.stream.validate_scope()
                await asyncio.wait_for(
                    send(
                        {
                            "type": "http.response.start",
                            "status": 200,
                            "headers": self.raw_headers,
                        }
                    ),
                    self.policy.send_timeout,
                )
                started = True
                while True:
                    if isinstance(item, Exception):
                        await fail(item)
                        return
                    # Revalidate at the send boundary: queued events may now be stale.
                    await self.stream.validate_scope()
                    last_id += 1
                    item = item.model_copy(update={"id": last_id})
                    if item.event in {"done", "error"}:
                        terminal = True
                        await stop_producer()
                    await write(encode_event(item))
                    if terminal:
                        await write(b"", more=False)
                        return
                    while True:
                        try:
                            item = await asyncio.wait_for(
                                queue.get(), self.policy.heartbeat_seconds
                            )
                            break
                        except TimeoutError:
                            # Detect detach/delete even while upstream is idle.
                            await self.stream.validate_scope()
                            await write(b": keep-alive\n\n")
        except SlowClientError:
            return
        except TimeoutError as exc:
            with suppress(OSError, TimeoutError, SlowClientError):
                await fail(exc)
        except (OSError, asyncio.CancelledError):
            raise
        except Exception as exc:
            # A blocked send may leave incomplete bytes; never attempt a second terminal.
            with suppress(OSError, TimeoutError, SlowClientError):
                await fail(exc)
        finally:
            await stop_producer()
            if lease is not None:
                lease.release()


def build_stream_router(
    pipeline: StreamingAnswerPipeline,
    admission: QueryAdmission,
    policy: StreamPolicy | None = None,
) -> APIRouter:
    """Caller must mount behind T09 AuthenticationMiddleware; Principal remains required."""
    resolved = StreamPolicy.model_validate((policy or pipeline.policy).model_dump())
    router = APIRouter()

    @router.post(
        "/v1/query/stream",
        response_class=Response,
        responses={200: {"content": {"text/event-stream": {}}}},
    )
    async def query_stream(
        query: QueryRequest,
        principal: Annotated[Principal, Depends(require_principal)],
    ) -> Response:
        return QueryStreamResponse(pipeline.query(principal, query, uuid4()), admission, resolved)

    return router
