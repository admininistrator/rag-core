"""Actual HTTP/JWT/MinIO/PG/Redis/worker/Qdrant/BGE; LLM wire explicitly synthetic."""

import asyncio
import hashlib
import json
import os
import subprocess
import sys
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text

from rag_core.contracts.v1 import QueryResponse
from scripts.demo_app import lifecycle, read_answer
from tests.fixtures.public_support import public_environment, upload_fixture
from tests.integration.conftest import pg_url as integration_pg_url
from tests.integration.test_ingestion_pipeline import BUCKET, eventually, stack

__all__ = ["stack"]
pytestmark = [pytest.mark.e2e, pytest.mark.asyncio]
_broker_case = 0


@pytest.fixture
def pg_url():
    # Fresh real DB per case prevents failed outbox events crossing fixture app registries.
    yield from integration_pg_url.__wrapped__()


@pytest.fixture(autouse=True)
def isolated_broker(monkeypatch):
    global _broker_case
    assert _broker_case < 15, "Use the dedicated T26 project, at most15cases per run"
    monkeypatch.setenv("REDIS_URL", os.environ["REDIS_URL"].rsplit("/", 1)[0] + f"/{_broker_case}")
    _broker_case += 1


async def retained(f, source):
    data = f.uploader.get_object(Bucket=BUCKET, Key=source["key"], VersionId=source["version_id"])[
        "Body"
    ].read()
    assert hashlib.sha256(data).hexdigest() == source["sha256"]
    async with f.engine.connect() as conn:
        count = (
            await conn.execute(
                text("SELECT count(*) FROM chunks WHERE app_id=:app AND owner_id=:owner"),
                {"app": f.principal.app_id, "owner": f.principal.user_id},
            )
        ).scalar_one()
    assert count > 0
    from qdrant_client import AsyncQdrantClient, models

    from rag_core.domain.vectors import IndexProfile

    client = AsyncQdrantClient(url=f.config.qdrant_url, trust_env=False)
    try:
        result = await client.count(
            IndexProfile(f.config.model_fingerprint).collection_name,
            exact=True,
            count_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="app_id", match=models.MatchValue(value=f.principal.app_id)
                    ),
                    models.FieldCondition(
                        key="owner_id", match=models.MatchValue(value=f.principal.user_id)
                    ),
                ]
            ),
        )
        assert result.count == count
    finally:
        await client.close()


@pytest.mark.parametrize("provider", ["deepseek", "anthropic"])
async def test_complete_app_upload_history_stream_delete_retention(stack, monkeypatch, provider):
    f = stack
    registration = await upload_fixture(f)
    f.start_worker()
    async with public_environment(f, provider, monkeypatch) as e:
        ready = await e.client.get("/health/ready")
        assert ready.status_code == 200, ready.text

        async def dispatch(upload):
            metadata = await e.client.get("/v1/sessions/" + upload["session_id"])
            assert (
                metadata.status_code == 200
                and metadata.json()["scope_revision"] == upload["scope_revision"]
            )
            queued_retry = await e.client.post("/v1/jobs/" + upload["job"]["job_id"] + "/retry")
            assert queued_retry.status_code == 200 and queued_retry.json()["state"] == "queued"
            pending = await e.client.post(
                "/v1/query",
                json={
                    "session_id": upload["session_id"],
                    "question": "What is the capital of Vietnam?",
                },
            )
            assert pending.status_code == 409
            assert pending.json()["error"]["code"] == "documents_not_ready"
            assert await f.dispatcher.dispatch_one()

        result = await lifecycle(e.client, registration, on_registered=dispatch)
        assert result["answer"].answerability == result["final"].answerability == "supported"
        assert result["answer"].citations and result["final"].citations
        assert e.wire.calls[-1]["stream"] is True
        assert any("history" in c["messages"][-1]["content"] for c in e.wire.calls)
        deleted = await e.client.post(
            "/v1/query", json={"session_id": result["session"], "question": "Hanoi?"}
        )
        assert deleted.status_code == 410
        again = await e.client.delete("/v1/sessions/" + result["session"])
        assert again.status_code == 200
        fresh = (
            await e.client.post("/v1/sessions", json={"external_session_id": uuid4().hex})
        ).json()
        no_inherit = await e.client.post(
            "/v1/query", json={"session_id": fresh["session_id"], "question": "Hanoi?"}
        )
        assert (
            no_inherit.status_code == 409
            and no_inherit.json()["error"]["code"] == "no_session_documents"
        )
        await retained(f, registration["source"])
        assert e.services.admission.active == e.services.admission.waiting == 0
        print(
            f"T26 actual public HTTP lifecycle {provider} synthetic wire: app upload/history/JSON/SSE/delete + source/chunks/vectors retained PASS"
        )


async def register_ready(f, e, registration):
    session = (
        await e.client.post("/v1/sessions", json={"external_session_id": uuid4().hex})
    ).json()["session_id"]
    key = uuid4().hex
    path = f"/v1/sessions/{session}/documents"
    response = await e.client.post(path, json=registration, headers={"Idempotency-Key": key})
    assert response.status_code == 202, response.text
    upload = response.json()
    assert await f.dispatcher.dispatch_one()
    await eventually(lambda: f.job_ready(UUID(upload["job"]["job_id"])))
    return session, upload, key


