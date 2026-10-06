"""Code-only public errors, including validation failures without raw input values."""

from collections.abc import Callable, Coroutine
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse, Response

from rag_core.adapters.persistence.registrations import RegistrationError
from rag_core.api.streaming import stream_error
from rag_core.contracts.v1 import ErrorEnvelope
from rag_core.domain.llm import LlmError
from rag_core.domain.query import QueryPreparationError
from rag_core.ports.storage import StorageError


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def safe_error(_request: Request, exc: Exception) -> JSONResponse:
        request_id = uuid4()
        if isinstance(exc, QueryPreparationError) and "rewrite" in exc.code:
            exc = LlmError("llm_timeout" if "timeout" in exc.code else "llm_invalid_rewrite")
        if isinstance(exc, RegistrationError):
            status, code, retryable = exc.status_code, exc.code, False
        elif isinstance(exc, StorageError):
            status, code, retryable = {
                "storage_forbidden": (404, "not_found", False),
                "storage_not_found": (404, "not_found", False),
                "source_changed": (409, "source_changed", False),
                "source_too_large": (422, "file_too_large", False),
                "source_unpinned": (422, "invalid_request", False),
                "invalid_source": (422, "invalid_request", False),
            }.get(exc.code, (503, "dependency_unavailable", True))
        elif isinstance(exc, RequestValidationError):
            status, code, retryable = 422, "invalid_request", False
        elif isinstance(exc, HTTPException):
            status, code, retryable = exc.status_code, "not_found", False
        else:
            status, envelope = stream_error(exc, request_id)
            return JSONResponse(
                status_code=status,
                content=envelope.model_dump(mode="json"),
                headers={
                    "Cache-Control": "no-store",
                    **({"Retry-After": "1"} if status == 429 else {}),
                },
            )
        envelope = ErrorEnvelope.model_validate(
            {
                "request_id": request_id,
                "error": {
                    "code": code,
                    "message": "The requested operation could not be completed.",
                    "retryable": retryable,
                    "details": [],
                },
            }
        )
        return JSONResponse(
            status_code=status,
            content=envelope.model_dump(mode="json"),
            headers={"Cache-Control": "no-store"},
        )

    app.add_exception_handler(RequestValidationError, safe_error)
    app.add_exception_handler(HTTPException, safe_error)
    app.state.public_error_handler = safe_error


class SafeApiRoute(APIRoute):
    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        handler = super().get_route_handler()

        async def guarded(request: Request) -> Response:
            try:
                return await handler(request)
            except Exception as exc:
                # Handle here so ServerErrorMiddleware cannot log private adapter tracebacks.
                response: Response = await request.app.state.public_error_handler(request, exc)
                return response

        return guarded
