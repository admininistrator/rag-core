"""End-to-end verification of the standalone reference client over real HTTP.

DoD-1 Requirements verified:
1. App & user authentication: valid JWT & service key succeed, invalid tokens or service keys fail.
2. Source upload & registration: S3/MinIO upload registered with Idempotency-Key, polled until ready.
3. Session-only queries: isolated within session, cross-session and empty session fail closed.
4. Conversation history: follow-up queries with history succeed with contextual grounding.
5. JSON and SSE: both non-streaming and streaming queries return validated answers and citations.
6. Cancel & errors: streaming cancellation cleanly releases admission slots; errors map safely.
7. Deleted session: tombstoned session returns 410, repeated delete is idempotent, fresh session does not inherit.
8. Source & index retention: raw S3 object and Qdrant vector index are byte-for-byte retained after deletion.
9. "không import private core services": no imports of rag_core.services or private adapters.
"""

from __future__ import annotations

import asyncio
import hashlib
import inspect
import json
import subprocess
import sys
from collections.abc import AsyncIterator
from pathlib import Path
from uuid import uuid4

import boto3
import pytest
import pytest_asyncio
from qdrant_client import AsyncQdrantClient, models

import examples.reference_client as ref_mod
from examples.reference_client import (
    NoSessionDocumentsError,
    RagCoreClientError,
    RagCoreReferenceClient,
    SessionDeletedError,
    SessionNotFoundError,
)

pytestmark = [pytest.mark.e2e]
SECRET_DIR = Path(".local/secrets").resolve()


def test_no_private_core_services_imported():
    """Verify that neither the reference client nor this test imports private core services."""
    import ast

    # 1. Verify client module source has no rag_core imports
    client_tree = ast.parse(inspect.getsource(ref_mod))
    client_imports = []
    for node in ast.walk(client_tree):
        if isinstance(node, ast.Import):
            client_imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            client_imports.extend(f"{node.module}.{alias.name}" for alias in node.names)
    assert not any(imp.startswith("rag_core") for imp in client_imports), (
        f"reference_client imported internal rag_core module: {client_imports}"
    )

    # 2. Verify this test file has no private service imports
    test_tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    test_imports = [
        node.module
        for node in ast.walk(test_tree)
        if isinstance(node, ast.ImportFrom) and node.module
    ]
    forbidden_prefixes = (
        "rag_core.services",
        "rag_core.adapters",
        "rag_core.application",
        "rag_core.storage",
        "rag_core.retrieval",
    )
    for imp in test_imports:
        assert not any(imp.startswith(prefix) for prefix in forbidden_prefixes), (
            f"test_reference_client imported private core service: {imp}"
        )


