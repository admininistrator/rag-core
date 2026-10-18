"""Independent admin credentials, real PG sessions/expiry/rotation/CSRF and privacy."""

import asyncio
import json
import secrets
import socket
import threading
from uuid import uuid4

import httpx
import pytest
import uvicorn
from pydantic import SecretStr
from sqlalchemy import text

from rag_core.adapters.persistence.database import build_engine
from rag_core.admin.auth import COOKIE, AdminAuthentication, AdminServices, digest
from rag_core.admin.config import AdminConfig, hash_password, load_admin_config, verify_password
from rag_core.api.app import create_app
from rag_core.api.health import HealthChecks
from rag_core.config import Settings
from tests.fixtures.admin_support import ORIGIN, AdminFixture
from tests.fixtures.admin_support import admin_fixture as shared_admin_fixture
from tests.integration.conftest import pg_url  # noqa: F401

admin_fixture = shared_admin_fixture

pytestmark = [pytest.mark.security, pytest.mark.asyncio]


async def test_unauthorized_and_app_credentials_never_admin(admin_fixture: AdminFixture) -> None:
    f = admin_fixture
    for path in [
        "/overview",
        "/documents",
        "/jobs",
        "/sessions",
        "/index",
        "/audit",
        "/auth/session",
    ]:
        response = await f.client.get("/v1/admin" + path)
        assert response.status_code == 401
        assert response.headers["cache-control"] == "no-store"
    response = await f.client.get(
        "/v1/admin/documents",
        headers={
            "Authorization": "Bearer not-admin",
            "X-RAG-Service-Key": secrets.token_urlsafe(32),
        },
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "admin_required"
    for method, path in [("POST", f"/jobs/{uuid4()}/cancel"), ("DELETE", f"/sessions/{uuid4()}")]:
        assert (await f.client.request(method, "/v1/admin" + path)).status_code == 401
    assert (await f.client.get("/v1/administrator/documents")).status_code == 503
    unconfigured = create_app(checks=HealthChecks(checks={}))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=unconfigured), base_url=ORIGIN
    ) as client:
        assert (await client.get("/v1/admin/documents")).status_code == 503


async def test_login_password_hash_cookie_logout_and_replay(admin_fixture: AdminFixture) -> None:
    f = admin_fixture
    assert verify_password(f.password, f.config.password_hash.get_secret_value())
    assert not verify_password("wrong", f.config.password_hash.get_secret_value())
    assert f.password not in repr(f.config)
    response = await f.client.post(
        "/v1/admin/auth/login",
        headers={"Origin": ORIGIN},
        json={"username": "admin", "password": "wrong"},
    )
    assert response.status_code == 401 and "set-cookie" not in response.headers
    headers = await f.login()
    token = f.client.cookies.get(COOKIE)
    assert token and len(token) == 43
    async with f.engine.connect() as conn:
        row = (
            (
                await conn.execute(
                    text("SELECT * FROM admin_sessions WHERE token_hash=:token"),
                    {"token": digest(token)},
                )
            )
            .mappings()
            .one()
        )
        assert token not in str(dict(row)) and headers["X-CSRF-Token"] not in str(dict(row))
    assert (await f.client.get("/v1/admin/auth/session")).json()["csrf_token"] == headers[
        "X-CSRF-Token"
    ]
    assert (await f.client.post("/v1/admin/auth/logout", headers=headers)).status_code == 204
    f.client.cookies.set(COOKIE, token)
    assert (await f.client.get("/v1/admin/documents")).status_code == 401
    async with f.engine.connect() as conn:
        actions = (
            await conn.execute(text("SELECT action,outcome FROM audit_events ORDER BY created_at"))
        ).all()
        assert ("login", "denied") in actions and ("logout", "success") in actions


