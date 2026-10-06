"""Real loopback HTTP API/provider protocol fixtures; NOT a live LLM service."""

import asyncio
import hashlib
import json
import secrets
import socket
import time
from contextlib import asynccontextmanager
from types import SimpleNamespace

import httpx
import httpx2
import jwt
import uvicorn
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import FastAPI, Request
from pydantic import SecretStr
from starlette.responses import JSONResponse, StreamingResponse

from rag_core.adapters.llm.anthropic import AnthropicProvider
from rag_core.adapters.llm.config import AnthropicSettings, DeepSeekSettings
from rag_core.adapters.llm.deepseek import DeepSeekProvider
from rag_core.adapters.persistence.citations import PostgresCitationRepository
from rag_core.api.app import create_app
from rag_core.api.health import HealthChecks
from rag_core.api.streaming import build_stream_router
from rag_core.application.admission import QueryAdmission
from rag_core.application.answers import AnswerAssembler, AnswerPipeline
from rag_core.application.query import QueryPreparation
from rag_core.application.retrieval import RetrievalPipeline
from rag_core.application.streaming import StreamingAnswerPipeline
from rag_core.config import Settings
from rag_core.domain.query import DomainRegistry, builtin_domains
from rag_core.domain.streaming import StreamPolicy
from tests.contract.test_llm_providers import (
    MODEL,
    SYNTHETIC_KEY,
    frame,
    json_response,
    stream_payloads,
)
from tests.fixtures.answer_support import good_answer


@asynccontextmanager
async def serve(app, listener=None):
    owned = listener is None
    listener = listener or socket.socket()
    if owned:
        listener.bind(("127.0.0.1", 0))
    listener.setblocking(False)
    server = uvicorn.Server(uvicorn.Config(app, log_level="critical", access_log=False))
    task = asyncio.create_task(server.serve(sockets=[listener]))
    try:
        async with asyncio.timeout(10):
            while not server.started:
                assert not task.done(), "loopback server exited before startup"
                await asyncio.sleep(0.01)
        yield f"http://127.0.0.1:{listener.getsockname()[1]}"
    finally:
        server.should_exit = True
        await asyncio.wait_for(task, 10)
        listener.close()


class NativeWireFixture:
    def __init__(self, provider):
        self.provider = provider
        self.active = 0
        self.calls = []
        self.generation = []
        self.hold = False
        self.delay = 0.0
        self.failure = False
        self.usage = True
        self.responses = []
        self.gate = asyncio.Event()
        self.first = asyncio.Event()
        self.closed = asyncio.Event()
        self.raw_fragments = []
        self.app = FastAPI()

        @self.app.post("/v1/{operation}")
        async def protocol(request: Request, operation: str):
            body = await request.json()
            self.calls.append(body)
            data = json.loads(body["messages"][-1]["content"])
            if "answerability" not in data:
                answer = {"standalone_question": data["question"], "question_language": "vi"}
            else:
                self.generation.append(data)
                value = (
                    self.responses[min(len(self.generation) - 1, len(self.responses) - 1)]
                    if self.responses
                    else good_answer
                )
                answer = value(data) if callable(value) else value
            text = answer if isinstance(answer, str) else json.dumps(answer, ensure_ascii=False)
            if not body.get("stream"):
                return JSONResponse(json_response(provider, text, usage=self.usage))

            async def wire():
                self.active += 1
                self.closed.clear()
                try:
                    await asyncio.sleep(self.delay)
                    # Native schema; two deltas allow a genuinely partial public answer.
                    split = text.index(" ") + 1
                    # First native delta ends after the first complete cited sentence.
                    if ". " in text:
                        split = text.index(". ") + 2
                    elif "]. " in text:
                        split = text.index("]. ") + 3
                    payloads = stream_payloads(provider, text=text[:split], usage=self.usage)
                    delta_index = 2 if provider == "deepseek" else 3
                    for payload in payloads[: delta_index + 1]:
                        packet = frame(payload, provider, "\r\n")
                        # Split the actual TCP response into individual UTF-8 bytes.
                        for byte in packet:
                            piece = bytes([byte])
                            self.raw_fragments.append(piece)
                            yield piece
                    self.first.set()
                    if self.hold:
                        await self.gate.wait()
                    if self.failure:
                        # A native technical error, not a fabricated insufficient result.
                        if provider == "anthropic":
                            yield frame(
                                {
                                    "type": "error",
                                    "error": {
                                        "type": "api_error",
                                        "message": "PRIVATE UPSTREAM ERROR",
                                    },
                                },
                                provider,
                            )
                        else:
                            yield b'data: {"error":{"message":"PRIVATE UPSTREAM ERROR"}}\r\n\r\n'
                        return
                    delta = payloads[delta_index].copy()
                    if provider == "deepseek":
                        delta["choices"] = [
                            {"index": 0, "delta": {"content": text[split:]}, "finish_reason": None}
                        ]
                    else:
                        delta["delta"] = {"type": "text_delta", "text": text[split:]}
                    yield frame(delta, provider)
                    for payload in payloads[delta_index + 1 :]:
                        yield frame(payload, provider)
                    if provider == "deepseek":
                        yield b"data: [DONE]\n\n"
                finally:
                    self.active -= 1
                    self.closed.set()

            return StreamingResponse(wire(), media_type="text/event-stream")


