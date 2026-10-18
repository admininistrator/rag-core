"""T28 local shells plus real PostgreSQL-backed API contracts consumed by the UI.

Client execution/visual observation is a separate manual gate, not claimed by HTML 200.
"""

from html.parser import HTMLParser
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import text

from rag_core.api.app import create_app
from rag_core.api.health import HealthChecks
from tests.fixtures.admin_support import AdminFixture
from tests.fixtures.admin_support import admin_fixture as shared_admin_fixture

admin_fixture = shared_admin_fixture
pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


class Markup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = []

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


@pytest.mark.parametrize("page", ["", "/documents", "/jobs", "/sessions", "/index", "/evaluations"])
async def test_local_shell_has_no_embedded_authority_or_private_data(admin_fixture, page):
    f = admin_fixture
    row = await f.seed("ready")
    response = await f.client.get("/admin" + page)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
    assert "script-src 'self'" in response.headers["content-security-policy"]
    assert "unsafe-inline" not in response.headers["content-security-policy"]
    for private in [
        f.password,
        f.config.password_hash.get_secret_value(),
        str(row["doc"]),
        "PRIVATE_SOURCE_KEY",
        "PRIVATE_CHUNK_ANSWER",
    ]:
        assert private not in response.text
    markup = Markup()
    markup.feed(response.text)
    ids = [attrs["id"] for _, attrs in markup.elements if "id" in attrs]
    assert len(ids) == len(set(ids))
    for tag, attrs in markup.elements:
        if tag in {"input", "select", "button"}:
            # Named form controls can shadow native submission/reset methods.
            assert not {attrs.get("id"), attrs.get("name")} & {"reset", "submit", "requestSubmit"}
        if tag in {"input", "select"} and attrs.get("type") != "checkbox":
            assert any(t == "label" and a.get("for") == attrs["id"] for t, a in markup.elements)
        assert not any(key.startswith("on") for key in attrs)
        if tag in {"script", "link"}:
            assert (attrs.get("src") or attrs.get("href")).startswith("/admin/assets/")
    assert (await f.client.get("/v1/admin/documents")).status_code == 401
    if page == "/evaluations":
        assert "No evaluation reports available" in response.text
    print("T28 shell", page or "/overview", "PASS: local assets/labels/CSP/no embedded data")


async def test_local_assets_unknown_routes_and_unconfigured_api():
    app = create_app(checks=HealthChecks(checks={}))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://localhost"
    ) as client:
        for name, mime in [("admin.js", "text/javascript"), ("admin.css", "text/css")]:
            response = await client.get("/admin/assets/" + name)
            assert response.status_code == 200 and response.headers["content-type"].startswith(mime)
            assert response.headers["x-content-type-options"] == "nosniff"
        assert (await client.get("/admin/assets/admin.html")).status_code == 404
        assert (await client.get("/admin/not-a-view")).status_code == 404
        assert (await client.get("/admin/assets/%2e%2e%2fconfig.py")).status_code == 404
        assert (await client.get("/v1/admin/auth/session")).status_code == 503
    print("T28 fail closed: no configured API ->503; asset/view allowlists PASS")


async def test_view_data_real_counts_filters_pagination_and_index(admin_fixture: AdminFixture):
    f = admin_fixture
    app = "views-" + uuid4().hex
    first = await f.seed("ready", app=app)
    await f.seed("failed", app=app)
    await f.login()
    current = (await f.client.get("/v1/admin/auth/session")).json()
    assert len(current["csrf_token"]) == 64
    params = {"app": app, "limit": 1}
    response = await f.client.get("/v1/admin/documents", params=params)
    body = response.json()
    assert len(body["items"]) == 1 and body["next_cursor"]
    other = (
        await f.client.get("/v1/admin/documents", params={**params, "cursor": body["next_cursor"]})
    ).json()
    assert other["next_cursor"] is None
    assert body["items"][0]["version_id"] != other["items"][0]["version_id"]
    assert (
        await f.client.get(
            "/v1/admin/documents",
            params={
                "app": app,
                "owner": "test-owner",
                "state": "ready",
                "content_type": "text/plain",
            },
        )
    ).json()["items"][0]["version_id"] == str(first["version"])
    for resource in ["documents", "jobs", "sessions", "index"]:
        response = await f.client.get("/v1/admin/" + resource, params={"app": app})
        assert response.status_code == 200
        assert response.json()["items"]
        assert "PRIVATE_" not in response.text and "<img" not in response.text
        assert (
            await f.client.get("/v1/admin/" + resource, params={"app": "missing-" + uuid4().hex})
        ).json()["items"] == []
    summary = (await f.client.get("/v1/admin/overview")).json()
    async with f.engine.connect() as conn:
        expected = (await conn.execute(text("SELECT count(*) FROM documents"))).scalar_one()
    assert summary["counts"]["documents"] == expected
    assert summary["sizes"]["metadata_database_bytes"] > 0
    assert summary["broker_queue_depth"] is None
    assert (await f.client.get("/v1/admin/jobs", params={"cursor": "invalid"})).status_code == 422
    print("T28 data PASS: actual PG counts/filtered keyset pages/index/empty/error")


async def test_ui_action_contract_csrf_errors_audit_and_retention(admin_fixture: AdminFixture):
    f = admin_fixture
    headers = await f.login()
    row = await f.seed("failed")
    path = f"/v1/admin/jobs/{row['job']}/retry"
    assert (await f.client.post(path)).status_code == 403
    assert (await f.client.post(path, headers=headers)).status_code == 200
    ready = await f.seed("ready")
    assert (
        await f.client.post(f"/v1/admin/jobs/{ready['job']}/retry", headers=headers)
    ).status_code == 409
    assert (
        await f.client.post(f"/v1/admin/jobs/{ready['job']}/reindex", headers=headers)
    ).status_code == 200
    links = await f.client.get(f"/v1/admin/sessions/{row['session']}/documents")
    assert links.status_code == 200 and links.json()["items"][0]["status"] == "attached"
    assert (
        await f.client.delete(
            f"/v1/admin/sessions/{row['session']}/documents/{row['doc']}", headers=headers
        )
    ).status_code == 200
    assert (
        await f.client.delete(f"/v1/admin/sessions/{row['session']}", headers=headers)
    ).status_code == 200
    async with f.engine.connect() as conn:
        assert (
            await conn.execute(
                text("SELECT count(*) FROM documents WHERE document_id=:id"), {"id": row["doc"]}
            )
        ).scalar_one() == 1
        assert (
            await conn.execute(
                text(
                    "SELECT count(*) FROM audit_events WHERE target_id=:id AND action='job_retry' AND outcome='success'"
                ),
                {"id": row["job"]},
            )
        ).scalar_one() == 1
    assert (await f.client.post("/v1/admin/auth/logout", headers=headers)).status_code == 204
    assert (await f.client.get("/v1/admin/auth/session")).status_code == 401
    print(
        "T28 actions PASS: real PG CSRF403/illegal409/retry/reindex/audit/detach/retention/logout401"
    )
