"""All public v1 routes; identities only from authenticated request state."""

import asyncio
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header, Query, Request
from starlette.responses import JSONResponse, Response

from rag_core.api.auth import require_principal
from rag_core.api.errors import SafeApiRoute
from rag_core.api.runtime import PublicServices
from rag_core.api.streaming import QueryStreamResponse
from rag_core.application.admission import QueryLease
from rag_core.auth import Principal
from rag_core.contracts.v1 import (
    CitationResolveResponse,
    DetachResponse,
    DocumentListResponse,
    DocumentRegisterRequest,
    DocumentRegisterResponse,
    DocumentResponse,
    ErrorBody,
    JobResponse,
    QueryRequest,
    QueryResponse,
    SessionCreateRequest,
    SessionResponse,
)
from rag_core.domain.metadata import Session
from rag_core.domain.registration import Job

PrincipalDep = Annotated[Principal, Depends(require_principal)]


def require_services(request: Request) -> PublicServices:
    services = getattr(request.app.state, "public_services", None)
    if services is None:
        raise RuntimeError("public_api_unconfigured")
    return services  # type: ignore[no-any-return]


ServicesDep = Annotated[PublicServices, Depends(require_services)]


def session_response(session: Session) -> SessionResponse:
    return SessionResponse(
        request_id=uuid4(),
        session_id=session.session_id,
        external_session_id=session.external_session_id,
        status=session.status,
        scope_revision=session.scope_revision,
    )


def job_response(job: Job) -> JobResponse:
    from pydantic import TypeAdapter

    from rag_core.contracts.v1 import ErrorCode

    error = None
    if job.error_code is not None:
        try:
            code: ErrorCode = TypeAdapter(ErrorCode).validate_python(job.error_code)
        except ValueError:
            code = "extraction_failed"
        error = ErrorBody(code=code, message="Document ingestion failed.", retryable=job.retryable)
    return JobResponse(
        request_id=uuid4(),
        job_id=job.job_id,
        document_id=job.document_id,
        version_id=job.version_id,
        state=job.state,
        progress=job.progress / 100,
        error=error,
        retryable=job.retryable,
    )


async def disconnected(request: Request) -> None:
    while not await request.is_disconnected():
        await asyncio.sleep(0.05)


