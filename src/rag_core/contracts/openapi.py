"""Generate designed API inventory without registering executable business routes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, TypeAdapter

from rag_core.contracts import sse, v1

SCHEMA_MODELS: tuple[type[BaseModel], ...] = (
    v1.ContractLimits,
    v1.FileMeasurements,
    v1.QueryRequest,
    v1.QueryResponse,
    v1.SessionCreateRequest,
    v1.SessionResponse,
    v1.DocumentRegisterRequest,
    v1.DocumentRegisterResponse,
    v1.DocumentListResponse,
    v1.DetachResponse,
    v1.JobResponse,
    v1.CitationResolveResponse,
    v1.ErrorEnvelope,
    v1.LiveResponse,
    v1.ReadyResponse,
    sse.MetaEvent,
    sse.EvidenceEvent,
    sse.AnswerDeltaEvent,
    sse.DoneEvent,
    sse.ErrorEvent,
    sse.SSEHeartbeat,
    sse.SSESequence,
)


@dataclass(frozen=True)
class Endpoint:
    method: str
    path: str
    operation_id: str
    task: str
    response: str
    status: int = 200
    request: str | None = None
    served: bool = True
    idempotency: bool = False


ENDPOINTS = (
    Endpoint(
        "post",
        "/v1/sessions",
        "create_session",
        "T10",
        "SessionResponse",
        request="SessionCreateRequest",
    ),
    Endpoint("get", "/v1/sessions/{session_id}", "get_session", "T10", "SessionResponse"),
    Endpoint("delete", "/v1/sessions/{session_id}", "delete_session", "T10", "SessionResponse"),
    Endpoint(
        "post",
        "/v1/sessions/{session_id}/documents",
        "register_document",
        "T12",
        "DocumentRegisterResponse",
        202,
        "DocumentRegisterRequest",
        idempotency=True,
    ),
    Endpoint(
        "get",
        "/v1/sessions/{session_id}/documents",
        "list_documents",
        "T12",
        "DocumentListResponse",
    ),
    Endpoint(
        "delete",
        "/v1/sessions/{session_id}/documents/{document_id}",
        "detach_document",
        "T12",
        "DetachResponse",
    ),
    Endpoint("get", "/v1/jobs/{job_id}", "get_job", "T12/T19", "JobResponse"),
    Endpoint("post", "/v1/jobs/{job_id}/retry", "retry_job", "T12/T19", "JobResponse"),
    Endpoint("post", "/v1/query", "query", "T24/T26", "QueryResponse", request="QueryRequest"),
    Endpoint(
        "post", "/v1/query/stream", "query_stream", "T25/T26", "SSEEvent", request="QueryRequest"
    ),
    Endpoint(
        "get",
        "/v1/sessions/{session_id}/citations/{chunk_id}",
        "resolve_citation",
        "T24",
        "CitationResolveResponse",
    ),
    Endpoint("get", "/health/live", "health_live", "T02", "LiveResponse", served=True),
    Endpoint("get", "/health/ready", "health_ready", "T02", "ReadyResponse", served=True),
)

ERROR_STATUSES = {
    401: "Invalid or missing credentials",
    403: "Insufficient role",
    404: "Resource not in current authorized scope",
    409: "Scope/readiness/idempotency conflict",
    410: "Deleted session for its owner",
    422: "Invalid input",
    429: "Rate limit or bounded queue full",
    502: "Provider error",
    503: "Dependency unavailable",
    504: "Timeout",
}


def component_schemas() -> dict[str, Any]:
    components: dict[str, Any] = {}
    for model in SCHEMA_MODELS:
        schema = model.model_json_schema(ref_template="#/components/schemas/{model}")
        definitions = schema.pop("$defs", {})
        components.update(definitions)
        components[model.__name__] = schema
    event_schema = TypeAdapter(sse.SSEEvent).json_schema(
        ref_template="#/components/schemas/{model}"
    )
    components.update(event_schema.pop("$defs", {}))
    components["SSEEvent"] = event_schema
    return components


def _content(model: str, media_type: str = "application/json") -> dict[str, Any]:
    return {media_type: {"schema": {"$ref": f"#/components/schemas/{model}"}}}


def build_designed_openapi() -> dict[str, Any]:
    paths: dict[str, Any] = {}
    for endpoint in ENDPOINTS:
        stream = endpoint.operation_id == "query_stream"
        health = endpoint.path.startswith("/health/")
        operation: dict[str, Any] = {
            "operationId": endpoint.operation_id,
            "tags": ["health" if health else "public"],
            "summary": endpoint.operation_id.replace("_", " "),
            "x-implementation-status": "VERIFIED" if health else "IMPLEMENTED",
            "x-served": endpoint.served,
            "x-implementation-task": endpoint.task,
            "responses": {
                str(endpoint.status): {
                    "description": "Served response",
                    "content": _content(
                        endpoint.response, "text/event-stream" if stream else "application/json"
                    ),
                }
            },
        }
        if not health:
            operation["security"] = [{"UserJWT": [], "AppServiceKey": []}]
            operation["description"] = (
                "Mounted in T26; trusted runtime configuration is required. Authenticated app+subject and active session links/"
                "ready versions constrain access. Schemas do not grant ownership or readiness."
            )
            for status, description in ERROR_STATUSES.items():
                error: dict[str, Any] = {
                    "description": description,
                    "content": _content("ErrorEnvelope"),
                }
                if status == 429:
                    error["headers"] = {
                        "Retry-After": {
                            "description": "Backoff delay in seconds",
                            "schema": {"type": "integer", "minimum": 1},
                        }
                    }
                operation["responses"][str(status)] = error
        elif endpoint.operation_id == "health_ready":
            operation["responses"]["503"] = {
                "description": "Dependency unavailable; health-specific body, not business error",
                "content": _content("ReadyResponse"),
            }
        parameters: list[dict[str, Any]] = []
        for parameter in ("session_id", "document_id", "job_id", "chunk_id"):
            if "{" + parameter + "}" in endpoint.path:
                schema = {"type": "string"}
                if parameter != "chunk_id":
                    schema["format"] = "uuid"
                parameters.append(
                    {"name": parameter, "in": "path", "required": True, "schema": schema}
                )
        if endpoint.idempotency:
            parameters.append(
                {
                    "name": "Idempotency-Key",
                    "in": "header",
                    "required": True,
                    "schema": {"type": "string", "minLength": 1},
                    "description": "Scoped app+owner+session+request hash; mismatch 409",
                }
            )
        if endpoint.operation_id == "list_documents":
            parameters.extend(
                [
                    {"name": "cursor", "in": "query", "schema": {"type": "string"}},
                    {
                        "name": "limit",
                        "in": "query",
                        "schema": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 50,
                            "default": 50,
                        },
                    },
                ]
            )
        if parameters:
            operation["parameters"] = parameters
        if endpoint.request:
            operation["requestBody"] = {"required": True, "content": _content(endpoint.request)}
        if stream:
            operation["x-sse-contract"] = {
                "order": "meta -> evidence -> answer_delta* -> done|error",
                "early-error": "meta -> error before evidence is allowed",
                "heartbeat": "SSE comment; no event ID",
                "event-ids": "increasing per request",
                "wire": "SSE UTF-8 frames: id/event/data lines, blank-line delimiter; "
                "data line contains JSON. SSEEvent schema describes a parsed event, "
                "not a JSON HTTP response body.",
                "replay": False,
                "deltas": "provisional",
                "done": "validated final QueryResponse",
                "runtime": "IMPLEMENTED; scope checks before evidence/delta/done; cancel upstream",
            }
        paths.setdefault(endpoint.path, {})[endpoint.method] = operation
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "RAG Core API v1 — designed contract",
            "version": "1.0.0",
            "description": "API v1 contract inventory. Public routes mounted in T26; "
            "business services require trusted configuration and authentication.",
        },
        "paths": paths,
        "components": {
            "schemas": component_schemas(),
            "securitySchemes": {
                "UserJWT": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
                "AppServiceKey": {"type": "apiKey", "in": "header", "name": "X-RAG-Service-Key"},
            },
        },
        "x-deferred-inventory": [
            {"path": "/metrics", "status": "DESIGNED", "task": "T32", "protected": True},
            {"path": "/admin/*", "status": "DESIGNED", "task": "T27-T29"},
            {"path": "/v1/admin/*", "status": "DESIGNED", "task": "T27-T29"},
        ],
        "x-initial-limits": v1.INITIAL_LIMITS.model_dump(),
    }
