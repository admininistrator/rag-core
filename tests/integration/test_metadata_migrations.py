"""Separate empty PG database and destructive replay only inside that test DB."""

import subprocess
from collections.abc import Callable

import psycopg
import pytest
from sqlalchemy.engine import URL

pytestmark = pytest.mark.integration


def test_migrations_reproduce_schema_on_separate_database(
    pg_url: URL,
    migration_runner: Callable[..., subprocess.CompletedProcess[str]],
) -> None:
    dsn = pg_url.set(drivername="postgresql").render_as_string(hide_password=False)

    def schema() -> list[tuple[object, ...]]:
        with psycopg.connect(dsn) as conn:
            return list(
                conn.execute("""
                SELECT c.relname, a.attname, pg_catalog.format_type(a.atttypid,a.atttypmod),
                       a.attnotnull, pg_get_expr(d.adbin,d.adrelid)
                FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
                JOIN pg_attribute a ON a.attrelid=c.oid
                LEFT JOIN pg_attrdef d ON d.adrelid=c.oid AND d.adnum=a.attnum
                WHERE n.nspname='public' AND c.relkind='r' AND a.attnum>0 AND NOT a.attisdropped
                ORDER BY c.relname,a.attnum
            """)
            )

    before = schema()

    def constraints_and_indexes() -> list[tuple[object, ...]]:
        with psycopg.connect(dsn) as conn:
            return list(
                conn.execute("""
                SELECT r.relname, c.conname, pg_get_constraintdef(c.oid)
                FROM pg_constraint c JOIN pg_class r ON r.oid=c.conrelid
                JOIN pg_namespace n ON n.oid=r.relnamespace
                WHERE n.nspname='public'
                UNION ALL
                SELECT tablename, indexname, indexdef FROM pg_indexes WHERE schemaname='public'
                ORDER BY 1,2,3
            """)
            )

    constraints = constraints_and_indexes()
    assert {row[0] for row in before} == {
        "alembic_version",
        "sessions",
        "documents",
        "document_versions",
        "index_generations",
        "session_documents",
        "ingestion_jobs",
        "outbox_events",
    }
    assert migration_runner(pg_url, "upgrade", "head").returncode == 0
    assert schema() == before
    assert constraints_and_indexes() == constraints
    assert migration_runner(pg_url, "downgrade", "base").returncode == 0
    assert {row[0] for row in schema()} == {"alembic_version"}
    assert migration_runner(pg_url, "upgrade", "head").returncode == 0
    assert schema() == before
    assert constraints_and_indexes() == constraints
    print(
        "PASS separate empty PG migration -> repeat head -> downgrade base -> upgrade head: identical schema"
    )
