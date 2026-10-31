"""FastAPI reference backend application demonstrating RAG Core integration.

Exemplifies how an external chat backend (such as Scarlet) maps its own
entities, authentication, file storage, and streaming to RAG Core v1 API.

Key Patterns Illustrated:
1. Session mapping: external client session ID mapped to authenticated user's RAG Core session.
2. Direct upload & registration: app uploads to S3/MinIO, then registers source with RAG Core.
3. Ingestion tracking: polling job status until ready.
4. Conversation history & grounding: forwarding messages to RAG Core with session boundary check.
5. SSE streaming: consuming RAG Core SSE and forwarding events to the frontend client.
6. Citation resolution: looking up verified citation metadata.
7. Deletion: deleting chat session while preserving raw document files and vector embeddings.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from examples.reference_client import (
    DocumentsNotReadyError,
    NoSessionDocumentsError,
    RagCoreClientError,
    RagCoreReferenceClient,
    RateLimitError,
    SessionDeletedError,
    SessionNotFoundError,
)

app = FastAPI(
    title="Scarlet / App Reference Gateway",
    description="Sample application backend integrating RAG Core via HTTP API v1",
    version="1.0.0",
)

# Configuration from environment
RAG_CORE_BASE_URL = os.getenv("RAG_CORE_BASE_URL", "http://127.0.0.1:8000")
RAG_SERVICE_KEY = os.getenv("RAG_SERVICE_KEY", "example-service-key")


def get_rag_client(auth_header: str | None = None) -> RagCoreReferenceClient:
    """Helper to instantiate RagCoreReferenceClient with user token."""
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.removeprefix("Bearer ").strip()
    return RagCoreReferenceClient(
        base_url=RAG_CORE_BASE_URL,
        auth_token=token,
        service_key=RAG_SERVICE_KEY,
    )


# -----------------------------------------------------------------------------
# Request & Response Models
# -----------------------------------------------------------------------------


class CreateChatSessionRequest(BaseModel):
    client_session_id: str = Field(
        ..., description="External session identifier from frontend/user"
    )


class RegisterDocumentRequest(BaseModel):
    storage_alias: str = "app-storage"
    bucket: str
    key: str
    filename: str
    content_type: str = "application/pdf"
    version_id: str | None = None
    sha256: str | None = None


class ChatQueryRequest(BaseModel):
    question: str
    domain: str = "default"
    document_ids: list[str] | None = None
    history: list[dict[str, str]] | None = None
    corpus_languages: list[str] | None = None
    answer_language: str | None = None


# -----------------------------------------------------------------------------
# API Routes
# -----------------------------------------------------------------------------


@app.post("/api/chat/sessions", status_code=status.HTTP_201_CREATED)
async def create_session(
    body: CreateChatSessionRequest,
    authorization: str | None = Header(None),
) -> dict[str, Any]:
    """Create or resolve RAG Core session for an app chat session."""
    client = get_rag_client(authorization)
    try:
        core_session = await client.create_or_resolve_session(body.client_session_id)
        return {
            "client_session_id": body.client_session_id,
            "core_session_id": core_session["session_id"],
            "scope_revision": core_session.get("scope_revision", 0),
        }
    except RagCoreClientError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    finally:
        await client.close()


@app.post("/api/chat/sessions/{session_id}/documents", status_code=status.HTTP_202_ACCEPTED)
async def register_document(
    session_id: str,
    body: RegisterDocumentRequest,
    idempotency_key: str | None = Header(None),
    authorization: str | None = Header(None),
) -> dict[str, Any]:
    """Register an uploaded document with the session."""
    client = get_rag_client(authorization)
    try:
        source = {
            "storage_alias": body.storage_alias,
            "bucket": body.bucket,
            "key": body.key,
        }
        if body.version_id:
            source["version_id"] = body.version_id
        if body.sha256:
            source["sha256"] = body.sha256

        key = idempotency_key or f"upload-{uuid4().hex}"
        result = await client.register_document(
            session_id=session_id,
            external_upload_id=uuid4().hex,
            source=source,
            filename=body.filename,
            content_type=body.content_type,
            idempotency_key=key,
        )
        return result
    except RagCoreClientError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    finally:
        await client.close()


@app.get("/api/chat/jobs/{job_id}")
async def get_job_status(
    job_id: str,
    authorization: str | None = Header(None),
) -> dict[str, Any]:
    """Poll ingestion job status."""
    client = get_rag_client(authorization)
    try:
        return await client.get_job(job_id)
    except RagCoreClientError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    finally:
        await client.close()


@app.post("/api/chat/sessions/{session_id}/query")
async def chat_query(
    session_id: str,
    body: ChatQueryRequest,
    authorization: str | None = Header(None),
) -> dict[str, Any]:
    """Execute a grounded query over documents in the session."""
    client = get_rag_client(authorization)
    try:
        result = await client.query(
            session_id=session_id,
            question=body.question,
            domain=body.domain,
            document_ids=body.document_ids,
            history=body.history,
            corpus_languages=body.corpus_languages,
            answer_language=body.answer_language,
        )
        return {
            "request_id": result.request_id,
            "session_id": result.session_id,
            "answer": result.answer,
            "answerability": result.answerability,
            "reason_code": result.reason_code,
            "citations": result.citations,
            "contexts": result.contexts,
            "usage": result.usage,
            "timings_ms": result.timings_ms,
        }
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Session not found") from exc
    except SessionDeletedError as exc:
        raise HTTPException(status_code=410, detail="Session has been deleted") from exc
    except NoSessionDocumentsError as exc:
        raise HTTPException(status_code=409, detail="No ready documents in this session") from exc
    except DocumentsNotReadyError as exc:
        raise HTTPException(status_code=409, detail="Documents are still ingesting") from exc
    except RateLimitError as exc:
        raise HTTPException(
            status_code=429, detail="Server is currently busy, please retry"
        ) from exc
    except RagCoreClientError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    finally:
        await client.close()


@app.post("/api/chat/sessions/{session_id}/query/stream")
async def chat_query_stream(
    session_id: str,
    body: ChatQueryRequest,
    authorization: str | None = Header(None),
) -> StreamingResponse:
    """Stream grounded query events as Server-Sent Events (SSE)."""
    client = get_rag_client(authorization)

    async def event_generator() -> AsyncIterator[str]:
        try:
            async for event in client.stream_query(
                session_id=session_id,
                question=body.question,
                domain=body.domain,
                document_ids=body.document_ids,
                history=body.history,
                corpus_languages=body.corpus_languages,
                answer_language=body.answer_language,
            ):
                import json

                yield f"id: {event.id}\nevent: {event.event}\ndata: {json.dumps(event.data)}\n\n"
        finally:
            await client.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-store",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/chat/sessions/{session_id}/citations/{chunk_id}")
async def resolve_citation(
    session_id: str,
    chunk_id: str,
    authorization: str | None = Header(None),
) -> dict[str, Any]:
    """Resolve citation details (filename, page/paragraph locator, quote) within session."""
    client = get_rag_client(authorization)
    try:
        return await client.resolve_citation(session_id=session_id, chunk_id=chunk_id)
    except RagCoreClientError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    finally:
        await client.close()


@app.delete("/api/chat/sessions/{session_id}")
async def delete_session(
    session_id: str,
    authorization: str | None = Header(None),
) -> dict[str, Any]:
    """Delete chat session in app and tombstone core session; retains raw storage and index."""
    client = get_rag_client(authorization)
    try:
        return await client.delete_session(session_id)
    except RagCoreClientError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    finally:
        await client.close()
