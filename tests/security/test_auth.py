"""Authentication attacks, fail-closed configuration and real HTTP JWKS rotation."""

import asyncio
import hashlib
import json
import secrets
import time
from types import SimpleNamespace
from typing import Annotated

import httpx
import jwt
import pytest
from fastapi import Depends
from pydantic import ValidationError

from rag_core.api.app import create_app
from rag_core.api.auth import require_principal
from rag_core.api.health import HealthChecks
from rag_core.auth import AuthUnavailable, InvalidCredentials, Principal
from rag_core.auth.config import AuthConfig, load_auth_config
from rag_core.auth.verifier import Authenticator
from rag_core.config import Settings
from rag_core.contracts.v1 import ErrorEnvelope, SessionCreateRequest

pytestmark = [pytest.mark.security, pytest.mark.asyncio]


@pytest.fixture
def registry(jwks_server):
    service_key = secrets.token_urlsafe(32)
    data = {
        "allow_loopback_http": True,
        "cache_ttl_seconds": 10,
        "refresh_interval_seconds": 2,
        "apps": [
            {
                "app_id": "app-a",
                "issuer": "issuer-a",
                "audience": "rag-a",
                "jwks_url": jwks_server.url,
                "service_key_sha256": hashlib.sha256(service_key.encode()).hexdigest(),
            }
        ],
    }
    return data, service_key


def signed(keypairs, *, overrides=None, headers=None, key_index=0, remove=None):
    now = int(time.time())
    payload = {
        "sub": "user-a",
        "app_id": "app-a",
        "iss": "issuer-a",
        "aud": "rag-a",
        "iat": now,
        "nbf": now,
        "exp": now + 60,
    }
    payload.update(overrides or {})
    if remove:
        payload.pop(remove)
    return jwt.encode(
        payload,
        keypairs[key_index][0],
        algorithm="RS256",
        headers={"kid": keypairs[key_index][1]["kid"], **(headers or {})},
    )


async def test_verified_identity_ignores_unsigned_sources_and_signed_user_id(registry, keypairs):
    data, service = registry
    result = await Authenticator(AuthConfig.model_validate(data)).authenticate(
        service, signed(keypairs, overrides={"user_id": "forged", "jwks_url": "http://attacker"})
    )
    assert result == Principal("app-a", "user-a")


@pytest.mark.parametrize(
    "overrides",
    [
        {"iss": "evil"},
        {"aud": "other-app"},
        {"exp": 1},
        {"nbf": 4102444800},
        {"iat": 4102444800},
        {"app_id": "app-b"},
        {"sub": ""},
        {"sub": 42},
        {"sub": " "},
        {"sub": "x" * 257},
        {"exp": "4102444800"},
        {"nbf": False},
        {"exp": float("inf")},
        {"exp": float("nan")},
    ],
)
async def test_rejects_invalid_claims(registry, keypairs, overrides):
    data, service = registry
    with pytest.raises(InvalidCredentials):
        await Authenticator(AuthConfig.model_validate(data)).authenticate(
            service, signed(keypairs, overrides=overrides)
        )


@pytest.mark.parametrize("claim", ["sub", "app_id", "iss", "aud", "exp", "nbf", "iat"])
async def test_required_claims(registry, keypairs, claim):
    data, service = registry
    with pytest.raises(InvalidCredentials):
        await Authenticator(AuthConfig.model_validate(data)).authenticate(
            service, signed(keypairs, remove=claim)
        )


async def test_wrong_signature_and_disallowed_algorithms(registry, keypairs):
    data, service = registry
    auth = Authenticator(AuthConfig.model_validate(data))
    bad = signed(keypairs, key_index=1, headers={"kid": "first"})
    for token in (
        bad,
        jwt.encode({"sub": "x"}, "", algorithm="none"),
        jwt.encode({"sub": "x"}, secrets.token_urlsafe(32), algorithm="HS256"),
        "malformed",
        "a" * 16385,
    ):
        with pytest.raises(InvalidCredentials):
            await auth.authenticate(service, token)


@pytest.mark.parametrize(
    "headers",
    [
        {"jku": "http://attacker/jwks"},
        {"jwk": {"kty": "RSA"}},
        {"x5u": "https://attacker"},
        {"x5c": []},
        {"crit": ["b64"]},
        {"kid": "x" * 129},
    ],
)
async def test_token_cannot_select_jwks_or_critical_extensions(
    registry, keypairs, jwks_server, headers
):
    data, service = registry
    with pytest.raises(InvalidCredentials):
        await Authenticator(AuthConfig.model_validate(data)).authenticate(
            service, signed(keypairs, headers=headers)
        )
    assert jwks_server.requests == []