async def test_ownership_idempotency_pagination_detach_and_citation(stack, monkeypatch):
    f = stack
    f.start_worker()
    registration = await upload_fixture(f)
    async with public_environment(f, "deepseek", monkeypatch) as e:
        session, upload, key = await register_ready(f, e, registration)
        path = f"/v1/sessions/{session}/documents"
        duplicate = await e.client.post(path, json=registration, headers={"Idempotency-Key": key})
        assert (
            duplicate.status_code == 202
            and duplicate.json()["job"]["job_id"] == upload["job"]["job_id"]
        )
        mismatch = await e.client.post(
            path, json={**registration, "filename": "changed.txt"}, headers={"Idempotency-Key": key}
        )
        assert mismatch.status_code == 409
        listed = await e.client.get(path + "?limit=1")
        assert listed.status_code == 200 and len(listed.json()["documents"]) == 1
        second_registration = await upload_fixture(f)
        second = await e.client.post(
            path, json=second_registration, headers={"Idempotency-Key": uuid4().hex}
        )
        assert second.status_code == 202
        assert await f.dispatcher.dispatch_one()
        await eventually(lambda: f.job_ready(UUID(second.json()["job"]["job_id"])))
        first_page = (await e.client.get(path + "?limit=1")).json()
        assert first_page["next_cursor"]
        second_page = (
            await e.client.get(path + "?limit=1&cursor=" + first_page["next_cursor"])
        ).json()
        assert second_page["next_cursor"] is None
        assert (
            first_page["documents"][0]["document_id"] != second_page["documents"][0]["document_id"]
        )
        query = {
            "session_id": session,
            "domain": "document",
            "document_ids": [upload["document"]["document_id"]],
            "question": "What is the capital of Vietnam?",
        }
        answer = QueryResponse.model_validate((await e.client.post("/v1/query", json=query)).json())
        citation_path = f"/v1/sessions/{session}/citations/{answer.citations[0].chunk_id}"
        assert (await e.client.get(citation_path)).status_code == 200
        for headers in [e.headers("other-user"), e.headers(app_id="other-app")]:
            for protected in [
                f"/v1/sessions/{session}",
                path,
                "/v1/jobs/" + upload["job"]["job_id"],
                citation_path,
            ]:
                assert (await e.client.get(protected, headers=headers)).status_code == 404
        wrong = await e.client.post("/v1/query", json={**query, "document_ids": [str(uuid4())]})
        assert wrong.status_code == 404
        assert (
            await e.client.post("/v1/jobs/" + upload["job"]["job_id"] + "/retry")
        ).status_code == 409
        detached = await e.client.delete(path + "/" + upload["document"]["document_id"])
        assert detached.status_code == 200
        assert (await e.client.delete(path + "/" + upload["document"]["document_id"])).json()[
            "scope_revision"
        ] == detached.json()["scope_revision"]
        assert (await e.client.get(citation_path)).status_code == 404
        assert (await e.client.post("/v1/query", json=query)).status_code == 404
        replay = await e.client.post(path, json=registration, headers={"Idempotency-Key": key})
        assert replay.json()["document"]["link_status"] == "detached"
        await retained(f, registration["source"])
        print("T26 actual HTTP owner/app/session/idempotency/citation/detach/no-resurrection PASS")


async def test_public_input_insufficient_and_safe_error(stack, monkeypatch):
    f = stack
    f.start_worker()
    async with public_environment(f, "deepseek", monkeypatch) as e:
        session, _upload, _ = await register_ready(f, e, await upload_fixture(f))
        query = {"session_id": session, "question": "Capital?"}
        for change in [
            {"user_id": "FORGED PRIVATE"},
            {"history": [{"role": "system", "content": "PRIVATE"}]},
            {"question": " "},
            {"domain": "document"},
        ]:
            response = await e.client.post("/v1/query", json={**query, **change})
            assert response.status_code == 422 and "PRIVATE" not in response.text
            assert response.json()["error"]["code"] == "invalid_request"
        insufficient = {
            **query,
            "domain": "multilingual",
            "corpus_languages": ["en"],
            "answer_language": "vi",
        }
        response = await e.client.post("/v1/query", json=insufficient)
        assert response.status_code == 200, response.text
        result = QueryResponse.model_validate(response.json())
        assert (
            result.answerability == "insufficient_evidence"
            and not result.citations
            and not result.contexts
        )
        final = await read_answer(e.client, insufficient)
        assert final.answerability == "insufficient_evidence" and not final.citations
        assert e.wire.generation[-1]["answerability"] == "insufficient_evidence"
        e.wire.responses = ['{"answer":"PRIVATE invalid output","citations":[]}']
        response = await e.client.post("/v1/query", json=query)
        assert response.status_code == 502 and "PRIVATE" not in response.text
        assert response.json()["error"]["code"] == "invalid_citation"
        configured = e.app.state.public_services
        e.app.state.public_services = None
        try:
            unavailable = await e.client.get("/v1/sessions/" + session)
            assert unavailable.status_code == 503
            assert unavailable.json()["error"]["code"] == "dependency_unavailable"
        finally:
            e.app.state.public_services = configured
        print(
            "T26 public validation redaction + genuine pipeline insufficient (LLM wire synthetic) PASS"
        )


