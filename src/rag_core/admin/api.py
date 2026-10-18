"""Cookie-only metadata administration API; no browser UI or content viewer."""

import asyncio
import hmac
import json
from collections.abc import AsyncIterator, Callable, Coroutine
from typing import Annotated, Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from pydantic import BaseModel, ConfigDict, Field, SecretStr, ValidationError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse, Response

from rag_core.adapters.persistence.admin import audited_action, metadata_page, overview
from rag_core.adapters.persistence.registrations import RegistrationError
from rag_core.admin.auth import (
    COOKIE,
    COOKIE_PATH,
    AdminAuthentication,
    AdminError,
    audit,
    csrf_token,
    digest,
)
from rag_core.domain.ingestion import IngestionError


def error_response(code: str, status: int, request_id: UUID) -> JSONResponse:
    return JSONResponse(
        {
            "request_id": str(request_id),
            "error": {
                "code": code,
                "message": "The administration request could not be completed.",
                "retryable": status in {429, 503},
                "details": [],
            },
        },
        status_code=status,
        headers={"Retry-After": "60"} if status == 429 else {},
    )


class AdminRoute(APIRoute):
    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        handler = super().get_route_handler()

        async def guarded(request: Request) -> Response:
            request.state.admin_request_id = uuid4()
            try:
                response = await handler(request)
            except AdminError as exc:
                response = error_response(exc.code, exc.status, request.state.admin_request_id)
            except (RequestValidationError, ValidationError, json.JSONDecodeError):
                response = error_response("invalid_request", 422, request.state.admin_request_id)
            except HTTPException as exc:
                response = error_response(
                    "not_found", exc.status_code, request.state.admin_request_id
                )
            except Exception:
                # Do not propagate DB/adapter exceptions to Uvicorn traceback logs.
                response = error_response(
                    "dependency_unavailable", 503, request.state.admin_request_id
                )
            response.headers.update(
                {
                    "Cache-Control": "no-store",
                    "X-Content-Type-Options": "nosniff",
                    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
                    "X-Request-ID": str(request.state.admin_request_id),
                }
            )
            return response

        return guarded


def authentication(request: Request) -> AdminAuthentication:
    auth = getattr(request.app.state, "admin_authentication", None)
    if not isinstance(auth, AdminAuthentication):
        raise AdminError("dependency_unavailable", 503)
    return auth


def cookie(request: Request) -> str | None:
    # Reject duplicate cookies instead of accepting framework last-value behavior.
    values = [
        part.strip().split("=", 1)[1]
        for header in request.headers.getlist("cookie")
        for part in header.split(";")
        if part.strip().startswith(COOKIE + "=")
    ]
    return values[0] if len(values) == 1 else None


def same_origin(request: Request, auth: AdminAuthentication) -> bool:
    return request.headers.getlist("origin") == [
        auth.services.config.origin
    ] and request.headers.get("sec-fetch-site") not in {"cross-site"}


async def protected(request: Request) -> AsyncIterator[AsyncConnection]:
    auth = authentication(request)
    failure = None
    async with auth.services.engine.begin() as conn:
        token = cookie(request)
        try:
            expected = await auth.require(conn, token)
        except AdminError:
            if request.headers.get("authorization") or request.headers.get("x-rag-service-key"):
                raise AdminError("admin_required", 403) from None
            raise
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            headers = request.headers.getlist("x-csrf-token")
            if (
                not same_origin(request, auth)
                or len(headers) != 1
                or len(headers[0]) != 64
                or not hmac.compare_digest(digest(headers[0]), expected)
            ):
                await audit(conn, "csrf_rejected", request.state.admin_request_id, outcome="denied")
                failure = AdminError("csrf_failed", 403)
        if failure is None:
            yield conn
    if failure is not None:
        raise failure


Connection = Annotated[AsyncConnection, Depends(protected, scope="function")]


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    username: str = Field(min_length=1, max_length=128)
    password: SecretStr = Field(min_length=1, max_length=1024)


async def login_body(request: Request) -> LoginRequest:
    if request.headers.get("content-type", "").split(";")[0] != "application/json":
        raise AdminError("invalid_request", 422)
    body = bytearray()
    try:
        async with asyncio.timeout(5):
            async for chunk in request.stream():
                if len(body) + len(chunk) > 8192:
                    raise AdminError("invalid_request", 413)
                body.extend(chunk)
    except TimeoutError:
        raise AdminError("request_timeout", 408) from None
    return LoginRequest.model_validate_json(body)