async def test_service_key_and_app_binding_even_with_shared_jwks(registry, keypairs, jwks_server):
    data, service = registry
    second_service = secrets.token_urlsafe(32)
    data["apps"].append(
        {
            **data["apps"][0],
            "app_id": "app-b",
            "service_key_sha256": hashlib.sha256(second_service.encode()).hexdigest(),
        }
    )
    auth = Authenticator(AuthConfig.model_validate(data))
    for wrong in ("", "short", secrets.token_urlsafe(32)):
        with pytest.raises(InvalidCredentials):
            await auth.authenticate(wrong, signed(keypairs))
    assert jwks_server.requests == []
    with pytest.raises(InvalidCredentials):
        await auth.authenticate(second_service, signed(keypairs))
    assert await auth.authenticate(second_service, signed(keypairs, overrides={"app_id": "app-b"}))
    assert await auth.authenticate(service, signed(keypairs))
    assert len(jwks_server.requests) == 2  # Caches are app-specific even with the same URL/kid.


async def test_rotation_revocation_ttl_failure_and_flood_bound(
    registry, keypairs, jwks_server, monkeypatch
):
    data, service = registry
    clock = [100.0]
    monkeypatch.setattr("rag_core.auth.verifier.time", SimpleNamespace(monotonic=lambda: clock[0]))
    auth = Authenticator(AuthConfig.model_validate(data))
    first, second = signed(keypairs), signed(keypairs, key_index=1)
    await asyncio.gather(*(auth.authenticate(service, first) for _ in range(10)))
    assert len(jwks_server.requests) == 1
    jwks_server.body = json.dumps({"keys": [pair[1] for pair in keypairs]}).encode()
    with pytest.raises(InvalidCredentials):
        await auth.authenticate(service, second)  # Unknown kid within refresh cooldown.
    clock[0] += 2
    await auth.authenticate(service, second)  # New kid triggers bounded early refresh.
    await auth.authenticate(service, first)  # Grace window includes both keys.
    assert len(jwks_server.requests) == 2
    jwks_server.body = json.dumps({"keys": [keypairs[1][1]]}).encode()
    clock[0] += 10
    with pytest.raises(InvalidCredentials):
        await auth.authenticate(service, first)  # Expired cache refetch removes old key.
    assert len(jwks_server.requests) == 3
    for n in range(10):
        with pytest.raises(InvalidCredentials):
            await auth.authenticate(service, signed(keypairs, headers={"kid": f"unknown-{n}"}))
    assert len(jwks_server.requests) == 3
    jwks_server.status = 503
    clock[0] += 10
    for _ in range(5):
        with pytest.raises(AuthUnavailable):
            await auth.authenticate(service, second)  # No stale success on outage.
    assert len(jwks_server.requests) == 4
    jwks_server.status = 200
    clock[0] += 2
    await auth.authenticate(service, second)
    assert len(jwks_server.requests) == 5


@pytest.mark.parametrize(
    "case",
    [
        "redirect",
        "bad-json",
        "oversize",
        "duplicate",
        "private",
        "bad-key",
        "too-many",
        "wrong-use",
        "weak-key",
    ],
)
async def test_bad_jwks_fails_closed(registry, keypairs, jwks_server, case):
    data, service = registry
    public = keypairs[0][1]
    if case == "redirect":
        jwks_server.status = 302
    elif case == "bad-json":
        jwks_server.body = b"not-json"
    elif case == "oversize":
        jwks_server.body = b" " * 131073
    else:
        entries = {
            "duplicate": [public, public],
            "private": [{**public, "d": "forbidden"}],
            "bad-key": [{**public, "n": "!"}],
            "too-many": [public] * 33,
            "wrong-use": [{**public, "use": "enc"}],
            "weak-key": [{**public, "n": "AQAB"}],
        }
        jwks_server.body = json.dumps({"keys": entries[case]}).encode()
    with pytest.raises((AuthUnavailable, InvalidCredentials)):
        await Authenticator(AuthConfig.model_validate(data)).authenticate(service, signed(keypairs))
    assert jwks_server.requests == ["/jwks"]  # No redirect followed.


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com/jwks",
        "file:///key",
        "http://localhost/jwks",
        "https://user:password@example.com/jwks",
        "https://example.com/jwks?secret=1",
        "https://example.com/jwks#fragment",
    ],
)
async def test_bad_trusted_url_rejected(registry, url):
    data, _ = registry
    data["apps"][0]["jwks_url"] = url
    with pytest.raises(ValidationError):
        AuthConfig.model_validate(data)


