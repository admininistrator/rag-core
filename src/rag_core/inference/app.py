"""Internal HTTP transport. No public retrieval, content cache, or model-per-worker factory."""

import asyncio
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from rag_core.adapters.models.flag import FlagModels
from rag_core.domain.models import InferenceError, InferenceRequest
from rag_core.inference.scheduler import InferenceScheduler


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
        started = time.monotonic()
        backend = await asyncio.to_thread(
            FlagModels, Path(os.environ.get("MODEL_CACHE", "/models")),
            device=os.environ.get("MODEL_DEVICE", "cpu"),
        )
        app.state.scheduler = InferenceScheduler(backend)
        try:
            app.state.load_seconds = time.monotonic() - started
            warmup = time.monotonic()
            for operation in ("embed", "rerank"):
                await app.state.scheduler.infer(uuid4(), InferenceRequest(
                    operation=operation, texts=["Hello Việt Nam."],
                    query="Việt Nam?" if operation == "rerank" else None,
                    timeout_seconds=120,
                ))
            app.state.warmup_seconds = time.monotonic() - warmup
            app.state.startup_seconds = time.monotonic() - started
            yield
        finally:
            await app.state.scheduler.close()

    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)

    @app.middleware("http")
    async def bounded_body(request: Request, call_next: Any) -> Any:
        # Count streamed bytes too: Content-Length alone is not an admission boundary.
        size = 0
        data = bytearray()
        try:
            async with asyncio.timeout(5):
                async for part in request.stream():
                    size += len(part)
                    if size > 1024 * 1024:
                        return JSONResponse({"code": "model_body_limit"}, status_code=413)
                    data.extend(part)
        except TimeoutError:
            return JSONResponse({"code": "model_body_timeout"}, status_code=408)
        request._body = bytes(data)
        return await call_next(request)

    @app.exception_handler(InferenceError)
    async def inference_error(request: Request, error: InferenceError) -> JSONResponse:
        status = {"model_busy": 429, "model_token_limit": 422, "model_cancelled": 409,
                  "duplicate_inference_id": 409, "model_timeout": 504}.get(error.code, 503)
        return JSONResponse({"code": error.code}, status_code=status)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, error: Exception) -> JSONResponse:
        return JSONResponse({"code": "invalid_model_request"}, status_code=422)

    @app.get("/health/live")
    async def live() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready")
    async def ready() -> dict[str, Any]:
        import psutil  # type: ignore[import-untyped]
        scheduler = app.state.scheduler
        return {"status": "ready", "pid": os.getpid(), "model_instances": 2,
                "inference_processes": 1, "active_jobs": len(scheduler.jobs),
                "capacity": scheduler.capacity, "fingerprint": scheduler.backend.fingerprint,
                "runtime": scheduler.backend.runtime, "device": scheduler.backend.device,
                "startup_seconds": app.state.startup_seconds,
                "load_seconds": app.state.load_seconds,
                "warmup_seconds": app.state.warmup_seconds,
                "resources": scheduler.backend.resources(),
                "rss_bytes": psutil.Process().memory_info().rss}

    @app.post("/internal/infer/{request_id}")
    async def infer(request_id: UUID, payload: InferenceRequest, request: Request) -> Any:
        scheduler = app.state.scheduler
        task = asyncio.create_task(scheduler.infer(request_id, payload))
        try:
            while not task.done():
                if await request.is_disconnected():
                    task.cancel()
                    raise InferenceError("model_cancelled")
                await asyncio.wait({task}, timeout=0.05)
            return (await task).model_dump(mode="json")
        finally:
            if not task.done():
                task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    @app.delete("/internal/infer/{request_id}", status_code=204)
    async def cancel(request_id: UUID) -> None:
        app.state.scheduler.cancel(request_id)

    return app
