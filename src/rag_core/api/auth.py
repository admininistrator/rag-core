"""ASGI auth guard for v1 and dependency for future business handlers."""

from uuid import uuid4

from fastapi import HTTPException, Request
from starlette.datastructures import Headers
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from rag_core.auth import AuthUnavailable, InvalidCredentials, Principal
from rag_core.auth.verifier import Authenticator


def require_principal(request: Request) -> Principal:
    principal = getattr(request.state, "principal", None)
    if not isinstance(principal, Principal):
        raise HTTPException(status_code=401, detail="Authentication required")
    return principal


class AuthenticationMiddleware:
    def __init__(self, app: ASGIApp, authenticator: Authenticator | None) -> None:
        self.app = app
        self.authenticator = authenticator

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        path = scope.get("path", "")
        if scope["type"] != "http" or not (path == "/v1" or path.startswith("/v1/")):
            await self.app(scope, receive, send)
            return
        try:
            if self.authenticator is None:
                raise AuthUnavailable
            headers = Headers(scope=scope)
            authorization = headers.getlist("authorization")
            service_keys = headers.getlist("x-rag-service-key")
            if len(authorization) != 1 or len(service_keys) != 1:
                raise InvalidCredentials
            parts = authorization[0].split(" ")
            if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1]:
                raise InvalidCredentials
            principal = await self.authenticator.authenticate(service_keys[0], parts[1])
            scope.setdefault("state", {})["principal"] = principal
        except (InvalidCredentials, AuthUnavailable) as exc:
            invalid = isinstance(exc, InvalidCredentials)
            response = JSONResponse(
                status_code=401 if invalid else 503,
                content={
                    "request_id": str(uuid4()),
                    "error": {
                        "code": "invalid_credentials" if invalid else "dependency_unavailable",
                        "message": "Invalid credentials"
                        if invalid
                        else "Authentication unavailable",
                        "retryable": not invalid,
                        "details": [],
                    },
                },
                headers={
                    "Cache-Control": "no-store",
                    **({"WWW-Authenticate": "Bearer"} if invalid else {}),
                },
            )
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)