async def test_json_serialization_gate_shared_admission_and_disconnect(stack, monkeypatch):
    f = stack
    f.start_worker()
    async with public_environment(f, "deepseek", monkeypatch) as e:
        registration = await upload_fixture(f)
        session, upload, _ = await register_ready(f, e, registration)
        request = {"session_id": session, "question": "What is the capital of Vietnam?"}
        original = e.services.answers.answer
        leases = [
            await e.services.admission.acquire() for _ in range(e.services.policy.concurrency)
        ]
        try:
            for path in ["/v1/query", "/v1/query/stream"]:
                response = await e.client.post(path, json=request)
                assert response.status_code == 429 and response.headers["Retry-After"] == "1"
        finally:
            for lease in leases:
                lease.release()
        started, cancelled = asyncio.Event(), asyncio.Event()

        async def stall(*args):
            # Failure-only suspension at the actual application boundary, no fake success.
            started.set()
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()

        monkeypatch.setattr(e.services.answers, "answer", stall)
        call = asyncio.create_task(e.client.post("/v1/query", json=request))
        await asyncio.wait_for(started.wait(), 5)
        call.cancel()
        await asyncio.gather(call, return_exceptions=True)
        await asyncio.wait_for(cancelled.wait(), 5)
        await eventually(lambda: e.services.admission.active == 0)
        monkeypatch.setattr(e.services.answers, "answer", original)
        assert (await e.client.post("/v1/query", json=request)).status_code == 200

        async def detach_before_serialization(*args):
            result = await original(*args)
            await e.services.sessions.detach_document(
                f.principal, UUID(session), UUID(upload["document"]["document_id"])
            )
            return result

        monkeypatch.setattr(e.services.answers, "answer", detach_before_serialization)
        response = await e.client.post("/v1/query", json=request)
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "session_scope_changed"
        assert e.services.admission.active == e.services.admission.waiting == 0
        await retained(f, registration["source"])
        print(
            "T26 actual HTTP JSON: shared JSON/SSE 429, disconnected work cancelled, serialization scope gate PASS"
        )


async def test_standalone_cli_app_real_subprocess(stack, monkeypatch):
    f = stack
    f.start_worker()
    env = {**os.environ, "DATABASE_URL": f.pg_url.render_as_string(hide_password=False)}
    env.pop("DATABASE_PASSWORD_FILE", None)
    dispatcher = subprocess.Popen(
        [sys.executable, "-m", "rag_core.adapters.broker.dispatcher"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    f.processes.append(dispatcher)
    async with public_environment(f, "deepseek", monkeypatch) as e:
        source = f.tmp / "public-demo.txt"
        source.write_text(
            "Hanoi is the capital of Vietnam. Hà Nội là thủ đô của Việt Nam.\n", encoding="utf-8"
        )
        headers = e.headers()
        token, service = f.tmp / "demo.jwt", f.tmp / "service-key"
        token.write_text(headers["Authorization"].removeprefix("Bearer "))
        service.write_text(headers["X-RAG-Service-Key"])
        config = f.tmp / "demo.json"
        config.write_text(
            json.dumps(
                {
                    "api_url": e.base_url,
                    "s3_endpoint": "http://minio:9000",
                    "bucket": BUCKET,
                    "prefix": "allowed/",
                    "storage_alias": "fixture",
                    "fixture": str(source),
                    "jwt_file": str(token),
                    "service_key_file": str(service),
                    "uploader_key_file": "/run/secrets/minio_uploader_user",
                    "uploader_secret_file": "/run/secrets/minio_uploader_password",
                }
            )
        )
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            "scripts/demo_app.py",
            "--config",
            str(config),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), 130)
        except BaseException:
            process.kill()
            await process.wait()
            raise
        assert process.returncode == 0, "standalone demo failed; raw child output withheld"
        summary = json.loads(stdout)
        assert (
            summary["status"] == "PASS"
            and summary["source_retained"]
            and summary["session_deleted"]
        )
        assert (
            summary["json"] == summary["sse"] == "supported" and summary["output"] == "[REDACTED]"
        )
        assert headers["X-RAG-Service-Key"].encode() not in stdout + stderr
        async with f.engine.connect() as conn:
            rows = (
                (
                    await conn.execute(
                        text(
                            "SELECT status FROM sessions WHERE app_id=:app AND external_session_id LIKE 'demo-%'"
                        ),
                        {"app": f.principal.app_id},
                    )
                )
                .scalars()
                .all()
            )
            assert rows == ["deleted"]
        print(
            "T26 independent CLI subprocess: actual app S3 upload/dispatcher/worker/HTTP/own history/SSE/tombstone/source hash PASS"
        )
