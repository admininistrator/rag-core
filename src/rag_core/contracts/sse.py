"""SSE payload/sequence contracts only; no streaming transport or provider runtime."""

from __future__ import annotations

from typing import Annotated, Literal, Self
from uuid import UUID

from pydantic import Field, RootModel, model_validator

from rag_core.contracts.v1 import (
    ContractModel,
    Domain,
    ErrorEnvelope,
    Evidence,
    HistoryMetadata,
    NonnegativeInt,
    PositiveInt,
    QueryResponse,
    Text,
)


class MetaData(ContractModel):
    request_id: UUID
    session_id: UUID
    scope_revision: NonnegativeInt
    domain: Domain
    history: HistoryMetadata


class MetaEvent(ContractModel):
    event: Literal["meta"]
    id: PositiveInt = Field(description="Monotonically increasing, request-local event ID")
    data: MetaData


class EvidenceEvent(ContractModel):
    event: Literal["evidence"]
    id: PositiveInt
    data: Evidence


class DeltaData(ContractModel):
    text: Annotated[str, Field(min_length=1)] = Field(
        description="Provisional text, including whitespace; persist only validated done response"
    )


class AnswerDeltaEvent(ContractModel):
    event: Literal["answer_delta"]
    id: PositiveInt
    data: DeltaData


class DoneEvent(ContractModel):
    event: Literal["done"]
    id: PositiveInt
    data: QueryResponse


class ErrorEvent(ContractModel):
    event: Literal["error"]
    id: PositiveInt
    data: ErrorEnvelope


SSEEvent = Annotated[
    MetaEvent | EvidenceEvent | AnswerDeltaEvent | DoneEvent | ErrorEvent,
    Field(discriminator="event"),
]


class SSEHeartbeat(ContractModel):
    """Wire heartbeat is a comment ': ...', without event/data/id fields."""

    comment: Text

    @model_validator(mode="after")
    def single_line(self) -> Self:
        if "\r" in self.comment or "\n" in self.comment:
            raise ValueError("Heartbeat comment must occupy a single line")
        return self


class SSESequence(RootModel[list[SSEEvent]]):
    """Validate a completed logical event trace, excluding heartbeat comments.

    Errors may terminate after meta before evidence (e.g. retrieval failure).
    A disconnected partial trace is incomplete and cannot pass this contract.
    This checker does not perform scope revalidation or factual citation audits.
    """

    @model_validator(mode="after")
    def ordered_complete_trace(self) -> Self:
        events = self.root
        if len(events) < 2 or not isinstance(events[0], MetaEvent):
            raise ValueError("Stream must begin with meta and contain a terminal event")
        meta = events[0].data
        evidence: Evidence | None = None
        previous_id = 0
        terminal = False
        for index, event in enumerate(events):
            if event.id <= previous_id:
                raise ValueError("Event IDs must strictly increase within the request")
            previous_id = event.id
            if terminal:
                raise ValueError("No events may follow a terminal event")
            if isinstance(event, MetaEvent):
                if index != 0:
                    raise ValueError("Stream has exactly one meta event")
            elif isinstance(event, EvidenceEvent):
                if index != 1 or evidence is not None:
                    raise ValueError("Evidence must occur exactly once immediately after meta")
                evidence = event.data
            elif isinstance(event, AnswerDeltaEvent):
                if evidence is None:
                    raise ValueError("Answer delta requires evidence first")
            elif isinstance(event, DoneEvent):
                if evidence is None:
                    raise ValueError("Done requires evidence first")
                response = event.data
                if (
                    response.request_id,
                    response.session_id,
                    response.scope_revision,
                    response.domain,
                ) != (meta.request_id, meta.session_id, meta.scope_revision, meta.domain):
                    raise ValueError("Done must retain the request/session/scope/domain from meta")
                if (response.answerability, response.citations, response.contexts) != (
                    evidence.answerability,
                    evidence.citations,
                    evidence.contexts,
                ):
                    raise ValueError("Done must retain the validated evidence allowlist")
                histories = [warning.history for warning in response.warnings]
                if meta.history.truncated and meta.history not in histories:
                    raise ValueError("Done must report the history truncation announced in meta")
                if any(history != meta.history for history in histories):
                    raise ValueError("Done history metadata must match meta")
                terminal = True
            elif isinstance(event, ErrorEvent):
                if event.data.request_id != meta.request_id:
                    raise ValueError("Error must retain the request ID from meta")
                terminal = True
        if not terminal:
            raise ValueError("Stream must end with exactly one done or error")
        return self
