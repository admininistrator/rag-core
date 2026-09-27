"""Health application factory with a fail-closed guard for the v1 namespace."""

from __future__ import annotations

from fastapi import FastAPI, Response, status

from rag_core import __version__
from rag_core.api.auth import AuthenticationMiddleware
from rag_core.api.health import HealthChecks, build_health_checks
from rag_core.auth.config import load_auth_config
from rag_core.auth.verifier import Authenticator
from rag_core.config import Settings, load_settings


def create_app(*, settings: Settings | None = None, checks: HealthChecks | None = None) -> FastAPI:
    """Create health routes and the T09 auth guard; business endpoints are not mounted."""

    resolved_settings = settings
    if checks is None:
        resolved_settings = settings or load_settings()
        checks = build_health_checks(resolved_settings)
    resolved_checks = checks
    app = FastAPI(title="RAG Core", version=__version__)
    authenticator = None
    if resolved_settings is not None and resolved_settings.auth_config_file is not None:
        authenticator = Authenticator(
            load_auth_config(
                resolved_settings.auth_config_file,
                production=resolved_settings.app_env == "production",
            )
        )
    app.add_middleware(AuthenticationMiddleware, authenticator=authenticator)

    @app.get("/health/live", tags=["health"])
    async def live() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready", tags=["health"])
    async def ready(response: Response) -> dict[str, object]:
        report = await resolved_checks.readiness()
        if not report.ready:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return report.as_dict()

    return app
