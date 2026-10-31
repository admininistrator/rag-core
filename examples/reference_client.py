"""Reference HTTPX client for RAG Core API v1.

Demonstrates application integration:
- Authentication via JWT Bearer token and X-RAG-Service-Key
- Session management: create/resolve, metadata, tombstone
- Document registration: S3/MinIO upload registration with Idempotency-Key
- Ingestion job status polling and retry
- Session-only grounded queries with conversation history
- Robust SSE streaming parser for /v1/query/stream (meta, evidence, answer_delta, done, error)
- Safe client-side cancellation and error envelope handling
- Citation source resolution within current session scope
- Document detachment and session deletion with retained source/index semantics

IMPORTANT: This client has zero dependency on RAG Core private internals.
It communicates exclusively over public HTTP API v1 endpoints.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

import httpx


class RagCoreClientError(Exception):
    """Base exception for RAG Core client errors."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int = 500,
        error_code: str = "client_error",
        retryable: bool = False,
        request_id: str | None = None,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.retryable = retryable
        self.request_id = request_id
        self.details = details or []

    def __repr__(self) -> str:
        return (
            f"RagCoreClientError(code={self.error_code!r}, status={self.status_code}, "
            f"retryable={self.retryable}, request_id={self.request_id!r})"
        )


class SessionNotFoundError(RagCoreClientError):
    """Session not found (HTTP 404)."""


class SessionDeletedError(RagCoreClientError):
    """Session has been deleted/tombstoned (HTTP 410)."""


class NoSessionDocumentsError(RagCoreClientError):
    """Session contains no ready documents (HTTP 409)."""


class DocumentsNotReadyError(RagCoreClientError):
    """One or more requested documents are still ingesting (HTTP 409)."""


class RateLimitError(RagCoreClientError):
    """Query admission or rate limit reached (HTTP 429)."""


class StreamInterruptedError(RagCoreClientError):
    """Server terminated the SSE stream prematurely or sent an error event."""


@dataclass(frozen=True)
class SSEEvent:
    """Parsed Server-Sent Event from /v1/query/stream."""

    event: str
    id: int
    data: dict[str, Any]


@dataclass
class QueryResult:
    """Unified result for both JSON query and SSE query stream."""

    request_id: str
    session_id: str
    scope_revision: int
    domain: str
    answer: str
    answerability: str
    reason_code: str | None = None
    citations: list[dict[str, Any]] = field(default_factory=list)
    contexts: list[dict[str, Any]] = field(default_factory=list)
    usage: dict[str, Any] = field(default_factory=dict)
    timings_ms: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


