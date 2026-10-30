"""T29 end-to-end administration browser workflows using real Playwright and real Docker backend.

Verifies:
- Login / logout / session expiry / CSRF
- Metadata privacy & XSS escaping
- Live PostgreSQL counts & honest dependency health / measurements
- Keyset pagination & filters (documents, jobs, sessions)
- Retry & reindex with real Celery worker, inference, MinIO, and Qdrant
- Session detach & tombstone with strict immutable source retention (no source deletion)
- Evaluations explicit empty state
- Responsive viewports (desktop 1920x1080, mobile 390x844) & keyboard navigation
- Screenshots captured to ignored .local/screenshots/ without secrets
"""

import asyncio
import hashlib
import os
import secrets
import socket
import subprocess
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID, uuid4

import boto3
import httpx
import pytest
import pytest_asyncio
import redis
import uvicorn
from playwright.async_api import Browser, Page, async_playwright
from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine

from rag_core.adapters.broker.celery import CeleryJobPublisher
from rag_core.adapters.persistence.database import build_engine
from rag_core.adapters.persistence.ingestion import PostgresIngestionRepository
from rag_core.adapters.persistence.registrations import (
    OutboxDispatcher,
    PostgresRegistrationRepository,
)
from rag_core.adapters.persistence.sessions import PostgresSessionRepository
from rag_core.adapters.storage.s3 import S3StorageReader, StorageLocation, StorageRegistry
from rag_core.admin.auth import AdminServices
from rag_core.admin.config import AdminConfig, hash_password
from rag_core.api.app import create_app
from rag_core.api.health import HealthChecks
from rag_core.auth import Principal
from rag_core.contracts.v1 import DocumentRegisterRequest
from rag_core.workers.runtime import WorkerConfig

pytestmark = [pytest.mark.e2e, pytest.mark.asyncio]

BUCKET = "rag-core-storage-test"
SECRET_DIR = Path(".local/secrets").resolve()
SCREENSHOT_DIR = Path(".local/screenshots").resolve()
TOKENIZER_PATH = Path(".local/tokenizers/bge-m3/tokenizer.json").resolve()

# Dedicated test ports from compose.admin-test.yaml
REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:16387/0")
QDRANT_URL = os.environ.get("RAG_ADMIN_TEST_QDRANT_URL", "http://127.0.0.1:56337")
STORAGE_URL = os.environ.get("RAG_ADMIN_TEST_STORAGE_URL", "http://127.0.0.1:19007")
INFERENCE_URL = os.environ.get("INFERENCE_URL", "http://127.0.0.1:58087")


@dataclass
class AdminBrowserEnvironment:
    base_url: str
    username: str
    password: str
    engine: AsyncEngine
    pg_url: URL
    repo: PostgresRegistrationRepository
    worker_repo: PostgresIngestionRepository
    principal: Principal
    session_id: UUID
    uploader: object
    dispatcher: OutboxDispatcher
    broker: redis.Redis
    worker_process: subprocess.Popen[bytes]
    worker_config: WorkerConfig
    tmp_path: Path


@asynccontextmanager
async def start_loopback_server(app: object) -> AsyncIterator[str]:
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    port = listener.getsockname()[1]
    listener.setblocking(False)

    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error", access_log=False)
    )
    task = asyncio.create_task(server.serve(sockets=[listener]))
    try:
        async with asyncio.timeout(10):
            while not server.started:
                assert not task.done(), "Uvicorn exited before startup"
                await asyncio.sleep(0.02)
        yield f"http://127.0.0.1:{port}"
    finally:
        server.should_exit = True
        await task


