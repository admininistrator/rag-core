"""Real PostgreSQL fixture for admin security/operations; random per-module database."""

import asyncio
import secrets
from collections.abc import AsyncIterator
from dataclasses import dataclass
from uuid import UUID, uuid4

import httpx
import pytest_asyncio
from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine

from rag_core.adapters.persistence.database import build_engine
from rag_core.adapters.persistence.sessions import PostgresSessionRepository
from rag_core.admin.auth import AdminServices
from rag_core.admin.config import AdminConfig, hash_password
from rag_core.api.app import create_app
from rag_core.api.health import HealthChecks
from rag_core.auth import Principal

ORIGIN = "http://127.0.0.1:8000"


@dataclass
class AdminFixture:
    engine: AsyncEngine
    client: httpx.AsyncClient
    config: AdminConfig
    password: str
    app: object
    url: URL

    async def login(self) -> dict[str, str]:
        response = await self.client.post(
            "/v1/admin/auth/login",
            headers={"Origin": ORIGIN},
            json={"username": self.config.username, "password": self.password},
        )
        assert response.status_code == 200, response.text
        return {"Origin": ORIGIN, "X-CSRF-Token": response.json()["csrf_token"]}

    async def seed(
        self, state: str = "queued", *, app: str | None = None, owner: str = "test-owner"
    ) -> dict[str, UUID | str]:
        principal = Principal(app or "admin-test-" + uuid4().hex, owner)
        sessions = PostgresSessionRepository(self.engine)
        session = await sessions.create_session(
            principal, "<script>external</script>" + uuid4().hex
        )
        ids = {k: uuid4() for k in ["doc", "version", "job", "registration", "generation"]}
        p = {
            **ids,
            "app": principal.app_id,
            "owner": principal.user_id,
            "session": session.session_id,
            "state": state,
        }
        async with self.engine.begin() as conn:
            await conn.execute(
                text("""
                INSERT INTO documents (document_id,app_id,owner_id,filename,storage_alias,bucket,object_key)
                VALUES (:doc,:app,:owner,'<img src=x onerror=alert(1)>.txt',
                    'private-storage-alias','private-bucket','PRIVATE_SOURCE_KEY')
            """),
                p,
            )
            await conn.execute(
                text("""
                INSERT INTO document_versions (version_id,app_id,owner_id,document_id,
                    source_sha256,content_type,size_bytes)
                VALUES (:version,:app,:owner,:doc,repeat('a',64),'text/plain',30)
            """),
                p,
            )
            await conn.execute(
                text("""
                INSERT INTO ingestion_jobs (job_id,app_id,owner_id,version_id,state,task_fingerprint,
                    error_code) VALUES (:job,:app,:owner,:version,:state,'seed',
                    'PRIVATE_ERROR_WITH_SECRET_AND_ANSWER')
            """),
                p,
            )
            await conn.execute(
                text("""
                INSERT INTO upload_registrations (registration_id,app_id,owner_id,session_id,
                    idempotency_key,request_hash,external_upload_id,document_id,version_id,job_id)
                VALUES (:registration,:app,:owner,:session,'seed',repeat('b',64),'upload',:doc,:version,:job)
            """),
                p,
            )
            await sessions.attach_version(
                conn, principal, session.session_id, ids["version"], ids["registration"]
            )
            if state == "ready":
                await conn.execute(
                    text("""
                    INSERT INTO index_generations (generation_id,app_id,owner_id,version_id,state,
                        index_fingerprint) VALUES (:generation,:app,:owner,:version,'ready',repeat('c',64))
                """),
                    p,
                )
                await conn.execute(
                    text("""
                    UPDATE document_versions SET state='ready',active_generation_id=:generation
                    WHERE version_id=:version
                """),
                    p,
                )
                await conn.execute(
                    text("""
                    INSERT INTO chunks (chunk_id,app_id,owner_id,version_id,generation_id,ordinal,
                        text,checksum,token_count,language,unit_id,source_map)
                    VALUES (:chunk,:app,:owner,:version,:generation,0,'PRIVATE_CHUNK_ANSWER',
                        repeat('d',64),4,'und','private-unit','{}'::jsonb)
                """),
                    {**p, "chunk": uuid4()},
                )
        return p


@pytest_asyncio.fixture
async def admin_fixture(pg_url: URL) -> AsyncIterator[AdminFixture]:
    engine = build_engine(pg_url)
    password = secrets.token_urlsafe(24)
    hashed = await asyncio.to_thread(hash_password, password)
    config = AdminConfig(
        username="admin", password_hash=SecretStr(hashed), origin=ORIGIN, allow_loopback_http=True
    )

    async def postgres() -> None:
        async with engine.connect() as conn:
            assert (await conn.execute(text("SELECT 1"))).scalar_one() == 1

    app = create_app(
        checks=HealthChecks(checks={"postgres": postgres}),
        admin_services=AdminServices(engine, config),
    )
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=ORIGIN) as client:
        try:
            yield AdminFixture(engine, client, config, password, app, pg_url)
        finally:
            # Only local admin session/auth fixtures. Seed metadata retained until private DB teardown.
            async with engine.begin() as conn:
                await conn.execute(text("DELETE FROM admin_sessions"))
                await conn.execute(text("DELETE FROM admin_login_limits"))
            await engine.dispose()
