"""Development-only RSA/JWKS/token CLI; secrets are written to files, never stdout."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from uuid import uuid4

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from rag_core.auth.config import AuthConfig


def _write_new(path: Path, content: bytes) -> None:
    # Exclusive creation prevents silent replacement. Windows uses inherited ACLs;
    # the operator must restrict the parent directory to the current account.
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as stream:
        stream.write(content)


def initialize(directory: Path, *, app_id: str, port: int) -> None:
    origin = f"http://127.0.0.1:{port}"
    service_key = secrets.token_urlsafe(32)
    config = AuthConfig.model_validate(
        {
            "allow_loopback_http": True,
            "apps": [
                {
                    "app_id": app_id,
                    "service_key_sha256": hashlib.sha256(service_key.encode()).hexdigest(),
                    "issuer": origin,
                    "audience": f"rag-core:{app_id}",
                    "jwks_url": f"{origin}/.well-known/jwks.json",
                }
            ],
        }
    )
    directory.mkdir(mode=0o700, parents=True, exist_ok=False)
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public: dict[str, Any] = jwt.algorithms.RSAAlgorithm.to_jwk(key.public_key(), as_dict=True)
    public.update(kid=uuid4().hex, alg="RS256", use="sig", key_ops=["verify"])
    _write_new(
        directory / "private.pem",
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ),
    )
    _write_new(directory / "jwks.json", json.dumps({"keys": [public]}).encode())
    _write_new(directory / "service-key", service_key.encode())
    _write_new(directory / "apps.json", config.model_dump_json(indent=2).encode())


def issue(directory: Path, *, subject: str, output: Path, ttl: int) -> None:
    if not subject.strip() or len(subject) > 256 or not 1 <= ttl <= 3600:
        raise ValueError("invalid subject or TTL")
    config = AuthConfig.model_validate_json((directory / "apps.json").read_bytes())
    app = config.apps[0]
    kid = json.loads((directory / "jwks.json").read_bytes())["keys"][0]["kid"]
    now = int(time.time())
    token = jwt.encode(
        {
            "sub": subject,
            "app_id": app.app_id,
            "iss": app.issuer,
            "aud": app.audience,
            "iat": now,
            "nbf": now,
            "exp": now + ttl,
        },
        (directory / "private.pem").read_bytes(),
        algorithm="RS256",
        headers={"kid": kid},
    )
    _write_new(output, token.encode())


def serve(directory: Path, port: int) -> None:
    class PublicJWKS(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.path != "/.well-known/jwks.json":
                self.send_error(404)
                return
            try:
                # Re-read only the public file for rotation. Never serve a directory.
                body = (directory / "jwks.json").read_bytes()
            except OSError:
                self.send_error(503)
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: Any) -> None:
            pass  # Never log request paths, query strings or credential attempts.

    with ThreadingHTTPServer(("127.0.0.1", port), PublicJWKS) as server:
        server.serve_forever()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Create new local dev credentials (never overwrite)")
    init.add_argument("--directory", type=Path, default=Path(".local/auth"))
    init.add_argument("--app-id", default="local-dev")
    init.add_argument("--port", type=int, default=8765)
    token = commands.add_parser("token", help="Write a short-lived JWT to a new file")
    token.add_argument("--directory", type=Path, default=Path(".local/auth"))
    token.add_argument("--subject", required=True)
    token.add_argument("--output", type=Path, required=True)
    token.add_argument("--ttl", type=int, default=300)
    server = commands.add_parser("serve", help="Serve only public JWKS on literal loopback")
    server.add_argument("--directory", type=Path, default=Path(".local/auth"))
    server.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    try:
        if args.command == "init":
            if not 1 <= args.port <= 65535:
                raise ValueError("invalid port")
            initialize(args.directory, app_id=args.app_id, port=args.port)
        elif args.command == "token":
            issue(args.directory, subject=args.subject, output=args.output, ttl=args.ttl)
        else:
            serve(args.directory, args.port)
        print("LOCAL ISSUER: OK (credentials not displayed)")
        return 0
    except (OSError, ValueError, KeyError, jwt.PyJWTError):
        print("LOCAL ISSUER: FAILED (check paths, configuration and exclusive output files)")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