async def test_csrf_origin_and_duplicate_headers_are_enforced(admin_fixture: AdminFixture) -> None:
    f = admin_fixture
    body = {"username": "admin", "password": f.password}
    for origin in [None, "http://evil.test", "null", ORIGIN + ".evil.test"]:
        response = await f.client.post(
            "/v1/admin/auth/login", json=body, headers={"Origin": origin} if origin else {}
        )
        assert response.status_code == 403
    headers = await f.login()
    seeded = await f.seed()
    path = f"/v1/admin/jobs/{seeded['job']}/cancel"
    bad = [
        {},
        {"Origin": ORIGIN},
        {"X-CSRF-Token": headers["X-CSRF-Token"]},
        {**headers, "Origin": "http://evil.test"},
        {**headers, "X-CSRF-Token": "x" * 64},
        {**headers, "Sec-Fetch-Site": "cross-site"},
    ]
    for supplied in bad:
        assert (await f.client.post(path, headers=supplied)).status_code == 403
    duplicate = [
        ("Origin", ORIGIN),
        ("X-CSRF-Token", headers["X-CSRF-Token"]),
        ("X-CSRF-Token", headers["X-CSRF-Token"]),
    ]
    assert (await f.client.post(path, headers=duplicate)).status_code == 403
    assert (await f.client.post(path, headers=headers)).status_code == 200
    async with f.engine.connect() as conn:
        assert (
            await conn.execute(
                text("SELECT count(*) FROM audit_events WHERE action='csrf_rejected'")
            )
        ).scalar_one() >= 7


async def test_session_expiry_rotation_and_fixation(admin_fixture: AdminFixture) -> None:
    f = admin_fixture
    await f.login()
    old_token = f.client.cookies.get(COOKIE)
    await f.login()
    new_token = f.client.cookies.get(COOKIE)
    assert old_token != new_token
    async with f.engine.connect() as conn:
        assert (
            await conn.execute(
                text("SELECT revoked_at IS NOT NULL FROM admin_sessions WHERE token_hash=:token"),
                {"token": digest(old_token)},
            )
        ).scalar_one()
    async with f.engine.begin() as conn:
        await conn.execute(
            text(
                "UPDATE admin_sessions SET created_at=now()-interval '2 hours',"
                "expires_at=now()-interval '1 hour'"
            )
        )
    assert (await f.client.get("/v1/admin/documents")).status_code == 401
    await f.login()
    rotated = f.config.model_copy(
        update={"password_hash": SecretStr(hash_password(secrets.token_urlsafe(24)))}
    )
    f.app.state.admin_authentication = AdminAuthentication(AdminServices(f.engine, rotated))
    assert (await f.client.get("/v1/admin/documents")).status_code == 401


async def test_login_boundaries_throttle_and_no_secret_logging(
    admin_fixture: AdminFixture, caplog
) -> None:
    f = admin_fixture
    for _ in range(10):
        response = await f.client.post(
            "/v1/admin/auth/login",
            headers={"Origin": ORIGIN},
            json={"username": "attacker-" + secrets.token_hex(4), "password": "wrong"},
        )
        assert response.status_code == 401
    response = await f.client.post(
        "/v1/admin/auth/login",
        headers={"Origin": ORIGIN},
        json={"username": "admin", "password": f.password},
    )
    assert response.status_code == 429 and response.headers["retry-after"] == "60"
    response = await f.client.post(
        "/v1/admin/auth/login",
        headers={"Origin": ORIGIN, "Content-Type": "application/json"},
        content=b"x" * 8193,
    )
    assert response.status_code == 413
    response = await f.client.post(
        "/v1/admin/auth/login",
        headers={"Origin": ORIGIN},
        json={"username": "admin", "password": f.password, "role": "admin"},
    )
    assert response.status_code == 422
    assert f.password not in response.text + caplog.text
    assert f.config.password_hash.get_secret_value() not in caplog.text


