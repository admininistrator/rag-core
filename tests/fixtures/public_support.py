"""Production app/lifespan over real dependencies; native LLM fixture only when requested."""

import hashlib
import json
import os
import secrets
import socket
import time
from contextlib import AsyncExitStack, asynccontextmanager
from types import SimpleNamespace

import httpx
import httpx2
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa

from rag_core.api.app import create_app
from rag_core.api.health import build_health_checks
from rag_core.api.runtime import ApiConfig
from rag_core.config import Settings
from rag_core.domain.streaming import StreamPolicy
from tests.fixtures.streaming_support import NativeWireFixture, serve


@asynccontextmanager
async def public_environment(f, provider, monkeypatch=None, *, live=False):
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    origin = f"http://127.0.0.1:{listener.getsockname()[1]}"
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public = jwt.algorithms.RSAAlgorithm.to_jwk(private.public_key(), as_dict=True)
    public.update(kid="t26", alg="RS256", use="sig", key_ops=["verify"])
    key = secrets.token_urlsafe(32)
    auth_path = f.tmp / "apps.json"
    apps = [
        {
            "app_id": app,
            "service_key_sha256": hashlib.sha256(service.encode()).hexdigest(),
            "issuer": "t26-issuer",
            "audience": "t26-core",
            "jwks_url": origin + "/.well-known/jwks.json",
        }
        for app, service in [(f.principal.app_id, key), ("other-app", "other-" + key)]
    ]
    auth_path.write_text(json.dumps({"apps": apps, "allow_loopback_http": True}))
    config_path = f.tmp / "api.json"
    config_path.write_text(
        ApiConfig(
            provider=provider,
            model_fingerprint=f.config.model_fingerprint,
            inference_url=f.config.inference_url,
            temp_root=f.tmp / "api-temp",
            stream=StreamPolicy(heartbeat_seconds=0.05),
        ).model_dump_json()
    )
    settings = Settings(
        _env_file=None,
        app_env="test",
        database_url=f.pg_url.set(drivername="postgresql").render_as_string(hide_password=False),
        redis_url=os.environ["REDIS_URL"],
        qdrant_url=f.config.qdrant_url,
        database_password_file=None,
        auth_config_file=auth_path,
        storage_config_file=f.config.storage_config,
        api_config_file=config_path,
    )
    async with AsyncExitStack() as stack:
        wire = None
        if not live:
            assert monkeypatch is not None
            wire = NativeWireFixture(provider)
            upstream = await stack.enter_async_context(serve(wire.app))
            module = httpx if provider == "deepseek" else httpx2
            network = await stack.enter_async_context(module.AsyncClient(trust_env=False))

            async def translate(request):
                forwarded = network.build_request(
                    request.method,
                    upstream
                    + "/v1/"
                    + ("chat-completions" if provider == "deepseek" else "messages"),
                    content=request.content,
                )
                return await network.send(forwarded, stream=True)

            import rag_core.api.runtime as runtime

            real_provider = (
                runtime.DeepSeekProvider if provider == "deepseek" else runtime.AnthropicProvider
            )
            pool = await stack.enter_async_context(
                module.AsyncClient(transport=module.MockTransport(translate), trust_env=False)
            )
            monkeypatch.setenv(provider.upper() + "_API_KEY", "synthetic-key-never-live")
            monkeypatch.setenv(provider.upper() + "_MODEL", "synthetic-model")
            monkeypatch.setattr(
                runtime,
                "DeepSeekProvider" if provider == "deepseek" else "AnthropicProvider",
                lambda config, _owned_pool: real_provider(config, pool),
            )
        app = create_app(settings=settings, checks=build_health_checks(settings))

        @app.get("/.well-known/jwks.json")
        async def jwks():
            return {"keys": [public]}

        def headers(user=f.principal.user_id, app_id=f.principal.app_id):
            now = int(time.time())
            token = jwt.encode(
                {
                    "sub": user,
                    "app_id": app_id,
                    "iss": "t26-issuer",
                    "aud": "t26-core",
                    "iat": now,
                    "nbf": now,
                    "exp": now + 600,
                },
                private,
                algorithm="RS256",
                headers={"kid": "t26"},
            )
            return {
                "Authorization": "Bearer " + token,
                "X-RAG-Service-Key": key if app_id == f.principal.app_id else "other-" + key,
            }

        base_url = await stack.enter_async_context(serve(app, listener))
        client = await stack.enter_async_context(
            httpx.AsyncClient(base_url=base_url, trust_env=False, timeout=130, headers=headers())
        )
        yield SimpleNamespace(
            client=client,
            app=app,
            headers=headers,
            wire=wire,
            services=app.state.public_services,
            base_url=base_url,
        )


async def upload_fixture(
    f, text="Hanoi is the capital of Vietnam. Hà Nội là thủ đô của Việt Nam.\n"
):
    data = text.encode()
    key = "allowed/t26-" + secrets.token_hex(16) + ".txt"
    result = f.uploader.put_object(Bucket="rag-core-storage-test", Key=key, Body=data)
    return {
        "external_upload_id": secrets.token_hex(16),
        "filename": "capital.txt",
        "content_type": "text/plain",
        "source": {
            "storage_alias": "fixture",
            "bucket": "rag-core-storage-test",
            "key": key,
            "version_id": result["VersionId"],
            "sha256": hashlib.sha256(data).hexdigest(),
        },
    }