def build_admin_router() -> APIRouter:
    router = APIRouter(prefix="/v1/admin", tags=["admin"], route_class=AdminRoute)

    @router.post("/auth/login")
    async def login(request: Request) -> Response:
        auth = authentication(request)
        if not same_origin(request, auth):
            raise AdminError("csrf_failed", 403)
        body = await login_body(request)
        token = await auth.login(
            body.username,
            body.password.get_secret_value(),
            request.state.admin_request_id,
            cookie(request),
        )
        response = JSONResponse(
            {
                "role": "admin",
                "csrf_token": csrf_token(token),
                "expires_in": auth.services.config.session_seconds,
            }
        )
        response.set_cookie(
            COOKIE,
            token,
            max_age=auth.services.config.session_seconds,
            path=COOKIE_PATH,
            secure=auth.services.config.secure_cookie,
            httponly=True,
            samesite="strict",
        )
        return response

    @router.get("/auth/session")
    async def current(request: Request, conn: Connection) -> dict[str, Any]:
        return {"role": "admin", "csrf_token": csrf_token(cookie(request) or "")}

    @router.post("/auth/logout")
    async def logout(request: Request, conn: Connection) -> Response:
        await conn.execute(
            text("UPDATE admin_sessions SET revoked_at=now() WHERE token_hash=:token"),
            {"token": digest(cookie(request) or "")},
        )
        await audit(conn, "logout", request.state.admin_request_id)
        response = Response(status_code=204)
        response.delete_cookie(
            COOKIE,
            path=COOKIE_PATH,
            secure=authentication(request).services.config.secure_cookie,
            httponly=True,
            samesite="strict",
        )
        return response

    @router.get("/overview")
    async def summary(request: Request, conn: Connection) -> dict[str, Any]:
        data = await overview(conn)
        report = await request.app.state.admin_health_checks.readiness()
        data["health"] = report.as_dict()
        # Outbox is the durable backlog; broker queue/resources require T32 instrumentation.
        data["broker_queue_depth"] = None
        data["vector_bytes"] = None
        return data

    @router.get("/sessions/{session_id}/documents")
    async def links(
        session_id: UUID,
        conn: Connection,
        cursor: UUID | None = None,
        limit: int = Query(default=50, ge=1, le=100),
    ) -> dict[str, Any]:
        exists = (
            await conn.execute(
                text("SELECT 1 FROM sessions WHERE session_id=:session"), {"session": session_id}
            )
        ).scalar_one_or_none()
        if exists is None:
            raise AdminError("not_found", 404)
        rows = (
            (
                await conn.execute(
                    text("""
            SELECT link_id,document_id,version_id,status,attached_at,detached_at
            FROM session_documents WHERE session_id=:session
                AND (CAST(:cursor AS uuid) IS NULL OR link_id>:cursor)
            ORDER BY link_id LIMIT :limit
        """),
                    {"session": session_id, "cursor": cursor, "limit": limit + 1},
                )
            )
            .mappings()
            .all()
        )
        from rag_core.adapters.persistence.admin import safe_value

        return {
            "items": [{k: safe_value(k, v) for k, v in r.items()} for r in rows[:limit]],
            "next_cursor": str(rows[limit - 1]["link_id"]) if len(rows) > limit else None,
        }

    async def action_response(
        request: Request,
        conn: AsyncConnection,
        action: str,
        target: UUID,
        document_id: UUID | None = None,
    ) -> Response:
        try:
            async with conn.begin_nested():
                await audited_action(
                    conn,
                    request.state.admin_request_id,
                    action,
                    target,
                    authentication(request).services.engine,
                    document_id,
                )
        except (AdminError, RegistrationError, IngestionError) as exc:
            await audit(
                conn,
                action,
                request.state.admin_request_id,
                target=target,
                related=document_id,
                outcome="denied",
            )
            status = exc.status if isinstance(exc, AdminError) else 409
            return error_response(
                "not_found" if status == 404 else "invalid_transition",
                status,
                request.state.admin_request_id,
            )
        return JSONResponse(
            {"request_id": str(request.state.admin_request_id), "status": "accepted"}
        )

    @router.post("/jobs/{job_id}/{operation}")
    async def job_operation(
        job_id: UUID, operation: str, request: Request, conn: Connection
    ) -> Response:
        if operation not in {"retry", "cancel", "reindex"}:
            raise AdminError("not_found", 404)
        return await action_response(request, conn, "job_" + operation, job_id)

    @router.delete("/sessions/{session_id}")
    async def tombstone(session_id: UUID, request: Request, conn: Connection) -> Response:
        return await action_response(request, conn, "session_tombstone", session_id)

    @router.delete("/sessions/{session_id}/documents/{document_id}")
    async def detach(
        session_id: UUID, document_id: UUID, request: Request, conn: Connection
    ) -> Response:
        return await action_response(request, conn, "session_detach", session_id, document_id)

    @router.get("/{resource}")
    async def page(
        resource: str,
        conn: Connection,
        cursor: UUID | None = None,
        limit: int = Query(default=50, ge=1, le=100),
        app: str | None = Query(default=None, max_length=256),
        owner: str | None = Query(default=None, max_length=256),
        state: str | None = Query(default=None, max_length=64),
        content_type: str | None = Query(default=None, max_length=128),
    ) -> dict[str, Any]:
        return await metadata_page(
            conn,
            resource,
            cursor=cursor,
            limit=limit,
            app=app,
            owner=owner,
            state=state,
            content_type=content_type,
        )

    for route in router.routes:
        if isinstance(route, APIRoute):
            route.openapi_extra = {
                "security": [] if route.path.endswith("/auth/login") else [{"AdminCookie": []}],
                "x-metadata-only": True,
                "x-csrf-required": bool((route.methods or set()) - {"GET", "HEAD", "OPTIONS"}),
                "x-csrf-token-required": bool((route.methods or set()) - {"GET", "HEAD", "OPTIONS"})
                and not route.path.endswith("/auth/login"),
            }
            if route.path.endswith("/auth/login"):
                route.openapi_extra["requestBody"] = {
                    "required": True,
                    "content": {"application/json": {"schema": LoginRequest.model_json_schema()}},
                }
    return router
