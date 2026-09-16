"""Health route behavior with deterministic injected dependency checks."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

import httpx
import pytest

from rag_core.api.app import create_app
from rag_core.api.health import HealthChecks
from rag_core.config import Settings


async def _ok() -> None:
    return None


async def _failed() -> None:
    raise ConnectionError("synthetic dependency failure")


def _checks(redis: Callable[[], Awaitable[None]] = _ok) -> HealthChecks:
    return HealthChecks(checks={"postgres": _ok, "redis": redis, "qdrant": _ok})


def _settings() -> Settings:
    return Settings(
        database_url="postgresql://rag_core:local-only@postgres:5432/rag_core",
        redis_url="redis://redis:6379/0",
        qdrant_url="http://qdrant:6333",
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_live_reports_process_without_running_readiness_checks() -> None:
    app = create_app(settings=_settings(), checks=_checks(redis=_failed))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_ready_reports_each_successful_real_dependency_slot() -> None:
    app = create_app(settings=_settings(), checks=_checks())
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "components": {"postgres": "ok", "redis": "ok", "qdrant": "ok"},
    }


@pytest.mark.unit
@pytest.mark.asyncio
async def test_ready_returns_503_and_redacts_dependency_exception() -> None:
    app = create_app(settings=_settings(), checks=_checks(redis=_failed))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "unavailable",
        "components": {"postgres": "ok", "redis": "unavailable", "qdrant": "ok"},
    }
    assert "synthetic" not in response.text