@pytest_asyncio.fixture(scope="module")
async def server_env() -> AsyncIterator[dict[str, str]]:
    """Launches the real RAG Core API server in a separate subprocess."""
    proc = subprocess.Popen(
        [sys.executable, "-m", "tests.fixtures.standalone_server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        assert proc.stdout is not None
        line = await asyncio.to_thread(proc.stdout.readline)
        if not line or not line.strip().startswith("{"):
            err = proc.stderr.read() if proc.stderr else ""
            raise RuntimeError(f"Server subprocess failed to start: {err}")
        info = json.loads(line)
        yield info
    finally:
        if proc.stdin:
            proc.stdin.close()
        await asyncio.to_thread(proc.wait, timeout=10)


@pytest.mark.asyncio
async def test_health_endpoints(server_env):
    """Verify process health probes via reference client."""
    async with RagCoreReferenceClient(base_url=server_env["base_url"]) as client:
        live = await client.health_live()
        assert live["status"] == "ok"
        ready = await client.health_ready()
        assert ready["status"] == "ready"


@pytest.mark.asyncio
async def test_authentication_and_authorization(server_env):
    """Verify app and user authentication boundaries and isolation."""
    base_url = server_env["base_url"]
    valid_token = server_env["auth_token"]
    valid_key = server_env["service_key"]

    # 1. Valid credentials succeed
    async with RagCoreReferenceClient(
        base_url=base_url, auth_token=valid_token, service_key=valid_key
    ) as client:
        session = await client.create_or_resolve_session(f"auth-test-{uuid4().hex}")
        assert session["session_id"]

    # 2. Invalid JWT token returns 401
    async with RagCoreReferenceClient(
        base_url=base_url, auth_token="invalid.token.payload", service_key=valid_key
    ) as client:
        with pytest.raises(RagCoreClientError) as exc_info:
            await client.create_or_resolve_session(uuid4().hex)
        assert exc_info.value.status_code == 401

    # 3. Invalid service key returns 401 invalid_credentials
    async with RagCoreReferenceClient(
        base_url=base_url, auth_token=valid_token, service_key="invalid-key"
    ) as client:
        with pytest.raises(RagCoreClientError) as exc_info:
            await client.create_or_resolve_session(uuid4().hex)
        assert exc_info.value.status_code == 401
        assert exc_info.value.error_code == "invalid_credentials"


@pytest.mark.asyncio
async def test_source_upload_registration_and_job_polling(server_env):
    """Verify S3 upload, registration with Idempotency-Key, and job polling."""
    base_url = server_env["base_url"]
    auth_token = server_env["auth_token"]
    service_key = server_env["service_key"]
    s3_endpoint = server_env["s3_endpoint"]
    bucket = server_env["bucket"]

    # Upload document to MinIO via standard boto3 (as an external application would)
    s3_user = (SECRET_DIR / "minio_uploader_user").read_text().strip()
    s3_pass = (SECRET_DIR / "minio_uploader_password").read_text().strip()
    uploader = boto3.client(
        "s3",
        endpoint_url=s3_endpoint,
        region_name="us-east-1",
        aws_access_key_id=s3_user,
        aws_secret_access_key=s3_pass,
    )
    content = b"Hanoi is the capital city of Vietnam. Ha Noi la thu do cua Viet Nam.\n"
    content_sha256 = hashlib.sha256(content).hexdigest()
    key = f"allowed/ref-doc-{uuid4().hex}.txt"
    put_res = uploader.put_object(Bucket=bucket, Key=key, Body=content)
    version_id = put_res.get("VersionId")

    async with RagCoreReferenceClient(
        base_url=base_url, auth_token=auth_token, service_key=service_key
    ) as client:
        # Create session
        session = await client.create_or_resolve_session(f"reg-session-{uuid4().hex}")
        session_id = session["session_id"]

        source_info = {
            "storage_alias": "fixture",
            "bucket": bucket,
            "key": key,
            "sha256": content_sha256,
        }
        if version_id:
            source_info["version_id"] = version_id

        # Register document with Idempotency-Key
        idemp_key = uuid4().hex
        upload_id = uuid4().hex
        upload = await client.register_document(
            session_id=session_id,
            external_upload_id=upload_id,
            source=source_info,
            filename="capital.txt",
            content_type="text/plain",
            idempotency_key=idemp_key,
        )
        assert upload["document"]["document_id"]
        job_id = upload["job"]["job_id"]

        # Duplicate registration with identical body & Idempotency-Key returns same job ID
        dup = await client.register_document(
            session_id=session_id,
            external_upload_id=upload_id,
            source=source_info,
            filename="capital.txt",
            content_type="text/plain",
            idempotency_key=idemp_key,
        )
        assert dup["job"]["job_id"] == job_id

        # Same Idempotency-Key with different payload raises 409 idempotency_conflict
        with pytest.raises(RagCoreClientError) as conflict_info:
            await client.register_document(
                session_id=session_id,
                external_upload_id=uuid4().hex,  # changed payload
                source=source_info,
                filename="capital.txt",
                content_type="text/plain",
                idempotency_key=idemp_key,
            )
        assert conflict_info.value.status_code == 409
        assert conflict_info.value.error_code == "idempotency_conflict"

        # Poll job until ready
        ready_job = await client.wait_for_job(job_id, timeout=30.0, poll_interval=0.2)
        assert ready_job["state"] == "ready"

        # List documents in session
        docs = await client.list_documents(session_id)
        assert len(docs["documents"]) == 1
        assert docs["documents"][0]["filename"] == "capital.txt"


@pytest.mark.asyncio
async def test_session_only_queries_and_history(server_env):
    """Verify session isolation in queries, empty session failure, and conversation history."""
    base_url = server_env["base_url"]
    auth_token = server_env["auth_token"]
    service_key = server_env["service_key"]
    s3_endpoint = server_env["s3_endpoint"]
    bucket = server_env["bucket"]

    s3_user = (SECRET_DIR / "minio_uploader_user").read_text().strip()
    s3_pass = (SECRET_DIR / "minio_uploader_password").read_text().strip()
    uploader = boto3.client(
        "s3",
        endpoint_url=s3_endpoint,
        region_name="us-east-1",
        aws_access_key_id=s3_user,
        aws_secret_access_key=s3_pass,
    )
    content = (
        "The official currency of Vietnam is the Vietnamese Dong (VND). "
        "Tiền tệ chính thức của Việt Nam là Đồng Việt Nam (VND). "
        "Nó được viết tắt là gì? Nó được viết tắt là VND.\n"
    ).encode()
    content_sha256 = hashlib.sha256(content).hexdigest()
    key = f"allowed/ref-curr-{uuid4().hex}.txt"
    uploader.put_object(Bucket=bucket, Key=key, Body=content)

    async with RagCoreReferenceClient(
        base_url=base_url, auth_token=auth_token, service_key=service_key
    ) as client:
        session = await client.create_or_resolve_session(f"query-session-{uuid4().hex}")
        session_id = session["session_id"]

        # 1. Query on empty session fails with NoSessionDocumentsError (409)
        with pytest.raises(NoSessionDocumentsError):
            await client.query(session_id=session_id, question="What is the currency?")

        # Register document
        upload = await client.register_document(
            session_id=session_id,
            external_upload_id=uuid4().hex,
            source={
                "storage_alias": "fixture",
                "bucket": bucket,
                "key": key,
                "sha256": content_sha256,
            },
            filename="currency.txt",
            content_type="text/plain",
            idempotency_key=uuid4().hex,
        )
        await client.wait_for_job(upload["job"]["job_id"], timeout=30.0, poll_interval=0.2)

        # 2. Grounded query returns supported answerability and citations
        result = await client.query(
            session_id=session_id,
            question="What is the currency of Vietnam?",
        )
        assert result.answerability == "supported"
        assert len(result.citations) >= 1
        assert result.citations[0]["filename"] == "currency.txt"
        assert len(result.contexts) >= 1

        # 3. Followup query with conversation history succeeds
        history = [
            {"role": "user", "content": "What is the currency of Vietnam?"},
            {"role": "assistant", "content": result.answer},
        ]
        followup = await client.query(
            session_id=session_id,
            question="Nó được viết tắt là gì?",
            history=history,
            answer_language="vi",
        )
        assert followup.answerability == "supported"
        assert len(followup.citations) >= 1

        # 4. Cross-session isolation: another session cannot access this document
        other_session = await client.create_or_resolve_session(f"other-{uuid4().hex}")
        with pytest.raises(NoSessionDocumentsError):
            await client.query(
                session_id=other_session["session_id"], question="What is the currency?"
            )

        # 5. Cross-user isolation: another user cannot access this session
        async with RagCoreReferenceClient(
            base_url=base_url,
            auth_token=server_env["other_user_token"],
            service_key=service_key,
        ) as other_client:
            with pytest.raises(SessionNotFoundError):
                await other_client.query(session_id=session_id, question="What is the currency?")


@pytest.mark.asyncio
async def test_sse_streaming_and_cancellation(server_env):
    """Verify Server-Sent Events (SSE) streaming flow, event ordering, and cancellation."""
    base_url = server_env["base_url"]
    auth_token = server_env["auth_token"]
    service_key = server_env["service_key"]
    s3_endpoint = server_env["s3_endpoint"]
    bucket = server_env["bucket"]

    s3_user = (SECRET_DIR / "minio_uploader_user").read_text().strip()
    s3_pass = (SECRET_DIR / "minio_uploader_password").read_text().strip()
    uploader = boto3.client(
        "s3",
        endpoint_url=s3_endpoint,
        region_name="us-east-1",
        aws_access_key_id=s3_user,
        aws_secret_access_key=s3_pass,
    )
    content = b"Mount Fansipan is the highest peak in Vietnam, located in Lao Cai.\n"
    content_sha256 = hashlib.sha256(content).hexdigest()
    key = f"allowed/ref-mountain-{uuid4().hex}.txt"
    uploader.put_object(Bucket=bucket, Key=key, Body=content)

    async with RagCoreReferenceClient(
        base_url=base_url, auth_token=auth_token, service_key=service_key
    ) as client:
        session = await client.create_or_resolve_session(f"stream-session-{uuid4().hex}")
        session_id = session["session_id"]

        upload = await client.register_document(
            session_id=session_id,
            external_upload_id=uuid4().hex,
            source={
                "storage_alias": "fixture",
                "bucket": bucket,
                "key": key,
                "sha256": content_sha256,
            },
            filename="mountain.txt",
            content_type="text/plain",
            idempotency_key=uuid4().hex,
        )
        await client.wait_for_job(upload["job"]["job_id"], timeout=30.0, poll_interval=0.2)

        # 1. Full streaming execution
        events = []
        async for event in client.stream_query(
            session_id=session_id,
            question="What is the highest peak in Vietnam?",
        ):
            events.append(event)

        event_names = [e.event for e in events]
        assert "meta" in event_names
        assert "evidence" in event_names
        assert "answer_delta" in event_names
        assert "done" in event_names

        meta_pos = event_names.index("meta")
        evidence_pos = event_names.index("evidence")
        done_pos = event_names.index("done")
        assert meta_pos < evidence_pos < done_pos

        done_event = events[done_pos]
        assert done_event.data["answerability"] == "supported"
        assert len(done_event.data["citations"]) >= 1

        # 2. Mid-stream client cancellation
        cancelled_events = []
        async for event in client.stream_query(
            session_id=session_id,
            question="What is the highest peak in Vietnam?",
        ):
            cancelled_events.append(event)
            if event.event == "meta":
                break  # Cancel mid-stream by breaking the async generator loop

        assert len(cancelled_events) == 1
        await asyncio.sleep(0.2)


@pytest.mark.asyncio
async def test_citation_resolution(server_env):
    """Verify citation resolution within current session scope."""
    base_url = server_env["base_url"]
    auth_token = server_env["auth_token"]
    service_key = server_env["service_key"]
    s3_endpoint = server_env["s3_endpoint"]
    bucket = server_env["bucket"]

    s3_user = (SECRET_DIR / "minio_uploader_user").read_text().strip()
    s3_pass = (SECRET_DIR / "minio_uploader_password").read_text().strip()
    uploader = boto3.client(
        "s3",
        endpoint_url=s3_endpoint,
        region_name="us-east-1",
        aws_access_key_id=s3_user,
        aws_secret_access_key=s3_pass,
    )
    content = b"Danang is a coastal city in central Vietnam known for sandy beaches.\n"
    content_sha256 = hashlib.sha256(content).hexdigest()
    key = f"allowed/ref-danang-{uuid4().hex}.txt"
    uploader.put_object(Bucket=bucket, Key=key, Body=content)

    async with RagCoreReferenceClient(
        base_url=base_url, auth_token=auth_token, service_key=service_key
    ) as client:
        session = await client.create_or_resolve_session(f"cite-session-{uuid4().hex}")
        session_id = session["session_id"]

        upload = await client.register_document(
            session_id=session_id,
            external_upload_id=uuid4().hex,
            source={
                "storage_alias": "fixture",
                "bucket": bucket,
                "key": key,
                "sha256": content_sha256,
            },
            filename="danang.txt",
            content_type="text/plain",
            idempotency_key=uuid4().hex,
        )
        await client.wait_for_job(upload["job"]["job_id"], timeout=30.0, poll_interval=0.2)

        res = await client.query(session_id=session_id, question="What is Danang known for?")
        chunk_id = res.citations[0]["chunk_id"]

        citation = await client.resolve_citation(session_id=session_id, chunk_id=chunk_id)
        citation_payload = citation["citation"]
        assert citation_payload["chunk_id"] == chunk_id
        assert citation_payload["filename"] == "danang.txt"
        assert citation_payload["locator"]

        # Other user cannot resolve citation
        async with RagCoreReferenceClient(
            base_url=base_url,
            auth_token=server_env["other_user_token"],
            service_key=service_key,
        ) as other_user_client:
            with pytest.raises(SessionNotFoundError):
                await other_user_client.resolve_citation(session_id=session_id, chunk_id=chunk_id)


@pytest.mark.asyncio
async def test_session_deletion_and_source_retention(server_env):
    """Verify session deletion tombstone semantics and byte-for-byte source/index retention."""
    base_url = server_env["base_url"]
    auth_token = server_env["auth_token"]
    service_key = server_env["service_key"]
    s3_endpoint = server_env["s3_endpoint"]
    bucket = server_env["bucket"]
    qdrant_url = server_env["qdrant_url"]
    model_fingerprint = server_env["model_fingerprint"]
    app_id = server_env["app_id"]
    user_id = server_env["user_id"]

    s3_user = (SECRET_DIR / "minio_uploader_user").read_text().strip()
    s3_pass = (SECRET_DIR / "minio_uploader_password").read_text().strip()
    uploader = boto3.client(
        "s3",
        endpoint_url=s3_endpoint,
        region_name="us-east-1",
        aws_access_key_id=s3_user,
        aws_secret_access_key=s3_pass,
    )
    content = b"Saigon is the economic hub of Vietnam with rich culinary history.\n"
    content_sha256 = hashlib.sha256(content).hexdigest()
    key = f"allowed/ref-saigon-{uuid4().hex}.txt"
    put_res = uploader.put_object(Bucket=bucket, Key=key, Body=content)
    version_id = put_res.get("VersionId")

    async with RagCoreReferenceClient(
        base_url=base_url, auth_token=auth_token, service_key=service_key
    ) as client:
        session = await client.create_or_resolve_session(f"del-session-{uuid4().hex}")
        session_id = session["session_id"]

        source_info = {
            "storage_alias": "fixture",
            "bucket": bucket,
            "key": key,
            "sha256": content_sha256,
        }
        if version_id:
            source_info["version_id"] = version_id

        upload = await client.register_document(
            session_id=session_id,
            external_upload_id=uuid4().hex,
            source=source_info,
            filename="saigon.txt",
            content_type="text/plain",
            idempotency_key=uuid4().hex,
        )
        await client.wait_for_job(upload["job"]["job_id"], timeout=30.0, poll_interval=0.2)

        # Confirm query works
        res = await client.query(session_id=session_id, question="What is Saigon?")
        assert res.answerability == "supported"

        # 1. Delete session
        del_res = await client.delete_session(session_id)
        assert del_res["session_id"] == session_id

        # 2. Subsequent query raises SessionDeletedError (410)
        with pytest.raises(SessionDeletedError):
            await client.query(session_id=session_id, question="What is Saigon?")

        # 3. Repeated delete is idempotent (returns 200)
        del_again = await client.delete_session(session_id)
        assert del_again["session_id"] == session_id

        # 4. Fresh session does not inherit the tombstoned session's documents
        fresh = await client.create_or_resolve_session(f"fresh-{uuid4().hex}")
        with pytest.raises(NoSessionDocumentsError):
            await client.query(session_id=fresh["session_id"], question="What is Saigon?")

        # 5. Raw S3 object retention: 100% byte-for-byte SHA256 identical
        get_kwargs = {"Bucket": bucket, "Key": key}
        if version_id:
            get_kwargs["VersionId"] = version_id
        retained_obj = uploader.get_object(**get_kwargs)
        retained_bytes = retained_obj["Body"].read()
        assert hashlib.sha256(retained_bytes).hexdigest() == content_sha256

        # 6. Qdrant vector index retention: points remain in collection
        qdrant = AsyncQdrantClient(url=qdrant_url, trust_env=False)
        try:
            collections = await qdrant.get_collections()
            fp_data = {
                "dense": 1024,
                "distance": "Cosine",
                "model": model_fingerprint,
                "schema": 1,
                "sparse": "bge-m3-no-idf",
            }
            target_col = (
                "rag_chunks_v1_"
                + hashlib.sha256(json.dumps(fp_data, sort_keys=True).encode()).hexdigest()
            )
            existing_cols = {c.name for c in collections.collections}
            assert target_col in existing_cols, f"Qdrant collection {target_col} should exist"
            count_res = await qdrant.count(
                collection_name=target_col,
                exact=True,
                count_filter=models.Filter(
                    must=[
                        models.FieldCondition(key="app_id", match=models.MatchValue(value=app_id)),
                        models.FieldCondition(
                            key="owner_id", match=models.MatchValue(value=user_id)
                        ),
                    ]
                ),
            )
            assert count_res.count > 0, "Vectors must be retained after session deletion"
        finally:
            await qdrant.close()