async def test_invalid_missing_and_production_configuration(registry, tmp_path):
    data, _ = registry
    path = tmp_path / "apps.json"
    with pytest.raises(AuthUnavailable, match="AUTH_CONFIG_FILE"):
        load_auth_config(path)
    for text in ("{}", "bad-json", '{"apps": []}', "x" * 262145):
        path.write_text(text)
        with pytest.raises(AuthUnavailable):
            load_auth_config(path)
    path.write_text(json.dumps(data))
    with pytest.raises(AuthUnavailable):
        load_auth_config(path, production=True)
    data["apps"].append(data["apps"][0])
    with pytest.raises(ValidationError):
        AuthConfig.model_validate(data)


def protected_app(config_path=None):
    settings = Settings(
        _env_file=None,
        database_url="postgresql://host/db",
        redis_url="redis://host/0",
        qdrant_url="http://host:6333",
        auth_config_file=config_path,
    )
    app = create_app(settings=settings, checks=HealthChecks(checks={}))

    @app.post("/v1/auth-test")
    async def probe(
        body: SessionCreateRequest, principal: Annotated[Principal, Depends(require_principal)]
    ):
        return {"app_id": principal.app_id, "user_id": principal.user_id}

    return app


async def test_http_guard_principal_injection_forged_body_and_safe_errors(
    registry, keypairs, tmp_path, caplog
):
    data, service = registry
    path = tmp_path / "apps.json"
    path.write_text(json.dumps(data))
    token = signed(keypairs)
    headers = {"Authorization": f"Bearer {token}", "X-RAG-Service-Key": service}
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=protected_app(path)), base_url="http://test"
    ) as client:
        body = {"external_session_id": "session"}
        ok = await client.post("/v1/auth-test", headers=headers, json=body)
        assert ok.status_code == 200 and ok.json() == {"app_id": "app-a", "user_id": "user-a"}
        for field in ("user_id", "app_id", "jwks_url"):
            bad = await client.post(
                "/v1/auth-test", headers=headers, json={**body, field: "forged"}
            )
            assert bad.status_code == 422
        for bad_headers in (
            {},
            {"Authorization": headers["Authorization"]},
            {"X-RAG-Service-Key": service},
            {**headers, "Authorization": "Bearer bad"},
        ):
            response = await client.post("/v1/auth-test", headers=bad_headers, json=body)
            assert response.status_code == 401
            ErrorEnvelope.model_validate(response.json())
            assert response.headers["www-authenticate"] == "Bearer"
            assert service not in response.text and token not in response.text
        duplicate = await client.post(
            "/v1/auth-test", headers=[*headers.items(), ("Authorization", "Bearer evil")], json=body
        )
        assert duplicate.status_code == 401
        assert (await client.get("/health/live")).status_code == 200
    assert token not in caplog.text and service not in caplog.text


async def test_missing_config_has_no_default_bypass():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=protected_app()), base_url="http://test"
    ) as client:
        for path in ("/v1", "/v1/auth-test", "/v1/query"):
            response = await client.post(path, json={"user_id": "forged"})
            assert response.status_code == 503
            ErrorEnvelope.model_validate(response.json())
        assert (await client.get("/health/live")).status_code == 200


async def test_jwks_timeout_and_cancel_are_bounded(registry, keypairs, jwks_server):
    data, service = registry
    data["jwks_timeout_seconds"] = 0.1
    jwks_server.delay = 0.5
    auth = Authenticator(AuthConfig.model_validate(data))
    started = time.monotonic()
    with pytest.raises(AuthUnavailable):
        await auth.authenticate(service, signed(keypairs))
    assert time.monotonic() - started < 1
    # Cancellation must propagate rather than become a successful principal or auth error.
    data["jwks_timeout_seconds"] = 3
    task = asyncio.create_task(
        Authenticator(AuthConfig.model_validate(data)).authenticate(service, signed(keypairs))
    )
    await asyncio.sleep(0.05)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


async def test_bad_config_stops_application_startup(tmp_path):
    with pytest.raises(AuthUnavailable, match="AUTH_CONFIG_FILE"):
        protected_app(tmp_path / "missing.json")
