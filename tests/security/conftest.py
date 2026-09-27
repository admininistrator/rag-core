"""Local real HTTP key service and generated RSA material; no fixed credentials."""

import json
import threading
import time
from contextlib import suppress
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa


@pytest.fixture(scope="session")
def keypairs():
    result = []
    for kid in ("first", "second"):
        private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public = jwt.algorithms.RSAAlgorithm.to_jwk(private.public_key(), as_dict=True)
        public.update(kid=kid, alg="RS256", use="sig", key_ops=["verify"])
        result.append((private, public))
    return result


@pytest.fixture
def jwks_server(keypairs):
    state = SimpleNamespace(
        body=json.dumps({"keys": [keypairs[0][1]]}).encode(), status=200, requests=[], delay=0
    )

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            state.requests.append(self.path)
            time.sleep(state.delay)
            self.send_response(state.status)
            self.send_header("Content-Type", "application/json")
            if state.status == 302:
                self.send_header("Location", "/attacker")
            self.send_header("Content-Length", str(len(state.body)))
            self.end_headers()
            # Expected socket closure when testing the client's deadline.
            with suppress(BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                self.wfile.write(state.body)

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    state.url = f"http://127.0.0.1:{server.server_port}/jwks"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield state
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
