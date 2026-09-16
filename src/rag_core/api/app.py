"""FastAPI application factory for process and dependency health routes."""

from __future__ import annotations

from fastapi import FastAPI, Response, status

from rag_core import __version__
from rag_core.api.health import HealthChecks, build_health_checks
from rag_core.config import Settings, load_settings


def create_app(
    *, settings: Settings | None = None, checks: HealthChecks | None = None
) -> FastAPI:
    """Create the T02 API skeleton without business endpoints."""

    if checks is None:
        resolved_settings = settings or load_settings()
        checks = build_health_checks(resolved_settings)
    resolved_checks = checks
    app = FastAPI(title="RAG Core", version=__version__)

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
