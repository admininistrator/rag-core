# RAG Core — Integration Examples and Reference Client

This directory provides a production-grade, zero-dependency reference client and sample FastAPI application demonstrating how external chat applications (such as Scarlet) integrate with RAG Core.

## Principles & Trust Boundary

1. **Zero Private Dependencies**: The client does not import any internal RAG Core modules (`rag_core.services.*`, `rag_core.adapters.*`, etc.). It communicates exclusively over public HTTP API v1 contracts using `httpx`.
2. **Session Isolation**: Every document upload and query is strictly scoped to the authenticated user's active session. Cross-session access fails closed with HTTP 404.
3. **Data Ownership & Immutability**:
   - The application owns raw document storage (S3/MinIO) and chat transcripts.
   - RAG Core only reads (`GetObject`) registered objects; it never writes or deletes objects in application storage.
   - Session deletion (`DELETE /v1/sessions/{session_id}`) tombstones the session and invalidates links, but permanently retains underlying document blobs in S3 and vector embeddings in Qdrant for audit and deduplication.
4. **Streaming Protocol**: `POST /v1/query/stream` returns Server-Sent Events (`meta` -> `evidence` -> `answer_delta` ... -> `done` or `error`). Stream cancellation safely terminates upstream execution and releases admission capacity immediately.

## Files

- [`reference_client.py`](reference_client.py): Async HTTPX client (`RagCoreReferenceClient`) with comprehensive method coverage, typed errors, Idempotency-Key support, and robust SSE stream parsing.
- [`fastapi_app.py`](fastapi_app.py): Sample FastAPI backend proxy illustrating how an application maps its user sessions, upload events, and chat streams to RAG Core.

## Quickstart

### 1. Basic Client Usage

```python
import asyncio
from examples.reference_client import RagCoreReferenceClient


async def main():
    async with RagCoreReferenceClient(
        base_url="http://127.0.0.1:8000",
        auth_token="<user-jwt-token>",
        service_key="<app-service-key>",
    ) as client:
        # Check health
        ready = await client.health_ready()
        print("RAG Core ready:", ready["status"])

        # 1. Create or resolve session
        session = await client.create_or_resolve_session(external_session_id="chat-session-123")
        session_id = session["session_id"]

        # 2. Register document previously uploaded to S3
        upload = await client.register_document(
            session_id=session_id,
            external_upload_id="upload-event-001",
            source={
                "storage_alias": "app-storage",
                "bucket": "app-documents",
                "key": "user-1/contract.pdf",
                "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            },
            filename="contract.pdf",
            idempotency_key="idemp-key-001",
        )

        # 3. Poll ingestion job until ready
        job = await client.wait_for_job(upload["job"]["job_id"], timeout=60.0)
        print("Document indexed into generation:", job["state"])

        # 4. Non-streaming query
        result = await client.query(
            session_id=session_id,
            question="What is the term of this contract?",
        )
        print("Answer:", result.answer)
        print("Citations:", [c["locator"] for c in result.citations])

        # 5. Streaming query via SSE
        async for event in client.stream_query(
            session_id=session_id,
            question="What are the termination clauses?",
        ):
            if event.event == "answer_delta":
                print(event.data.get("delta", ""), end="", flush=True)
            elif event.event == "done":
                print("\n[Done] Citations count:", len(event.data.get("citations", [])))

        # 6. Delete session (tombstone)
        await client.delete_session(session_id)
        print("Session deleted; raw documents and vectors retained.")


if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Running Verification Tests

```bash
uv run pytest tests/e2e/test_reference_client.py -v -s
```

