"""Explicit operator-run PostgreSQL migrations; never run on API startup."""

from alembic import context
from sqlalchemy import create_engine, pool

from rag_core.adapters.persistence.database import database_url_from_env

url = database_url_from_env()
if context.is_offline_mode():
    context.configure(url=url, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = create_engine(url, poolclass=pool.NullPool, hide_parameters=True)
    with engine.connect() as connection, connection.begin():
        # One explicit migration owner, including concurrent CLI invocations.
        connection.exec_driver_sql("SELECT pg_advisory_xact_lock(710010)")
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()