def build_public_router() -> APIRouter:
    router = APIRouter(route_class=SafeApiRoute)

    @router.post("/v1/sessions", response_model=SessionResponse, operation_id="create_session")
    async def create_session(
        body: SessionCreateRequest, principal: PrincipalDep, services: ServicesDep
    ) -> SessionResponse:
        return session_response(
            await services.sessions.create_session(principal, body.external_session_id)
        )

    @router.get(
        "/v1/sessions/{session_id}", response_model=SessionResponse, operation_id="get_session"
    )
    async def get_session(
        session_id: UUID, principal: PrincipalDep, services: ServicesDep
    ) -> SessionResponse:
        return session_response(await services.sessions.get_session(principal, session_id))

    @router.delete(
        "/v1/sessions/{session_id}", response_model=SessionResponse, operation_id="delete_session"
    )
    async def delete_session(
        session_id: UUID, principal: PrincipalDep, services: ServicesDep
    ) -> SessionResponse:
        return session_response(await services.sessions.delete_session(principal, session_id))

    @router.post(
        "/v1/sessions/{session_id}/documents",
        status_code=202,
        response_model=DocumentRegisterResponse,
        operation_id="register_document",
    )
    async def register_document(
        session_id: UUID,
        body: DocumentRegisterRequest,
        principal: PrincipalDep,
        services: ServicesDep,
        key: Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=256)],
    ) -> DocumentRegisterResponse:
        result = await services.registrations.register(principal, session_id, key, body)
        return DocumentRegisterResponse(
            request_id=uuid4(),
            session_id=session_id,
            scope_revision=result.session.scope_revision,
            document=DocumentResponse(
                document_id=result.document_id,
                version_id=result.version_id,
                filename=result.filename,
                link_status=result.link_status,
                state=result.job.state,
            ),
            job=job_response(result.job),
        )

    @router.get(
        "/v1/sessions/{session_id}/documents",
        response_model=DocumentListResponse,
        operation_id="list_documents",
    )
    async def list_documents(
        session_id: UUID,
        principal: PrincipalDep,
        services: ServicesDep,
        cursor: UUID | None = None,
        limit: Annotated[int, Query(ge=1, le=50)] = 50,
    ) -> DocumentListResponse:
        session, documents, next_cursor = await services.registrations.list_documents(
            principal, session_id, cursor=cursor, limit=limit
        )
        return DocumentListResponse(
            request_id=uuid4(),
            session_id=session_id,
            scope_revision=session.scope_revision,
            next_cursor=str(next_cursor) if next_cursor else None,
            documents=[
                DocumentResponse(
                    document_id=d.document_id,
                    version_id=d.version_id,
                    filename=d.filename,
                    link_status=d.link_status,
                    state=d.job.state,
                )
                for d in documents
            ],
        )

    @router.delete(
        "/v1/sessions/{session_id}/documents/{document_id}",
        response_model=DetachResponse,
        operation_id="detach_document",
    )
    async def detach_document(
        session_id: UUID, document_id: UUID, principal: PrincipalDep, services: ServicesDep
    ) -> DetachResponse:
        result = await services.registrations.detach_document(principal, session_id, document_id)
        return DetachResponse(
            request_id=uuid4(),
            session_id=session_id,
            document_id=document_id,
            link_status="detached",
            scope_revision=result.scope_revision,
        )

    @router.get("/v1/jobs/{job_id}", response_model=JobResponse, operation_id="get_job")
    async def get_job(job_id: UUID, principal: PrincipalDep, services: ServicesDep) -> JobResponse:
        return job_response(await services.registrations.get_job(principal, job_id))

    @router.post("/v1/jobs/{job_id}/retry", response_model=JobResponse, operation_id="retry_job")
    async def retry_job(
        job_id: UUID, principal: PrincipalDep, services: ServicesDep
    ) -> JobResponse:
        return job_response(await services.registrations.retry_job(principal, job_id))

    @router.get(
        "/v1/sessions/{session_id}/citations/{chunk_id}",
        response_model=CitationResolveResponse,
        operation_id="resolve_citation",
    )
    async def resolve_citation(
        session_id: UUID, chunk_id: UUID, principal: PrincipalDep, services: ServicesDep
    ) -> CitationResolveResponse:
        return await services.citations.resolve(principal, session_id, chunk_id, uuid4())

    @router.post("/v1/query", response_model=QueryResponse, operation_id="query")
    async def query(
        body: QueryRequest, request: Request, principal: PrincipalDep, services: ServicesDep
    ) -> Response:
        lease: QueryLease | None = None
        work = None
        monitor = asyncio.create_task(disconnected(request))

        async def answer() -> JSONResponse:
            nonlocal lease
            async with asyncio.timeout(services.policy.total_timeout):
                lease = await services.admission.acquire()
                subset = tuple(body.document_ids) if body.document_ids is not None else None
                snapshot = await services.sessions.resolve_scope(principal, body.session_id, subset)
                result = await services.answers.answer(principal, body, uuid4())
                # Final serialization gate preserves the exact pairs, not only a revision number.
                await services.sessions.validate_snapshot(snapshot)
                return JSONResponse(
                    result.model_dump(mode="json"), headers={"Cache-Control": "no-store"}
                )

        try:
            work = asyncio.create_task(answer())
            done, _ = await asyncio.wait((work, monitor), return_when=asyncio.FIRST_COMPLETED)
            if monitor in done:
                raise asyncio.CancelledError
            return await work
        finally:
            monitor.cancel()
            if work is not None:
                work.cancel()

            async def close() -> None:
                try:
                    await asyncio.gather(
                        monitor, *([work] if work is not None else []), return_exceptions=True
                    )
                finally:
                    if lease is not None:
                        lease.release()

            # A second cancellation cannot interrupt provider cleanup or release its slot early.
            await asyncio.shield(asyncio.create_task(close()))

    @router.post(
        "/v1/query/stream",
        response_class=Response,
        operation_id="query_stream",
        responses={200: {"content": {"text/event-stream": {}}}},
    )
    async def query_stream(
        body: QueryRequest, principal: PrincipalDep, services: ServicesDep
    ) -> Response:
        return QueryStreamResponse(
            services.streaming.query(principal, body, uuid4()), services.admission, services.policy
        )

    return router
