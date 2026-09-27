"""Real PostgreSQL only; create/drop exclusively UUID-named test databases."""

import asyncio
import os
import subprocess
import sys
from collections.abc import Callable, Iterator
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest
from psycopg import sql
from sqlalchemy.engine import URL

from rag_core.adapters.persistence.database import database_url


def pytest_asyncio_loop_factories() -> dict[str, Callable[[], asyncio.AbstractEventLoop]]:
    # Psycopg requires selector I/O on Windows; this hook is local to integration tests.
    return {"selector": asyncio.SelectorEventLoop}


def migrate(url: URL, *arguments: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["DATABASE_URL"] = url.render_as_string(hide_password=False)
    # The URL already contains the separately loaded password.
    env.pop("DATABASE_PASSWORD_FILE", None)
    return subprocess.run(
        [sys.executable, "-m", "alembic", *arguments],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


@pytest.fixture
def migration_runner() -> Callable[..., subprocess.CompletedProcess[str]]:
    return migrate


@pytest.fixture(scope="module")
def pg_url() -> Iterator[URL]:
    value = os.environ.get("RAG_TEST_DATABASE_URL")
    if not value:
        pytest.fail("RAG_TEST_DATABASE_URL is required; this suite never substitutes SQLite/mocks")
    password_file = os.environ.get("DATABASE_PASSWORD_FILE")
    admin_url = database_url(value, Path(password_file) if password_file else None)
    if admin_url.database != "t10_acceptance" or admin_url.host not in {"127.0.0.1", "localhost"}:
        pytest.fail("Use the isolated loopback t10_acceptance PostgreSQL service")
    name = "t10_test_" + uuid4().hex
    dsn = admin_url.set(drivername="postgresql").render_as_string(hide_password=False)
    with psycopg.connect(dsn, autocommit=True) as admin:
        admin.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
    url = admin_url.set(database=name)
    try:
        with psycopg.connect(
            url.set(drivername="postgresql").render_as_string(hide_password=False)
        ) as empty:
            count = empty.execute(
                "SELECT count(*) FROM pg_tables WHERE schemaname='public'"
            ).fetchone()
            assert count == (0,)
        print(f"Real PostgreSQL: separate database {name}, public tables before migration=0")
        result = migrate(url, "upgrade", "head")
        assert result.returncode == 0, "Isolated database migration failed"
        print(f"Real PostgreSQL: migrated separate database {name}")
        yield url
    finally:
        with psycopg.connect(dsn, autocommit=True) as admin:
            admin.execute(sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(name)))
