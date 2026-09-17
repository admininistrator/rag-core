"""Synthetic design examples, never returned by an executable API route."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from pydantic import BaseModel

from rag_core.contracts import sse, v1
from rag_core.contracts.openapi import SCHEMA_MODELS

_EXTRA_MODELS: tuple[type[BaseModel], ...] = (v1.Citation, v1.HistoryMetadata)
EXAMPLE_MODELS = {model.__name__: model for model in (*SCHEMA_MODELS, *_EXTRA_MODELS)}


def build_examples() -> dict[str, Any]:
    request_id = "00000000-0000-4000-8000-000000000001"
    session_id = "00000000-0000-4000-8000-000000000002"
    document_id = "00000000-0000-4000-8000-000000000003"
    version_id = "00000000-0000-4000-8000-000000000004"
    job_id = "00000000-0000-4000-8000-000000000005"
    citation = {
        "id": "c1",
        "document_id": document_id,
        "version_id": version_id,
        "chunk_id": "synthetic-chunk-1",
        "filename": "synthetic-report.pdf",
        "locator": {"kind": "pdf", "page": 12},
        "quote": "Revenue rose by ten percent.",
    }
    context = {
        "chunk_id": "synthetic-chunk-1",
        "document_id": document_id,
        "text": "Revenue rose by ten percent.",
        "citation_ids": ["c1"],
    }
    evidence = {"answerability": "supported", "citations": [citation], "contexts": [context]}
    response = {
        **evidence,
        "request_id": request_id,
        "session_id": session_id,
        "scope_revision": 3,
        "domain": "multilingual",
        "answer": "Doanh thu tăng mười phần trăm. [c1]",
        "reason_code": None,
        "usage": {"provider": None, "model": None, "input_tokens": None, "output_tokens": None},
        "timings_ms": {"retrieval": None, "generation": None, "total": None},
        "warnings": [],
    }
    error = {
        "request_id": request_id,
        "error": {
            "code": "documents_not_ready",
            "message": "Selected documents are not ready.",
            "retryable": True,
            "details": [{"field": "document_ids", "reason": "not_ready"}],
        },
    }
    history = {
        "received_messages": 1,
        "retained_messages": 1,
        "received_tokens": None,
        "retained_tokens": None,
        "truncated": False,
    }
    meta = {
        "event": "meta",
        "id": 1,
        "data": {
            "request_id": request_id,
            "session_id": session_id,
            "scope_revision": 3,
            "domain": "multilingual",
            "history": history,
        },
    }
    events: list[dict[str, Any]] = [
        meta,
        {"event": "evidence", "id": 2, "data": evidence},
        {"event": "answer_delta", "id": 3, "data": {"text": "Doanh thu tăng "}},
        {"event": "answer_delta", "id": 4, "data": {"text": "mười phần trăm. [c1]"}},
        {"event": "done", "id": 5, "data": response},
    ]
    document = {
        "document_id": document_id,
        "version_id": version_id,
        "filename": "synthetic-report.pdf",
        "link_status": "attached",
        "state": "queued",
    }
    job = {
        "request_id": request_id,
        "job_id": job_id,
        "document_id": document_id,
        "version_id": version_id,
        "state": "queued",
        "progress": None,
        "error": None,
        "retryable": False,
    }
    records: list[dict[str, Any]] = []

    def add(name: str, schema: str, value: Any) -> None:
        records.append({"name": name, "schema": schema, "value": deepcopy(value)})

    add("default_query", "QueryRequest", {"session_id": session_id, "question": "What changed?"})
    add(
        "document_query",
        "QueryRequest",
        {
            "session_id": session_id,
            "domain": "document",
            "question": "What changed?",
            "document_ids": [document_id],
        },
    )
    add(
        "multilingual_query",
        "QueryRequest",
        {
            "session_id": session_id,
            "domain": "multilingual",
            "question": "Doanh thu tăng thế nào?",
            "document_ids": [document_id],
            "history": [{"role": "user", "content": "Báo cáo 2023."}],
            "corpus_languages": ["en"],
            "answer_language": "vi",
        },
    )
    add("create_session", "SessionCreateRequest", {"external_session_id": "synthetic-chat-1"})
    add(
        "session",
        "SessionResponse",
        {
            "request_id": request_id,
            "session_id": session_id,
            "external_session_id": "synthetic-chat-1",
            "status": "active",
            "scope_revision": 0,
        },
    )
    add(
        "registration",
        "DocumentRegisterRequest",
        {
            "external_upload_id": "synthetic-upload-1",
            "source": {
                "storage_alias": "configured-app-storage",
                "bucket": "allowed-bucket",
                "key": "allowed-owner-prefix/synthetic-report.pdf",
                "version_id": "opaque-storage-version",
                "sha256": "a" * 64,
            },
            "filename": "synthetic-report.pdf",
            "content_type": "application/pdf",
        },
    )
    add(
        "registration_accepted_design",
        "DocumentRegisterResponse",
        {
            "request_id": request_id,
            "session_id": session_id,
            "scope_revision": 1,
            "document": document,
            "job": job,
        },
    )
    add(
        "document_list",
        "DocumentListResponse",
        {
            "request_id": request_id,
            "session_id": session_id,
            "scope_revision": 1,
            "documents": [document],
            "next_cursor": None,
        },
    )
    add(
        "detached",
        "DetachResponse",
        {
            "request_id": request_id,
            "session_id": session_id,
            "document_id": document_id,
            "link_status": "detached",
            "scope_revision": 2,
        },
    )
    add("job", "JobResponse", job)
    add("supported_design", "QueryResponse", response)
    insufficient = {
        **response,
        "answerability": "insufficient_evidence",
        "reason_code": "no_relevant_evidence",
        "answer": "Chưa có bằng chứng phù hợp.",
        "citations": [],
        "contexts": [],
    }
    add("insufficient_design", "QueryResponse", insufficient)
    truncation = {
        "received_messages": 21,
        "retained_messages": 20,
        "received_tokens": 8100,
        "retained_tokens": 8000,
        "truncated": True,
    }
    add(
        "notified_history_truncation",
        "QueryResponse",
        {
            **response,
            "warnings": [
                {
                    "code": "history_truncated",
                    "message": "History was truncated to its processing budget.",
                    "history": truncation,
                }
            ],
        },
    )
    add("error", "ErrorEnvelope", error)
    add(
        "citation_resolver",
        "CitationResolveResponse",
        {
            "request_id": request_id,
            "session_id": session_id,
            "scope_revision": 3,
            "citation": citation,
        },
    )
    locators: list[dict[str, Any]] = [
        {"kind": "docx", "heading_path": ["Revenue"], "paragraph": 0},
        {"kind": "docx", "heading_path": [], "table": 0},
        {
            "kind": "xlsx",
            "sheet": "Revenue",
            "cell_range": "B2:D4",
            "headers": ["USD"],
            "unit": "USD",
        },
        {"kind": "pptx", "slide": 1, "shape": 0},
        {"kind": "txt", "line_start": 1, "line_end": 2, "offsets": {"start": 0, "end": 10}},
        {"kind": "md", "paragraph": 0},
        {"kind": "csv", "row_start": 1, "row_end": 2, "columns": ["Revenue", "Year"]},
        {"kind": "html", "heading_path": ["Revenue"], "block": 0},
        {
            "kind": "image",
            "image_id": "synthetic-image-1",
            "ocr_block": 0,
            "bbox": {"x0": 0, "y0": 0, "x1": 100, "y1": 50},
        },
    ]
    for index, locator in enumerate(locators):
        add(f"locator_{locator['kind']}_{index}", "Citation", {**citation, "locator": locator})
    add("live", "LiveResponse", {"status": "ok"})
    add(
        "ready",
        "ReadyResponse",
        {"status": "ready", "components": {"postgres": "ok", "redis": "ok", "qdrant": "ok"}},
    )
    add("limits", "ContractLimits", v1.INITIAL_LIMITS.model_dump())
    add("file_boundary", "FileMeasurements", {"size_bytes": 104857600, "pages": 1000})
    add("sse_done_trace_design", "SSESequence", events)
    add(
        "sse_early_error_trace_design",
        "SSESequence",
        [meta, {"event": "error", "id": 2, "data": error}],
    )
    add("sse_heartbeat_comment", "SSEHeartbeat", {"comment": "keep-alive"})
    for event in events:
        model = {
            "meta": sse.MetaEvent,
            "evidence": sse.EvidenceEvent,
            "answer_delta": sse.AnswerDeltaEvent,
            "done": sse.DoneEvent,
        }[event["event"]]
        add(f"sse_{event['event']}_{event['id']}", model.__name__, event)
    add("sse_error", "ErrorEvent", {"event": "error", "id": 2, "data": error})
    return {"status": "SYNTHETIC_DESIGN_EXAMPLES_NOT_RUNTIME_OUTPUT", "examples": records}
