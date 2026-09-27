"""Bounded PostgreSQL engines with redacted URL repr and SQL parameters."""

import os
from pathlib import Path

from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import ArgumentError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


def database_url(value: str, password_file: Path | None = None) -> URL:
    try:
        url = make_url(value)
        if url.drivername not in {"postgresql", "postgresql+psycopg"} or not url.database:
            raise ValueError
        url = url.set(drivername="postgresql+psycopg")
        if password_file is not None:
            password = password_file.read_text(encoding="utf-8").strip()
            if not password:
                raise ValueError
            url = url.set(password=password)
        return url
    except (ArgumentError, ValueError, OSError):
        raise ValueError("Invalid DATABASE_URL or DATABASE_PASSWORD_FILE") from None


def database_url_from_env() -> URL:
    value = os.environ.get("DATABASE_URL", "")
    if not value:
        raise ValueError("DATABASE_URL is required for migrations")
    password_file = os.environ.get("DATABASE_PASSWORD_FILE")
    return database_url(value, Path(password_file) if password_file else None)


def build_engine(url: URL) -> AsyncEngine:
    return create_async_engine(
        url,
        pool_size=5,
        max_overflow=0,
        pool_timeout=5,
        pool_pre_ping=True,
        hide_parameters=True,
        connect_args={
            "connect_timeout": 5,
            "options": "-c statement_timeout=10000 -c lock_timeout=5000",
        },
    )
