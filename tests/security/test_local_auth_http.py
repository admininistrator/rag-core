"""DoD-2: local CLI signs a real JWT, consumed by a real loopback HTTP API."""

import json
import socket
import subprocess
import sys
import threading
import time
from contextlib import contextmanager
from typing import Annotated

import httpx
import pytest
import uvicorn
from fastapi import Depends

from rag_core.api.app import create_app
from rag_core.api.auth import require_principal
from rag_core.api.health import HealthChecks
from rag_core.auth import Principal
from rag_core.config import Settings
from rag_core.contracts.v1 import ErrorEnvelope, SessionCreateRequest

pytestmark = [pytest.mark.security, pytest.mark.integration]


def cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "rag_core.auth.local_issuer", *map(str, args)],
        capture_output=True,
        text=True,
        timeout=15,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )


@contextmanager
def api_server(config):
    settings = Settings(
        _env_file=None,
        database_url="postgresql://host/db",
        redis_url="redis://host/0",
        qdrant_url="http://host:6333",
        auth_config_file=config,
    )
    # No database/provider is exercised: this endpoint tests only the real auth path.
    app = create_app(settings=settings, checks=HealthChecks(checks={}))

    @app.post("/v1/auth-test")
    async def probe(
        body: SessionCreateRequest, principal: Annotated[Principal, Depends(require_principal)]
    ):
        return {"app_id": principal.app_id, "user_id": principal.user_id}

    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
        server = uvicorn.Server(uvicorn.Config(app, log_level="error", access_log=False))
        thread = threading.Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
        thread.start()
        try:
            deadline = time.monotonic() + 10
            while not server.started and thread.is_alive() and time.monotonic() < deadline:
                time.sleep(0.02)
            assert server.started, "Local test API failed to start"
            yield f"http://127.0.0.1:{port}"
        finally:
            server.should_exit = True
            thread.join(timeout=10)
            assert not thread.is_alive(), "Local test API did not stop"


def test_cli_jwt_over_real_http_and_revocation(tmp_path):
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        jwks_port = reservation.getsockname()[1]
    directory = tmp_path / "auth"
    initialized = cli("init", "--directory", directory, "--port", jwks_port)
    assert initialized.returncode == 0, initialized.stdout
    assert cli("init", "--directory", directory, "--port", jwks_port).returncode == 1
    token_path = directory / "user.jwt"
    issued = cli(
        "token", "--directory", directory, "--subject", "http-user", "--output", token_path
    )
    assert issued.returncode == 0, issued.stdout
    assert (
        cli("token", "--directory", directory, "--subject", "x", "--output", token_path).returncode
        == 1
    )
    token = token_path.read_text()
    service_key = (directory / "service-key").read_text()
    assert token not in issued.stdout and service_key not in initialized.stdout
    config_path = directory / "apps.json"
    config = json.loads(config_path.read_bytes())
    config.update(cache_ttl_seconds=1, refresh_interval_seconds=1)
    config_path.write_text(json.dumps(config))
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "rag_core.auth.local_issuer",
            "serve",
            "--directory",
            str(directory),
            "--port",
            str(jwks_port),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )
    try:
        with httpx.Client(timeout=3, trust_env=False) as client:
            origin = f"http://127.0.0.1:{jwks_port}"
            deadline = time.monotonic() + 10
            while True:
                assert process.poll() is None, "Local issuer process failed"
                try:
                    if client.get(origin + "/.well-known/jwks.json").status_code == 200:
                        break
                except httpx.ConnectError:
                    pass
                assert time.monotonic() < deadline, "Local JWKS service did not start"
                time.sleep(0.05)
            for path in ("/private.pem", "/service-key", "/apps.json", "/../private.pem"):
                assert client.get(origin + path).status_code == 404
            with api_server(config_path) as api:
                endpoint = api + "/v1/auth-test"
                headers = {"Authorization": f"Bearer {token}", "X-RAG-Service-Key": service_key}
                body = {"external_session_id": "http-test-session"}
                response = client.post(endpoint, headers=headers, json=body)
                assert response.status_code == 200
                assert response.json() == {"app_id": "local-dev", "user_id": "http-user"}
                missing = client.post(endpoint, json=body)
                assert missing.status_code == 401
                ErrorEnvelope.model_validate(missing.json())
                assert (
                    client.post(
                        endpoint, headers=headers, json={**body, "user_id": "forged"}
                    ).status_code
                    == 422
                )
                assert client.get(api + "/v1/not-implemented", headers=headers).status_code == 404
                # Remove the public signing key. Real elapsed cache TTL, no fake clock.
                (directory / "jwks.json").write_text('{"keys": []}')
                time.sleep(1.1)
                revoked = client.post(endpoint, headers=headers, json=body)
                assert revoked.status_code == 503
                ErrorEnvelope.model_validate(revoked.json())
                assert token not in revoked.text and service_key not in revoked.text
        print(
            "REAL HTTP AUTH: PASS; CLI RS256 -> public JWKS -> protected API 200; "
            "missing credentials 401; forged identity 422; unmounted route 404; "
            "empty JWKS after TTL 503; private files 404; no credentials displayed"
        )
    finally:
        process.terminate()
        process.wait(timeout=10)
