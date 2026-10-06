"""Public application factory with fail-closed authentication and trusted lifespan DI."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, status

from rag_core import __version__
from rag_core.api.auth import AuthenticationMiddleware
from rag_core.api.errors import install_error_handlers
from rag_core.api.health import HealthChecks, build_health_checks
from rag_core.api.public import build_public_router
from rag_core.api.runtime import PublicServices, load_api_config, public_services
from rag_core.auth.config import load_auth_config
from rag_core.auth.verifier import Authenticator
from rag_core.config import Settings, load_settings


def create_app(
    *,
    settings: Settings | None = None,
    checks: HealthChecks | None = None,
    services: PublicServices | None = None,
) -> FastAPI:
    """Mount contracts even without config; unconfigured business services fail closed."""

    resolved_settings = settings
    if checks is None:
        resolved_settings = settings or load_settings()
        checks = build_health_checks(resolved_settings)
    resolved_checks = checks

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if services is not None:
            app.state.public_services = services
            yield
        elif resolved_settings is not None and resolved_settings.api_config_file is not None:
            config = load_api_config(resolved_settings.api_config_file)
            async with public_services(resolved_settings, config) as runtime:
                app.state.public_services = runtime
                yield
            app.state.public_services = None
        else:
            yield

    app = FastAPI(title="RAG Core", version=__version__, lifespan=lifespan)
    app.state.public_services = services
    authenticator = None
    if resolved_settings is not None and resolved_settings.auth_config_file is not None:
        authenticator = Authenticator(
            load_auth_config(
                resolved_settings.auth_config_file,
                production=resolved_settings.app_env == "production",
            )
        )
    app.add_middleware(AuthenticationMiddleware, authenticator=authenticator)
    install_error_handlers(app)
    app.include_router(build_public_router())

    @app.get("/health/live", tags=["health"])
    async def live() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready", tags=["health"])
    async def ready(response: Response) -> dict[str, object]:
        report = await resolved_checks.readiness()
        if not report.ready:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return report.as_dict()

    from rag_core.contracts.openapi import build_designed_openapi

    generated_openapi = app.openapi

    def public_openapi() -> dict[str, object]:
        schema = generated_openapi()
        inventory = build_designed_openapi()
        schema.setdefault("components", {}).setdefault("schemas", {}).update(
            inventory["components"]["schemas"]
        )
        schema["components"]["securitySchemes"] = inventory["components"]["securitySchemes"]
        for path, methods in schema["paths"].items():
            if path not in inventory["paths"]:
                continue
            for method, operation in methods.items():
                if method not in inventory["paths"][path]:
                    continue
                designed = inventory["paths"][path][method]
                for field in ("security", "x-served", "x-implementation-status", "x-sse-contract"):
                    if field in designed:
                        operation[field] = designed[field]
                if path.startswith("/v1/"):
                    for code, response in designed["responses"].items():
                        if code != "200" and code != "202":
                            operation["responses"][code] = response
                if path == "/v1/query/stream":
                    operation["responses"]["200"] = designed["responses"]["200"]
        return schema

    app.openapi = public_openapi  # type: ignore[method-assign]
    return app