@asynccontextmanager
async def streaming_environment(
    e, selector, tmp_path, *, provider="deepseek", policy=None, answer_policy=None
):
    policy = policy or StreamPolicy(heartbeat_seconds=0.05)
    fixture = NativeWireFixture(provider)
    module = httpx if provider == "deepseek" else httpx2
    async with (
        serve(fixture.app) as upstream_url,
        module.AsyncClient(trust_env=False, timeout=10) as network,
    ):

        async def translate(request):
            # Routing-only synthetic HTTPS transport -> real loopback fixture HTTP.
            # All request/JSON/SSE decoding and close behavior use actual native adapters.
            forwarded = network.build_request(
                request.method,
                upstream_url
                + "/v1/"
                + ("chat-completions" if provider == "deepseek" else "messages"),
                content=request.content,
            )
            return await network.send(forwarded, stream=True)

        config_class = DeepSeekSettings if provider == "deepseek" else AnthropicSettings
        config = config_class(
            api_key=SecretStr(SYNTHETIC_KEY),
            model=MODEL,
            base_url="https://protocol.synthetic/v1",
            _env_file=None,
            max_attempts=1,
            timeout_seconds=10,
        )
        async with module.AsyncClient(
            transport=module.MockTransport(translate), trust_env=False
        ) as pool:
            llm = (
                DeepSeekProvider(config, pool)
                if provider == "deepseek"
                else AnthropicProvider(config, pool)
            )
            preparation = QueryPreparation(
                DomainRegistry(builtin_domains()), e.f.sessions, e.f.repo, e.tokenizer, llm
            )
            retrieval = RetrievalPipeline(e.models, e.models.expected_fingerprint)
            assembler = AnswerAssembler(
                selector,
                PostgresCitationRepository(e.f.engine, e.f.sessions),
                llm,
                e.tokenizer,
                answer_policy,
            )
            pipeline = StreamingAnswerPipeline(preparation, retrieval, selector, assembler, policy)
            json_pipeline = AnswerPipeline(preparation, retrieval, selector, assembler)
            admission = QueryAdmission(policy.concurrency, policy.queue_size, policy.queue_timeout)

            listener = socket.socket()
            listener.bind(("127.0.0.1", 0))
            origin = f"http://127.0.0.1:{listener.getsockname()[1]}"
            private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            public = jwt.algorithms.RSAAlgorithm.to_jwk(private.public_key(), as_dict=True)
            public.update(kid="t25", alg="RS256", use="sig", key_ops=["verify"])
            service_key = secrets.token_urlsafe(32)
            auth_path = tmp_path / "apps.json"
            auth_path.write_text(
                json.dumps(
                    {
                        "apps": [
                            {
                                "app_id": e.f.owner.app_id,
                                "service_key_sha256": hashlib.sha256(
                                    service_key.encode()
                                ).hexdigest(),
                                "issuer": "t25-issuer",
                                "audience": "t25-core",
                                "jwks_url": origin + "/.well-known/jwks.json",
                            }
                        ],
                        "allow_loopback_http": True,
                    }
                ),
                encoding="utf-8",
            )
            settings = Settings(
                _env_file=None,
                database_url="postgresql://host/db",
                redis_url="redis://host/0",
                qdrant_url="http://host:6333",
                auth_config_file=auth_path,
            )
            app = create_app(settings=settings, checks=HealthChecks(checks={}))
            app.include_router(build_stream_router(pipeline, admission, policy))

            @app.get("/.well-known/jwks.json")
            async def jwks():
                return {"keys": [public]}

            now = int(time.time())
            token = jwt.encode(
                {
                    "sub": e.f.owner.user_id,
                    "app_id": e.f.owner.app_id,
                    "iss": "t25-issuer",
                    "aud": "t25-core",
                    "iat": now,
                    "nbf": now,
                    "exp": now + 600,
                },
                private,
                algorithm="RS256",
                headers={"kid": "t25"},
            )
            async with (
                serve(app, listener) as base_url,
                httpx.AsyncClient(
                    base_url=base_url,
                    trust_env=False,
                    timeout=20,
                    headers={
                        "Authorization": "Bearer " + token,
                        "X-RAG-Service-Key": service_key,
                    },
                ) as client,
            ):
                yield SimpleNamespace(
                    client=client,
                    admission=admission,
                    wire=fixture,
                    pipeline=json_pipeline,
                    app=app,
                    llm=llm,
                )


async def events(response, *, comments=None):
    fields = {}
    async for line in response.aiter_lines():
        if line.startswith(":"):
            if comments is not None:
                comments.append(line)
        elif line:
            key, value = line.split(":", 1)
            fields[key] = value.lstrip(" ")
        elif fields:
            yield {
                "event": fields["event"],
                "id": int(fields["id"]),
                "data": json.loads(fields["data"]),
            }
            fields = {}


async def released(env):
    async with asyncio.timeout(3):
        while env.admission.active or env.admission.waiting or env.wire.active:
            await asyncio.sleep(0.01)