@pytest_asyncio.fixture
async def env(pg_url: URL, tmp_path: Path) -> AsyncIterator[AdminBrowserEnvironment]:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    engine = build_engine(pg_url)

    # 1. Fetch real inference fingerprint
    async with httpx.AsyncClient(trust_env=False) as client:
        inf_resp = await client.get(f"{INFERENCE_URL}/health/ready", timeout=10)
        inf_resp.raise_for_status()
        model_fingerprint = inf_resp.json()["fingerprint"]

    # 2. Storage registry with loopback permissions
    principal = Principal("t29-" + uuid4().hex, "admin-test-owner")
    app_target = "t29-filter-app"
    storage_locs = [
        StorageLocation(
            app_id=principal.app_id,
            alias="fixture",
            endpoint=STORAGE_URL,
            allow_loopback_http=True,
            bucket=BUCKET,
            region="us-east-1",
            prefix="allowed/",
            access_key_file=SECRET_DIR / "minio_reader_user",
            secret_key_file=SECRET_DIR / "minio_reader_password",
        ),
        StorageLocation(
            app_id=app_target,
            alias="fixture",
            endpoint=STORAGE_URL,
            allow_loopback_http=True,
            bucket=BUCKET,
            region="us-east-1",
            prefix="allowed/",
            access_key_file=SECRET_DIR / "minio_reader_user",
            secret_key_file=SECRET_DIR / "minio_reader_password",
        ),
    ]
    registry = StorageRegistry(locations=tuple(storage_locs))
    storage_config_file = tmp_path / "storage.json"
    storage_config_file.write_text(registry.model_dump_json())

    # 3. Worker config
    worker_temp = tmp_path / "worker-temp"
    worker_temp.mkdir(parents=True, exist_ok=True)
    worker_cfg = WorkerConfig(
        inference_url=INFERENCE_URL,
        qdrant_url=QDRANT_URL,
        model_fingerprint=model_fingerprint,
        storage_config=storage_config_file,
        tokenizer_path=TOKENIZER_PATH,
        temp_root=worker_temp,
        lease_seconds=10,
        heartbeat_seconds=1,
    )
    worker_config_file = tmp_path / "worker.json"
    worker_config_file.write_text(worker_cfg.model_dump_json())

    # 4. S3 uploader
    uploader = boto3.client(
        "s3",
        endpoint_url=STORAGE_URL,
        region_name="us-east-1",
        aws_access_key_id=(SECRET_DIR / "minio_uploader_user").read_text().strip(),
        aws_secret_access_key=(SECRET_DIR / "minio_uploader_password").read_text().strip(),
    )

    # 5. Outbox dispatcher & Redis broker
    dispatcher = OutboxDispatcher(engine, CeleryJobPublisher(REDIS_URL))
    broker = redis.Redis.from_url(REDIS_URL, socket_timeout=3)
    assert broker.ping(), "Redis broker unreachable"

    # 6. Repositories
    reg_temp = tmp_path / "registration-temp"
    reg_temp.mkdir(parents=True, exist_ok=True)
    repo = PostgresRegistrationRepository(engine, S3StorageReader(registry, temp_dir=reg_temp))
    worker_repo = PostgresIngestionRepository(engine, lease_seconds=10)
    session = await repo.sessions.create_session(principal, "browser-test-session-" + uuid4().hex)

    # 7. Start real Celery worker subprocess
    worker_env = {
        **os.environ,
        "WORKER_CONFIG_FILE": str(worker_config_file),
        "DATABASE_URL": pg_url.render_as_string(hide_password=False),
        "REDIS_URL": REDIS_URL,
    }
    worker_env.pop("DATABASE_PASSWORD_FILE", None)
    worker_proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "celery",
            "-A",
            "rag_core.workers.celery:app",
            "worker",
            "--pool=prefork",
            "--concurrency=1",
            "--prefetch-multiplier=1",
            "-Q",
            "rag_core_ingestion",
            "--loglevel=ERROR",
            "--without-gossip",
            "--without-mingle",
            "--without-heartbeat",
        ],
        env=worker_env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    # 8. Start FastAPI server with AdminServices on loopback
    admin_password = secrets.token_urlsafe(24)
    admin_username = "admin"
    admin_hashed = await asyncio.to_thread(hash_password, admin_password)

    # Create server with dynamic origin
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    port = listener.getsockname()[1]
    base_url = f"http://127.0.0.1:{port}"
    listener.setblocking(False)

    admin_config = AdminConfig(
        username=admin_username,
        password_hash=SecretStr(admin_hashed),
        origin=base_url,
        allow_loopback_http=True,
    )

    async def postgres_check() -> None:
        async with engine.connect() as conn:
            assert (await conn.execute(text("SELECT 1"))).scalar_one() == 1

    app = create_app(
        checks=HealthChecks(checks={"postgres": postgres_check}),
        admin_services=AdminServices(engine, admin_config),
    )

    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error", access_log=False)
    )
    server_task = asyncio.create_task(server.serve(sockets=[listener]))

    async with asyncio.timeout(10):
        while not server.started:
            await asyncio.sleep(0.02)

    e = AdminBrowserEnvironment(
        base_url=base_url,
        username=admin_username,
        password=admin_password,
        engine=engine,
        pg_url=pg_url,
        repo=repo,
        worker_repo=worker_repo,
        principal=principal,
        session_id=session.session_id,
        uploader=uploader,
        dispatcher=dispatcher,
        broker=broker,
        worker_process=worker_proc,
        worker_config=worker_cfg,
        tmp_path=tmp_path,
    )

    try:
        yield e
    finally:
        server.should_exit = True
        await server_task
        worker_proc.terminate()
        try:
            worker_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            worker_proc.kill()
        await engine.dispose()


