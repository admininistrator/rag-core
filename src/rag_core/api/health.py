"""Dependency-aware health checks for the T02 API skeleton."""

from __future__ import annotations

import asyncio
import math
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final, cast

import httpx
import psycopg
from psycopg.conninfo import make_conninfo
from redis.asyncio import Redis

from rag_core.config import Settings

DependencyCheck = Callable[[], Awaitable[None]]
COMPONENT_NAMES: Final = ("postgres", "redis", "qdrant")


@dataclass(frozen=True, slots=True)
class ReadinessReport:
    """Sanitized readiness result safe to return to an unauthenticated probe."""

    ready: bool
    components: Mapping[str, str]

    def as_dict(self) -> dict[str, object]:
        return {
            "status": "ready" if self.ready else "unavailable",
            "components": dict(self.components),
        }


@dataclass(frozen=True, slots=True)
class HealthChecks:
    """Named checks injected into the API for real adapters or isolated tests."""

    checks: Mapping[str, DependencyCheck]

    async def readiness(self) -> ReadinessReport:
        names = tuple(self.checks)
        results = await asyncio.gather(
            *(self.checks[name]() for name in names), return_exceptions=True
        )
        components = {
            name: "ok" if not isinstance(result, BaseException) else "unavailable"
            for name, result in zip(names, results, strict=True)
        }
        return ReadinessReport(
            ready=all(value == "ok" for value in components.values()),
            components=components,
        )


def _read_optional_secret(path: Path | None) -> str | None:
    if path is None:
        return None
    value = path.read_text(encoding="utf-8").strip()
    if not value:
        raise ValueError("Configured database password file is empty")
    return value


def build_health_checks(settings: Settings) -> HealthChecks:
    """Build probes that validate each dependency with its native protocol."""

    timeout = settings.health_timeout_seconds
    connect_timeout = max(1, math.ceil(timeout))
    database_password = _read_optional_secret(settings.database_password_file)

    async def check_postgres() -> None:
        async with asyncio.timeout(timeout):
            kwargs: dict[str, str | int] = {"connect_timeout": connect_timeout}
            if database_password is not None:
                kwargs["password"] = database_password
            conninfo = make_conninfo(str(settings.database_url), **kwargs)
            connection = await psycopg.AsyncConnection.connect(conninfo)
            async with connection, connection.cursor() as cursor:
                await cursor.execute("SELECT 1")
                row = await cursor.fetchone()
                if row != (1,):
                    raise RuntimeError("PostgreSQL readiness query returned an unexpected result")

    async def check_redis() -> None:
        async with asyncio.timeout(timeout):
            client: Redis = Redis.from_url(
                str(settings.redis_url),
                socket_connect_timeout=timeout,
                socket_timeout=timeout,
            )
            try:
                ping = cast(Awaitable[bool], client.ping())
                if await ping is not True:
                    raise RuntimeError("Redis PING did not return success")
            finally:
                await client.aclose()

    async def check_qdrant() -> None:
        url = f"{str(settings.qdrant_url).rstrip('/')}/readyz"
        async with asyncio.timeout(timeout):
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)
                response.raise_for_status()

    return HealthChecks(
        checks={
            "postgres": check_postgres,
            "redis": check_redis,
            "qdrant": check_qdrant,
        }
    )