class RagCoreReferenceClient:
    """Async client interacting with RAG Core API v1 exclusively over HTTP."""

    def __init__(
        self,
        base_url: str,
        *,
        auth_token: str | None = None,
        service_key: str | None = None,
        timeout: float = 60.0,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._auth_token = auth_token
        self._service_key = service_key
        self._timeout = timeout
        self._external_client = http_client
        self._owned_client: httpx.AsyncClient | None = None

    def _headers(self, idempotency_key: str | None = None) -> dict[str, str]:
        headers: dict[str, str] = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if self._auth_token:
            headers["Authorization"] = f"Bearer {self._auth_token}"
        if self._service_key:
            headers["X-RAG-Service-Key"] = self._service_key
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return headers

    async def _get_client(self) -> httpx.AsyncClient:
        if self._external_client is not None:
            return self._external_client
        if self._owned_client is None or self._owned_client.is_closed:
            self._owned_client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self._timeout,
                trust_env=False,
            )
        return self._owned_client

    async def close(self) -> None:
        """Close client sessions if owned."""
        if self._owned_client is not None and not self._owned_client.is_closed:
            await self._owned_client.aclose()
            self._owned_client = None

    async def __aenter__(self) -> RagCoreReferenceClient:
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Parse structured ErrorEnvelope from RAG Core and raise typed exception."""
        status = response.status_code
        try:
            body = response.json()
            error_data = body.get("error", {})
            error_code = error_data.get("code", "unknown_error")
            message = error_data.get("message", response.text)
            retryable = bool(error_data.get("retryable", False))
            request_id = body.get("request_id")
            details = error_data.get("details", [])
        except Exception:
            error_code = "http_error"
            message = response.text or f"HTTP {status}"
            retryable = status in {429, 502, 503, 504}
            request_id = None
            details = []

        kwargs = {
            "status_code": status,
            "error_code": error_code,
            "retryable": retryable,
            "request_id": request_id,
            "details": details,
        }

        if status == 404:
            raise SessionNotFoundError(f"Resource not found: {message}", **kwargs)
        if status == 410 or error_code == "session_deleted":
            raise SessionDeletedError(f"Session deleted: {message}", **kwargs)
        if error_code == "no_session_documents":
            raise NoSessionDocumentsError(f"No session documents: {message}", **kwargs)
        if error_code == "documents_not_ready":
            raise DocumentsNotReadyError(f"Documents not ready: {message}", **kwargs)
        if status == 429 or error_code == "busy":
            raise RateLimitError(f"Query capacity busy: {message}", **kwargs)
        raise RagCoreClientError(f"RAG Core error ({error_code}): {message}", **kwargs)

    # -------------------------------------------------------------------------
    # Health checks
    # -------------------------------------------------------------------------

    async def health_live(self) -> dict[str, Any]:
        """Check process liveness probe."""
        client = await self._get_client()
        resp = await client.get("/health/live")
        if resp.status_code != 200:
            self._handle_error_response(resp)
        return resp.json()

    async def health_ready(self) -> dict[str, Any]:
        """Check system readiness probe (DB, Redis, Qdrant)."""
        client = await self._get_client()
        resp = await client.get("/health/ready")
        if resp.status_code != 200:
            self._handle_error_response(resp)
        return resp.json()

    # -------------------------------------------------------------------------
    # Session management
    # -------------------------------------------------------------------------

    async def create_or_resolve_session(self, external_session_id: str) -> dict[str, Any]:
        """Create or resolve core session for external_session_id."""
        client = await self._get_client()
        resp = await client.post(
            "/v1/sessions",
            headers=self._headers(),
            json={"external_session_id": external_session_id},
        )
        if resp.status_code not in {200, 201}:
            self._handle_error_response(resp)
        return resp.json()

    async def get_session(self, session_id: str | UUID) -> dict[str, Any]:
        """Fetch session metadata and scope_revision."""
        client = await self._get_client()
        resp = await client.get(f"/v1/sessions/{session_id}", headers=self._headers())
        if resp.status_code != 200:
            self._handle_error_response(resp)
        return resp.json()

    async def delete_session(self, session_id: str | UUID) -> dict[str, Any]:
        """Tombstone session; retains source blobs and index vectors."""
        client = await self._get_client()
        resp = await client.delete(f"/v1/sessions/{session_id}", headers=self._headers())
        if resp.status_code != 200:
            self._handle_error_response(resp)
        return resp.json()

    # -------------------------------------------------------------------------
    # Document registration & management
    # -------------------------------------------------------------------------

    async def register_document(
        self,
        session_id: str | UUID,
        *,
        external_upload_id: str,
        source: dict[str, Any],
        filename: str,
        content_type: str = "application/pdf",
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Register an uploaded object with the session with Idempotency-Key.

        Returns 202 Accepted with document and ingestion job descriptor.
        """
        client = await self._get_client()
        payload = {
            "external_upload_id": external_upload_id,
            "source": source,
            "filename": filename,
            "content_type": content_type,
        }
        resp = await client.post(
            f"/v1/sessions/{session_id}/documents",
            headers=self._headers(idempotency_key=idempotency_key),
            json=payload,
        )
        if resp.status_code != 202:
            self._handle_error_response(resp)
        return resp.json()

    async def list_documents(
        self,
        session_id: str | UUID,
        *,
        limit: int = 50,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """List documents attached to session with keyset pagination."""
        client = await self._get_client()
        params: dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        resp = await client.get(
            f"/v1/sessions/{session_id}/documents",
            headers=self._headers(),
            params=params,
        )
        if resp.status_code != 200:
            self._handle_error_response(resp)
        return resp.json()

    async def detach_document(
        self,
        session_id: str | UUID,
        document_id: str | UUID,
    ) -> dict[str, Any]:
        """Detach document link from session; retains underlying chunks and vectors."""
        client = await self._get_client()
        resp = await client.delete(
            f"/v1/sessions/{session_id}/documents/{document_id}",
            headers=self._headers(),
        )
        if resp.status_code != 200:
            self._handle_error_response(resp)
        return resp.json()

    # -------------------------------------------------------------------------
    # Ingestion Job tracking
    # -------------------------------------------------------------------------

    async def get_job(self, job_id: str | UUID) -> dict[str, Any]:
        """Get status and progress of an ingestion job."""
        client = await self._get_client()
        resp = await client.get(f"/v1/jobs/{job_id}", headers=self._headers())
        if resp.status_code != 200:
            self._handle_error_response(resp)
        return resp.json()

    async def wait_for_job(
        self,
        job_id: str | UUID,
        *,
        timeout: float = 60.0,
        poll_interval: float = 0.5,
    ) -> dict[str, Any]:
        """Poll job until it reaches 'ready' or terminal error state."""
        async with asyncio.timeout(timeout):
            while True:
                job = await self.get_job(job_id)
                state = job.get("state")
                if state == "ready":
                    return job
                if state in {"failed", "cancelled"}:
                    error = job.get("error") or {}
                    raise RagCoreClientError(
                        f"Ingestion job failed: {error.get('message', state)}",
                        error_code=error.get("code", "ingestion_failed"),
                        status_code=409,
                    )
                await asyncio.sleep(poll_interval)

    async def retry_job(self, job_id: str | UUID) -> dict[str, Any]:
        """Retry a failed ingestion job (idempotent when already queued)."""
        client = await self._get_client()
        resp = await client.post(f"/v1/jobs/{job_id}/retry", headers=self._headers())
        if resp.status_code != 200:
            self._handle_error_response(resp)
        return resp.json()

    # -------------------------------------------------------------------------
    # Citations
    # -------------------------------------------------------------------------

    async def resolve_citation(
        self,
        session_id: str | UUID,
        chunk_id: str,
    ) -> dict[str, Any]:
        """Resolve citation source metadata within the session scope."""
        client = await self._get_client()
        resp = await client.get(
            f"/v1/sessions/{session_id}/citations/{chunk_id}",
            headers=self._headers(),
        )
        if resp.status_code != 200:
            self._handle_error_response(resp)
        return resp.json()

    # -------------------------------------------------------------------------
    # Queries (JSON and SSE Stream)
    # -------------------------------------------------------------------------

    async def query(
        self,
        session_id: str | UUID,
        question: str,
        *,
        domain: str = "default",
        document_ids: list[str] | None = None,
        history: list[dict[str, str]] | None = None,
        corpus_languages: list[str] | None = None,
        answer_language: str | None = None,
    ) -> QueryResult:
        """Execute non-streaming grounded query returning QueryResult."""
        client = await self._get_client()
        payload: dict[str, Any] = {
            "session_id": str(session_id),
            "question": question,
            "domain": domain,
        }
        if document_ids is not None:
            payload["document_ids"] = document_ids
        if history is not None:
            payload["history"] = history
        if corpus_languages is not None:
            payload["corpus_languages"] = corpus_languages
        if answer_language is not None:
            payload["answer_language"] = answer_language

        resp = await client.post("/v1/query", headers=self._headers(), json=payload)
        if resp.status_code != 200:
            self._handle_error_response(resp)

        data = resp.json()
        return QueryResult(
            request_id=data["request_id"],
            session_id=data["session_id"],
            scope_revision=data["scope_revision"],
            domain=data["domain"],
            answer=data["answer"],
            answerability=data["answerability"],
            reason_code=data.get("reason_code"),
            citations=data.get("citations", []),
            contexts=data.get("contexts", []),
            usage=data.get("usage", {}),
            timings_ms=data.get("timings_ms", {}),
            warnings=data.get("warnings", []),
        )

    async def stream_query(
        self,
        session_id: str | UUID,
        question: str,
        *,
        domain: str = "default",
        document_ids: list[str] | None = None,
        history: list[dict[str, str]] | None = None,
        corpus_languages: list[str] | None = None,
        answer_language: str | None = None,
    ) -> AsyncIterator[SSEEvent]:
        """Stream query responses via SSE (POST /v1/query/stream).

        Yields SSEEvent instances (meta, evidence, answer_delta, done).
        Raises StreamInterruptedError if the server terminates early or yields an error event.
        """
        client = await self._get_client()
        payload: dict[str, Any] = {
            "session_id": str(session_id),
            "question": question,
            "domain": domain,
        }
        if document_ids is not None:
            payload["document_ids"] = document_ids
        if history is not None:
            payload["history"] = history
        if corpus_languages is not None:
            payload["corpus_languages"] = corpus_languages
        if answer_language is not None:
            payload["answer_language"] = answer_language

        headers = self._headers()
        headers["Accept"] = "text/event-stream"

        async with client.stream(
            "POST",
            "/v1/query/stream",
            headers=headers,
            json=payload,
            timeout=self._timeout,
        ) as response:
            if response.status_code != 200:
                await response.aread()
                self._handle_error_response(response)

            event_name: str | None = None
            event_id: int | None = None
            data_lines: list[str] = []
            wire_bytes = 0
            max_stream_bytes = 8 * 1024 * 1024  # 8 MB guard limit

            async for line in response.aiter_lines():
                wire_bytes += len(line.encode("utf-8")) + 1
                if wire_bytes > max_stream_bytes:
                    raise StreamInterruptedError("SSE stream exceeded maximum allowed size limit")

                # Heartbeat comment: lines starting with ":"
                if line.startswith(":"):
                    continue

                if line:
                    field_name, sep, value = line.partition(":")
                    if sep:
                        value = value.removeprefix(" ")
                        if field_name == "event":
                            event_name = value
                        elif field_name == "id":
                            try:
                                event_id = int(value)
                            except ValueError:
                                event_id = None
                        elif field_name == "data":
                            data_lines.append(value)
                    continue

                # Empty line marks end of event block
                if event_name is not None and event_id is not None:
                    raw_data = "\n".join(data_lines)
                    try:
                        parsed_data = json.loads(raw_data) if raw_data else {}
                    except json.JSONDecodeError:
                        parsed_data = {"raw": raw_data}

                    event = SSEEvent(event=event_name, id=event_id, data=parsed_data)

                    if event.event == "error":
                        err = event.data.get("error", {})
                        raise StreamInterruptedError(
                            f"SSE error event received: {err.get('message', 'stream_error')}",
                            error_code=err.get("code", "stream_error"),
                            retryable=err.get("retryable", False),
                            request_id=event.data.get("request_id"),
                        )

                    yield event

                    if event.event == "done":
                        return

                    event_name, event_id = None, None
                    data_lines = []
