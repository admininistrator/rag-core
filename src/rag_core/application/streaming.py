"""Session-bound SSE application events; HTTP lifetime/admission is an adapter concern."""

import time
from collections.abc import AsyncGenerator
from contextlib import aclosing
from uuid import UUID

from rag_core.application.answers import AnswerAssembler
from rag_core.application.evidence import EvidenceSelector
from rag_core.application.query import QueryPreparation, ScopedRetrievalContext
from rag_core.application.retrieval import RetrievalPipeline
from rag_core.auth import Principal
from rag_core.contracts.sse import (
    AnswerDeltaEvent,
    DeltaData,
    DoneEvent,
    EvidenceEvent,
    MetaData,
    MetaEvent,
    SSEEvent,
)
from rag_core.contracts.v1 import Evidence, QueryRequest, QueryResponse
from rag_core.domain.streaming import StreamPolicy


class ScopedAnswerStream:
    def __init__(
        self,
        pipeline: "StreamingAnswerPipeline",
        principal: Principal,
        query: QueryRequest,
        request_id: UUID,
    ) -> None:
        self.pipeline = pipeline
        self.principal = principal
        self.query = QueryRequest.model_validate(query.model_dump())
        self.request_id = request_id
        self.context: ScopedRetrievalContext | None = None

    async def validate_scope(self) -> None:
        if self.context is not None:
            await self.context.vectors.validate_scope()

    async def events(self) -> AsyncGenerator[SSEEvent, None]:
        started = time.monotonic()
        p = self.pipeline
        context = await p.preparation.prepare(self.principal, self.query)
        self.context = context
        await self.validate_scope()
        yield MetaEvent(
            event="meta",
            id=1,
            data=MetaData(
                request_id=self.request_id,
                session_id=context.scope.session_id,
                scope_revision=context.scope.scope_revision,
                domain=context.domain.id,
                history=context.history_metadata,
            ),
        )
        retrieval_started = time.monotonic()
        retrieved = await p.retrieval.retrieve(context)
        selection = await p.selector.select(context, retrieved)
        ordinal = 1
        async with aclosing(
            p.assembler.stream(
                context,
                selection,
                self.request_id,
                sentence_chars=p.policy.sentence_chars,
                retrieval_ms=(time.monotonic() - retrieval_started) * 1000,
                started=started,
            )
        ) as answers:
            async for item in answers:
                await self.validate_scope()
                ordinal += 1
                if isinstance(item, QueryResponse):
                    yield DoneEvent(event="done", id=ordinal, data=item)
                elif isinstance(item, Evidence):
                    yield EvidenceEvent(event="evidence", id=ordinal, data=item)
                else:
                    yield AnswerDeltaEvent(
                        event="answer_delta", id=ordinal, data=DeltaData(text=item)
                    )


class StreamingAnswerPipeline:
    def __init__(
        self,
        preparation: QueryPreparation,
        retrieval: RetrievalPipeline,
        selector: EvidenceSelector,
        assembler: AnswerAssembler,
        policy: StreamPolicy | None = None,
    ) -> None:
        self.preparation = preparation
        self.retrieval = retrieval
        self.selector = selector
        self.assembler = assembler
        self.policy = StreamPolicy.model_validate((policy or StreamPolicy()).model_dump())

    def query(
        self, principal: Principal, query: QueryRequest, request_id: UUID
    ) -> ScopedAnswerStream:
        return ScopedAnswerStream(self, principal, query, request_id)