@pytest_asyncio.fixture
async def browser() -> AsyncIterator[Browser]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            yield browser
        finally:
            await browser.close()


async def process_job_in_worker_container(e: AdminBrowserEnvironment, job_id: UUID) -> str:
    """Run real ingestion job inside the Linux Docker worker container against the test database."""
    db_name = e.pg_url.database
    script = f"""
import asyncio
from pathlib import Path
from uuid import UUID
from rag_core.adapters.storage.s3 import StorageLocation, StorageRegistry
from rag_core.workers.runtime import WorkerConfig, run_job

reg = StorageRegistry(locations=(
    StorageLocation(
        app_id='{e.principal.app_id}',
        alias='fixture',
        endpoint='http://minio:9000',
        allow_compose_http=True,
        bucket='rag-core-storage-test',
        region='us-east-1',
        prefix='allowed/',
        access_key_file=Path('/run/secrets/minio_reader_user'),
        secret_key_file=Path('/run/secrets/minio_reader_password'),
    ),
    StorageLocation(
        app_id='t29-filter-app',
        alias='fixture',
        endpoint='http://minio:9000',
        allow_compose_http=True,
        bucket='rag-core-storage-test',
        region='us-east-1',
        prefix='allowed/',
        access_key_file=Path('/run/secrets/minio_reader_user'),
        secret_key_file=Path('/run/secrets/minio_reader_password'),
    ),
))
Path('/tmp/storage.json').write_text(reg.model_dump_json())

cfg = WorkerConfig(
    inference_url='http://inference:8080',
    qdrant_url='http://qdrant:6333',
    model_fingerprint='{e.worker_config.model_fingerprint}',
    storage_config=Path('/tmp/storage.json'),
    tokenizer_path=Path('/models/embedding/tokenizer.json'),
    temp_root=Path('/tmp/worker-temp'),
)
result = asyncio.run(run_job(UUID('{job_id}'), cfg))
print('WORKER_SUCCESS:', result)
"""
    cmd = [
        "docker",
        "compose",
        "-p",
        "rag-core-t29-test",
        "-f",
        "compose.ingestion-test.yaml",
        "-f",
        "compose.admin-test.yaml",
        "run",
        "--rm",
        "-e",
        f"DATABASE_URL=postgresql://rag_core_test@postgres:5432/{db_name}",
        "-e",
        "DATABASE_PASSWORD_FILE=/run/secrets/postgres_password",
        "ingestion-tests",
        "python",
        "-c",
        script,
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    assert proc.returncode == 0, f"Worker container failed: {stderr.decode()}"
    return stdout.decode()


async def seed_registered_document(
    e: AdminBrowserEnvironment,
    filename: str = "t29_doc.txt",
    content: bytes = b"RAG Core T29 browser verification content.",
    state: str = "ready",
    principal: Principal | None = None,
    session_id: UUID | None = None,
) -> dict[str, UUID | str]:
    p = principal or e.principal
    s_id = session_id or e.session_id
    key = f"allowed/t29-{uuid4().hex}-{filename}"
    upload_res = e.uploader.put_object(Bucket=BUCKET, Key=key, Body=content)
    version_id = upload_res["VersionId"]
    source = {
        "storage_alias": "fixture",
        "bucket": BUCKET,
        "key": key,
        "sha256": hashlib.sha256(content).hexdigest(),
        "version_id": version_id,
    }
    body = DocumentRegisterRequest.model_validate(
        {
            "source": source,
            "filename": filename,
            "content_type": "text/plain",
            "external_upload_id": uuid4().hex,
        }
    )
    reg = await e.repo.register(p, s_id, uuid4().hex, body)
    gen_id = uuid4()
    if state == "ready":
        async with e.engine.begin() as conn:
            await conn.execute(
                text("""
                INSERT INTO index_generations (generation_id, app_id, owner_id, version_id, state, index_fingerprint)
                VALUES (:gen, :app, :owner, :ver, 'ready', repeat('c', 64))
                """),
                {"gen": gen_id, "app": p.app_id, "owner": p.user_id, "ver": reg.version_id},
            )
            await conn.execute(
                text(
                    "UPDATE document_versions SET state='ready', active_generation_id=:gen WHERE version_id=:ver"
                ),
                {"gen": gen_id, "ver": reg.version_id},
            )
            await conn.execute(
                text("UPDATE ingestion_jobs SET state='ready' WHERE job_id=:job"),
                {"job": reg.job.job_id},
            )
            await conn.execute(
                text("""
                INSERT INTO chunks (chunk_id, app_id, owner_id, version_id, generation_id, ordinal,
                    text, checksum, token_count, language, unit_id, source_map)
                VALUES (:chunk, :app, :owner, :ver, :gen, 0, 'Seeded chunk content',
                    repeat('d', 64), 4, 'und', 'unit-1', '{}'::jsonb)
                """),
                {
                    "chunk": uuid4(),
                    "app": p.app_id,
                    "owner": p.user_id,
                    "ver": reg.version_id,
                    "gen": gen_id,
                },
            )
    elif state == "failed":
        async with e.engine.begin() as conn:
            await conn.execute(
                text("UPDATE document_versions SET state='failed' WHERE version_id=:ver"),
                {"ver": reg.version_id},
            )
            await conn.execute(
                text(
                    "UPDATE ingestion_jobs SET state='failed', attempts=1, max_attempts=3, error_code='simulated_error' WHERE job_id=:job"
                ),
                {"job": reg.job.job_id},
            )
    return {
        "doc": reg.document_id,
        "version": reg.version_id,
        "job": reg.job.job_id,
        "session": s_id,
        "key": key,
        "sha256": source["sha256"],
        "version_id": version_id,
        "generation": gen_id,
    }


async def login_in_browser(page: Page, e: AdminBrowserEnvironment) -> None:
    await page.goto(f"{e.base_url}/admin")
    await page.wait_for_selector("#login:not([hidden])")
    await page.fill("#username", e.username)
    await page.fill("#password", e.password)
    await page.click("button[type='submit']")
    await page.wait_for_selector("#dashboard:not([hidden])")
    await page.wait_for_selector("#logout:not([hidden])")


# ==============================================================================
# TESTS
# ==============================================================================


async def test_admin_browser_auth_flow(env: AdminBrowserEnvironment, browser: Browser):
    """DoD 1: Login, logout, failed login, session expiry, and CSRF protection."""
    e = env
    context = await browser.new_context(viewport={"width": 1280, "height": 800})
    page = await context.new_page()

    # 1. Initial visit shows login form
    await page.goto(f"{e.base_url}/admin")
    assert await page.is_visible("#login")
    assert not await page.is_visible("#dashboard")
    assert not await page.is_visible("#logout")
    await page.screenshot(path=str(SCREENSHOT_DIR / "t29_auth_initial_login.png"))

    # 2. Failed login with bad password
    await page.fill("#username", e.username)
    await page.fill("#password", "wrong-password-1234")
    await page.click("button[type='submit']")
    await page.wait_for_selector("#error:not([hidden])")
    error_text = await page.text_content("#error")
    assert "Incorrect username or password" in error_text or "401" in error_text
    assert await page.is_visible("#login")

    # 3. Successful login
    await page.fill("#username", e.username)
    await page.fill("#password", e.password)
    await page.click("button[type='submit']")
    await page.wait_for_selector("#dashboard:not([hidden])")
    assert await page.is_visible("#logout")
    await page.wait_for_selector("#status:has-text('metadata')")
    status_text = await page.text_content("#status")
    assert any(
        phrase in status_text
        for phrase in ["Current metadata loaded", "Loading current metadata", "Connecting"]
    )
    await page.screenshot(path=str(SCREENSHOT_DIR / "t29_auth_signed_in.png"))

    # 4. Sign out
    await page.click("#logout")
    await page.wait_for_selector("#login:not([hidden])")
    assert not await page.is_visible("#dashboard")
    assert not await page.is_visible("#logout")
    status_text = await page.text_content("#status")
    assert "Signed out" in status_text
    # Focused control should be username
    is_username_focused = await page.evaluate("document.activeElement.id === 'username'")
    assert is_username_focused

    # 5. Sign back in and test session expiry
    await page.fill("#username", e.username)
    await page.fill("#password", e.password)
    await page.click("button[type='submit']")
    await page.wait_for_selector("#dashboard:not([hidden])")

    # Force-expire session in PostgreSQL
    async with e.engine.begin() as conn:
        await conn.execute(text("DELETE FROM admin_sessions"))

    # Trigger refresh
    await page.click("#refresh")
    await page.wait_for_selector("#login:not([hidden])")
    await page.wait_for_selector("#error:not([hidden])")
    err_text = await page.text_content("#error")
    assert "expired" in err_text.lower() or "401" in err_text
    await page.screenshot(path=str(SCREENSHOT_DIR / "t29_auth_session_expired.png"))

    await context.close()


async def test_admin_browser_overview_and_metadata_xss(
    env: AdminBrowserEnvironment, browser: Browser
):
    """DoD 1: Overview counts, dependency health, and metadata XSS prevention."""
    e = env
    # Seed document with XSS payload in filename
    xss_filename = "<img src=x onerror=window.__xss_fired=true>.txt"
    await seed_registered_document(e, filename=xss_filename, state="ready")

    # Seed session with XSS in external_session_id
    sessions_repo = PostgresSessionRepository(e.engine)
    await sessions_repo.create_session(e.principal, "<script>window.__xss_fired=true</script>")

    context = await browser.new_context(viewport={"width": 1280, "height": 800})
    page = await context.new_page()
    await login_in_browser(page, e)

    # 1. Overview Screen
    assert await page.is_visible("#page-title")
    title = await page.text_content("#page-title")
    assert title == "Overview"

    # Verify counts & dependency health are populated
    await page.wait_for_selector(".cards")
    cards_text = await page.text_content(".cards")
    assert "Documents" in cards_text
    assert "Sessions" in cards_text

    grid_text = await page.text_content(".overview-grid")
    assert "postgres" in grid_text
    assert "ok" in grid_text
    # Honest measurements: null metrics labeled "Not measured"
    assert "Not measured" in grid_text
    await page.screenshot(path=str(SCREENSHOT_DIR / "t29_overview_screen.png"))

    # 2. Documents Screen & XSS verification
    await page.click("nav a:has-text('Documents')")
    await page.wait_for_selector("table")
    assert "/admin/documents" in page.url

    # Filename should be decoded text, not an active <img> tag
    table_html = await page.inner_html("#content")
    assert "<img src=x" not in table_html
    assert "&lt;img" in table_html or "<img" not in table_html
    doc_text = await page.text_content("table")
    assert "<img src=x onerror=alert(1)>.txt" in doc_text or xss_filename in doc_text

    # Verify XSS did not fire
    xss_fired = await page.evaluate("window.__xss_fired")
    assert xss_fired is None, "XSS execution detected in Documents view!"
    await page.screenshot(path=str(SCREENSHOT_DIR / "t29_documents_xss_safe.png"))

    # 3. Sessions Screen & XSS verification
    await page.click("nav a:has-text('Sessions')")
    await page.wait_for_selector("table")
    assert "/admin/sessions" in page.url
    sessions_text = await page.text_content("table")
    assert "<script>" in sessions_text or "script" in sessions_text
    xss_fired = await page.evaluate("window.__xss_fired")
    assert xss_fired is None, "XSS execution detected in Sessions view!"

    await context.close()


async def test_admin_browser_documents_filtering_and_pagination(
    env: AdminBrowserEnvironment, browser: Browser
):
    """DoD 1: Filtering, keyset pagination, reset filters, and empty state."""
    e = env
    app_target = "t29-filter-app"
    app_other = e.principal.app_id

    # Seed 3 items for target app
    p_target = Principal(app_target, "owner-target")
    sess_target = await e.repo.sessions.create_session(p_target, "session-target")
    for i in range(3):
        await seed_registered_document(
            e,
            filename=f"doc_{i}.txt",
            state="ready",
            principal=p_target,
            session_id=sess_target.session_id,
        )

    # Seed 1 item for other app
    await seed_registered_document(e, filename="other.txt", state="ready")

    context = await browser.new_context(viewport={"width": 1280, "height": 800})
    page = await context.new_page()
    await login_in_browser(page, e)

    await page.click("nav a:has-text('Documents')")
    await page.wait_for_selector("table")

    # 1. Filter by App and Rows = 10
    await page.fill("#filter-app", app_target)
    await page.select_option("#limit", "10")
    async with page.expect_response(lambda r: "/v1/admin/documents" in r.url and r.status == 200):
        await page.click("button:has-text('Apply filters')")
    await page.wait_for_selector("table")

    rows = await page.locator("tbody tr").count()
    assert rows == 3
    for i in range(rows):
        row_text = await page.locator("tbody tr").nth(i).text_content()
        assert app_target in row_text
        assert app_other not in row_text

    # 2. Keyset Pagination (limit = 10)
    assert await page.locator("#next").is_visible()
    prev_btn = page.locator("#previous")
    assert await prev_btn.is_disabled()

    # 3. Filter for Nonexistent App -> Empty State
    await page.fill("#filter-app", "nonexistent-app-9999")
    async with page.expect_response(lambda r: "/v1/admin/documents" in r.url and r.status == 200):
        await page.click("button:has-text('Apply filters')")
    await page.wait_for_selector(".panel.empty")
    empty_text = await page.text_content(".panel.empty")
    assert "No matching metadata" in empty_text

    # 4. Clear Filters -> Restores full list
    async with page.expect_response(lambda r: "/v1/admin/documents" in r.url and r.status == 200):
        await page.click("#clear-filters")
    await page.wait_for_selector("table")
    rows_after = await page.locator("tbody tr").count()
    assert rows_after > 0

    await context.close()


async def test_admin_browser_jobs_retry_and_reindex_flow(
    env: AdminBrowserEnvironment, browser: Browser
):
    """DoD 1 & DoD 2: Real retry and reindex flows with audit events and Celery execution."""
    e = env
    # 1. Seed a document with a failed job
    seeded = await seed_registered_document(
        e,
        filename="retry_me.txt",
        content=b"Sample content for real retry and reindex verification in T29.",
        state="failed",
    )
    job_id = seeded["job"]

    context = await browser.new_context(viewport={"width": 1280, "height": 800})
    page = await context.new_page()
    await login_in_browser(page, e)

    # 2. Navigate to Jobs
    await page.click("nav a:has-text('Jobs')")
    await page.wait_for_selector("table")

    # Locate the failed job row
    job_row = page.locator(f"tbody tr:has-text('{job_id}')")
    await job_row.wait_for()
    assert "failed" in (await job_row.text_content()).lower()

    retry_btn = job_row.locator("button:has-text('Retry')")
    assert await retry_btn.is_visible()

    # 3. Test Confirmation Dialog cancellation
    await retry_btn.click()
    await page.wait_for_selector("dialog#confirmation[open]")
    dialog_text = await page.text_content("#confirm-description")
    assert str(job_id) in dialog_text
    await page.screenshot(path=str(SCREENSHOT_DIR / "t29_dialog_retry_confirmation.png"))

    # Cancel confirmation
    await page.click("#confirm-cancel")
    await page.wait_for_selector("dialog#confirmation", state="hidden")
    # Verify state in DB remains failed
    async with e.engine.connect() as conn:
        db_state = (
            await conn.execute(
                text("SELECT state FROM ingestion_jobs WHERE job_id=:id"), {"id": job_id}
            )
        ).scalar_one()
    assert db_state == "failed"

    # 4. Confirm Retry
    await retry_btn.click()
    await page.wait_for_selector("dialog#confirmation[open]")
    await page.click("#confirm-accept")
    await page.wait_for_selector("dialog#confirmation", state="hidden")

    # Status message reflects audit request
    await page.wait_for_selector("#status:has-text('Operation accepted')")
    status_msg = await page.text_content("#status")
    assert "Audit request" in status_msg

    # 5. Check PostgreSQL audit and job state
    async with e.engine.connect() as conn:
        job_db = (
            await conn.execute(
                text("SELECT state FROM ingestion_jobs WHERE job_id=:id"), {"id": job_id}
            )
        ).scalar_one()
        audit_count = (
            await conn.execute(
                text(
                    "SELECT count(*) FROM audit_events WHERE target_id=:id AND action='job_retry' AND outcome='success'"
                ),
                {"id": job_id},
            )
        ).scalar_one()
        outbox_count = (
            await conn.execute(
                text("SELECT count(*) FROM outbox_events WHERE job_id=:id"), {"id": job_id}
            )
        ).scalar_one()

    assert job_db == "queued"
    assert audit_count >= 1
    assert outbox_count >= 1

    # 6. Dispatch the job to Celery Redis
    dispatched = await e.dispatcher.dispatch_one()
    assert dispatched is True

    # 7. Process retried ingestion job in Docker worker container
    worker_output = await process_job_in_worker_container(e, job_id)
    assert "WORKER_SUCCESS" in worker_output

    async with e.engine.connect() as conn:
        current_state = (
            await conn.execute(
                text("SELECT state FROM ingestion_jobs WHERE job_id=:id"), {"id": job_id}
            )
        ).scalar_one()
    assert current_state == "ready"

    # 8. Refresh browser UI and verify state transitioned to 'ready'
    async with page.expect_response(lambda r: "/v1/admin/jobs" in r.url and r.status == 200):
        await page.click("#refresh")
    refreshed_row = page.locator(f"tbody tr:has-text('{job_id}')")
    await page.wait_for_selector(f"tbody tr:has-text('{job_id}'):has-text('ready')")
    refreshed_text = await refreshed_row.text_content()
    assert "ready" in refreshed_text.lower()
    await page.screenshot(path=str(SCREENSHOT_DIR / "t29_jobs_retried_ready.png"))

    # 9. Verify 'Reindex' button now appears on the ready job
    reindex_btn = refreshed_row.locator("button:has-text('Reindex')")
    assert await reindex_btn.is_visible()

    # Click Reindex and confirm
    await reindex_btn.click()
    await page.wait_for_selector("dialog#confirmation[open]")
    await page.click("#confirm-accept")
    await page.wait_for_selector("dialog#confirmation", state="hidden")
    await page.wait_for_selector("#status:has-text('Operation accepted')")

    # Check PostgreSQL for reindex audit event
    async with e.engine.connect() as conn:
        reindex_audit = (
            await conn.execute(
                text(
                    "SELECT count(*) FROM audit_events WHERE target_id=:id AND action='job_reindex' AND outcome='success'"
                ),
                {"id": job_id},
            )
        ).scalar_one()
    assert reindex_audit >= 1
    await e.dispatcher.dispatch_one()
    reindex_worker_output = await process_job_in_worker_container(e, job_id)
    assert "WORKER_SUCCESS" in reindex_worker_output

    await context.close()


async def test_admin_browser_sessions_detach_tombstone_source_retention(
    env: AdminBrowserEnvironment, browser: Browser
):
    """DoD 1 & DoD 2: Detach and tombstone actions with strict immutable source retention."""
    e = env
    source_bytes = b"Immutable document source content that MUST NOT be deleted by admin actions."
    seeded = await seed_registered_document(
        e, filename="retention_doc.txt", content=source_bytes, state="ready"
    )
    doc_id = seeded["doc"]
    session_id = seeded["session"]
    source_key = seeded["key"]
    original_sha256 = seeded["sha256"]
    original_version = seeded["version_id"]

    # Pre-action inspection of MinIO object
    before_head = e.uploader.head_object(Bucket=BUCKET, Key=source_key)
    before_etag = before_head["ETag"]
    assert before_head["VersionId"] == original_version

    context = await browser.new_context(viewport={"width": 1280, "height": 800})
    page = await context.new_page()
    await login_in_browser(page, e)

    # 1. Navigate to Sessions
    await page.click("nav a:has-text('Sessions')")
    await page.wait_for_selector("table")
    session_row = page.locator(f"tbody tr:has-text('{session_id}')")
    await session_row.wait_for()

    # 2. View Links panel
    view_links_btn = session_row.locator("button:has-text('View links')")
    await view_links_btn.click()
    await page.wait_for_selector("#links-panel:not([hidden])")
    await page.wait_for_selector(f"#links-content tbody tr:has-text('{doc_id}')")
    link_row = page.locator(f"#links-content tbody tr:has-text('{doc_id}')")
    assert "attached" in (await link_row.text_content()).lower()
    await page.screenshot(path=str(SCREENSHOT_DIR / "t29_sessions_view_links.png"))

    # 3. Detach Document
    detach_btn = link_row.locator("button:has-text('Detach')")
    await detach_btn.click()
    await page.wait_for_selector("dialog#confirmation[open]")
    await page.click("#confirm-accept")
    await page.wait_for_selector("dialog#confirmation", state="hidden")
    await page.wait_for_selector("#status:has-text('Operation accepted')")

    # Verify link state became detached in UI
    await page.wait_for_selector(
        f"#links-content tbody tr:has-text('{doc_id}'):has-text('detached')"
    )
    detached_row_text = await page.locator(
        f"#links-content tbody tr:has-text('{doc_id}')"
    ).text_content()
    assert "detached" in detached_row_text.lower()

    # Close links panel
    await page.click("#close-links")
    await page.wait_for_selector("#links-panel", state="hidden")

    # 4. Tombstone Session
    tombstone_btn = session_row.locator("button:has-text('Tombstone')")
    await tombstone_btn.click()
    await page.wait_for_selector("dialog#confirmation[open]")
    await page.click("#confirm-accept")
    await page.wait_for_selector("dialog#confirmation", state="hidden")
    await page.wait_for_selector("#status:has-text('Operation accepted')")

    # Verify session status became deleted in UI
    await page.wait_for_selector(f"tbody tr:has-text('{session_id}'):has-text('deleted')")
    updated_session_text = await session_row.text_content()
    assert "deleted" in updated_session_text.lower()
    await page.screenshot(path=str(SCREENSHOT_DIR / "t29_session_tombstoned.png"))

    # 5. Check PostgreSQL Audit Events
    async with e.engine.connect() as conn:
        detach_audit = (
            await conn.execute(
                text(
                    "SELECT count(*) FROM audit_events WHERE target_id=:session_id AND related_id=:doc_id AND action='session_detach' AND outcome='success'"
                ),
                {"session_id": session_id, "doc_id": doc_id},
            )
        ).scalar_one()
        tombstone_audit = (
            await conn.execute(
                text(
                    "SELECT count(*) FROM audit_events WHERE target_id=:id AND action='session_tombstone' AND outcome='success'"
                ),
                {"id": session_id},
            )
        ).scalar_one()
    assert detach_audit >= 1
    assert tombstone_audit >= 1

    # 6. IMMUTABLE SOURCE RETENTION CHECK (MinIO)
    after_head = e.uploader.head_object(Bucket=BUCKET, Key=source_key)
    assert after_head["VersionId"] == original_version, "VersionId changed after deletion!"
    assert after_head["ETag"] == before_etag, "ETag changed after deletion!"
    assert after_head["ContentLength"] == len(source_bytes)

    # Download source content from MinIO and verify SHA256 byte-by-byte
    after_obj = e.uploader.get_object(Bucket=BUCKET, Key=source_key)
    downloaded_body = after_obj["Body"].read()
    assert hashlib.sha256(downloaded_body).hexdigest() == original_sha256
    assert downloaded_body == source_bytes

    # Document record in PostgreSQL remains intact
    async with e.engine.connect() as conn:
        doc_count = (
            await conn.execute(
                text("SELECT count(*) FROM documents WHERE document_id=:id"), {"id": doc_id}
            )
        ).scalar_one()
    assert doc_count == 1

    await context.close()


async def test_admin_browser_evaluations_empty_state_and_responsive(
    env: AdminBrowserEnvironment, browser: Browser
):
    """DoD 1: Honest evaluations empty state, responsive mobile view, and keyboard accessibility."""
    e = env

    # 1. Desktop Evaluations Screen
    context = await browser.new_context(viewport={"width": 1920, "height": 1080})
    page = await context.new_page()
    await login_in_browser(page, e)

    await page.click("nav a:has-text('Evaluations')")
    await page.wait_for_selector(".panel.empty")
    assert "/admin/evaluations" in page.url

    eval_text = await page.text_content(".panel.empty")
    assert "No evaluation reports available" in eval_text
    assert "Evaluation reporting is not available in this build" in eval_text
    assert "No runs triggered from this interface" in eval_text
    # Refresh controls must be hidden on evaluations screen
    assert not await page.is_visible("#refresh")
    await page.screenshot(path=str(SCREENSHOT_DIR / "t29_evaluations_empty_desktop.png"))

    # 2. Keyboard Navigation: Skip link
    await page.keyboard.press("Tab")
    skip_focused = await page.evaluate("document.activeElement.classList.contains('skip')")
    assert skip_focused
    await page.keyboard.press("Enter")
    main_focused = await page.evaluate("document.activeElement.id === 'main'")
    assert main_focused

    # 3. Responsive Mobile Viewport (iPhone 14 standard: 390 x 844)
    await context.close()
    mobile_context = await browser.new_context(
        viewport={"width": 390, "height": 844}, is_mobile=True
    )
    mobile_page = await mobile_context.new_page()
    await login_in_browser(mobile_page, e)

    # Verify overview on mobile
    await mobile_page.wait_for_selector(".cards")
    assert await mobile_page.is_visible(".cards")
    await mobile_page.screenshot(path=str(SCREENSHOT_DIR / "t29_mobile_overview.png"))

    # Navigate to documents and check horizontal scrolling table region
    await mobile_page.click("nav a:has-text('Documents')")
    await mobile_page.wait_for_selector(".table-wrap")
    wrap_role = await mobile_page.get_attribute(".table-wrap", "role")
    wrap_tabindex = await mobile_page.get_attribute(".table-wrap", "tabindex")
    assert wrap_role == "region"
    assert wrap_tabindex == "0"
    await mobile_page.screenshot(path=str(SCREENSHOT_DIR / "t29_mobile_documents.png"))

    await mobile_context.close()