async def test_config_https_default_and_safe_failures(tmp_path) -> None:
    password = secrets.token_urlsafe(24)
    hashed = hash_password(password)
    config = AdminConfig(username="admin", password_hash=hashed, origin="https://localhost:8000")
    assert config.secure_cookie and config.session_seconds == 3600
    for origin in [
        "http://remote.test",
        "https://localhost/path",
        "https://user@localhost",
        "https://localhost:bad",
        "null",
    ]:
        with pytest.raises(ValueError):
            AdminConfig(username="admin", password_hash=hashed, origin=origin)
    file = tmp_path / "admin.json"
    file.write_text(
        json.dumps(
            {
                "username": "admin",
                "password_hash": hashed,
                "origin": ORIGIN,
                "allow_loopback_http": True,
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Invalid ADMIN_CONFIG_FILE"):
        load_admin_config(file, production=True)
    file.write_text(password, encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid ADMIN_CONFIG_FILE") as exc:
        load_admin_config(file)
    assert password not in str(exc.value)


async def test_login_body_deadline_and_duplicate_cookie_rejection(
    admin_fixture: AdminFixture,
) -> None:
    f = admin_fixture

    async def slow_body():
        yield b"{"
        await asyncio.sleep(10)
        yield b"}"

    response = await f.client.post(
        "/v1/admin/auth/login",
        content=slow_body(),
        headers={"Origin": ORIGIN, "Content-Type": "application/json"},
    )
    assert response.status_code == 408
    await f.login()
    token = f.client.cookies.get(COOKIE)
    response = await f.client.get(
        "/v1/admin/jobs", headers={"Cookie": f"{COOKIE}={token}; {COOKIE}={token}"}
    )
    assert response.status_code == 401


async def test_https_secure_cookie_and_configured_lifespan(
    admin_fixture: AdminFixture, tmp_path
) -> None:
    f = admin_fixture
    data = f.config.model_dump(mode="json")
    data.update(
        origin="https://localhost:8000",
        allow_loopback_http=False,
        password_hash=f.config.password_hash.get_secret_value(),
    )
    path = tmp_path / "admin.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    settings = Settings(
        _env_file=None,
        app_env="production",
        database_url=f.url.set(drivername="postgresql").render_as_string(hide_password=False),
        redis_url="redis://127.0.0.1:16387/0",
        qdrant_url="http://127.0.0.1:56337",
        admin_config_file=path,
    )
    app = create_app(settings=settings, checks=HealthChecks(checks={}))
    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="https://localhost:8000"
        ) as client,
    ):
        response = await client.post(
            "/v1/admin/auth/login",
            headers={"Origin": "https://localhost:8000"},
            json={"username": "admin", "password": f.password},
        )
        assert response.status_code == 200
        assert "Secure" in response.headers["set-cookie"]
        assert (await client.get("/v1/admin/jobs")).status_code == 200
    assert app.state.admin_authentication is None


async def test_actual_loopback_http_cookie_security_and_csrf(admin_fixture: AdminFixture) -> None:
    f = admin_fixture
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen()
    origin = f"http://127.0.0.1:{listener.getsockname()[1]}"
    config = f.config.model_copy(update={"origin": origin})
    server_engine = build_engine(f.url)
    server = uvicorn.Server(
        uvicorn.Config(
            create_app(
                checks=HealthChecks(checks={}),
                admin_services=AdminServices(server_engine, config),
            ),
            log_level="critical",
            access_log=False,
            lifespan="on",
        )
    )

    def run():
        async def serve():
            try:
                await server.serve(sockets=[listener])
            finally:
                # Engine is owned by the injected fixture in this actual server thread.
                await server_engine.dispose()

        with asyncio.Runner(loop_factory=asyncio.SelectorEventLoop) as runner:
            runner.run(serve())

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    try:
        for _ in range(100):
            if server.started:
                break
            await asyncio.sleep(0.02)
        assert server.started
        async with httpx.AsyncClient(base_url=origin, trust_env=False) as client:
            response = await client.post(
                "/v1/admin/auth/login",
                headers={"Origin": origin},
                json={"username": "admin", "password": f.password},
            )
            assert response.status_code == 200
            cookie = response.headers["set-cookie"].lower()
            assert "httponly" in cookie and "samesite=strict" in cookie and "max-age=3600" in cookie
            assert "path=/v1/admin" in cookie and "secure;" not in cookie
            headers = {"Origin": origin, "X-CSRF-Token": response.json()["csrf_token"]}
            assert (await client.post("/v1/admin/auth/logout")).status_code == 403
            assert (await client.post("/v1/admin/auth/logout", headers=headers)).status_code == 204
            assert (await client.get("/v1/admin/documents")).status_code == 401
        print("T27 actual loopback HTTP: cookie/login/CSRF/logout/replay PASS")
    finally:
        server.should_exit = True
        await asyncio.to_thread(thread.join, 10)
        listener.close()
        assert not thread.is_alive()
