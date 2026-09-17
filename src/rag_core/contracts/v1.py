"""API v1 shapes and structural validation, independent of web/provider SDKs.

Ownership, upload allowlists, readiness, tokenizer budgets and scope revision
revalidation require runtime services in later tasks. History remains untrusted
input and is accepted above its processing budget for notified truncation.
"""

from __future__ import annotations

import re
from typing import Annotated, Literal, Self
from uuid import UUID

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator

Domain = Literal["default", "document", "multilingual"]
Language = Literal["en", "vi"]
SessionStatus = Literal["active", "deleted"]
LinkStatus = Literal["attached", "detached"]
JobState = Literal[
    "queued",
    "fetching",
    "parsing",
    "chunking",
    "embedding",
    "indexing",
    "ready",
    "failed",
    "cancelled",
]
Answerability = Literal["supported", "insufficient_evidence"]
ReasonCode = Literal["no_relevant_evidence", "conflicting_evidence"]
ErrorCode = Literal[
    "invalid_credentials",
    "forbidden",
    "not_found",
    "session_deleted",
    "no_session_documents",
    "documents_not_ready",
    "idempotency_conflict",
    "session_scope_changed",
    "invalid_request",
    "rate_limited",
    "busy",
    "provider_error",
    "dependency_unavailable",
    "timeout",
    "invalid_citation",
    "source_changed",
    "unsupported_format",
    "file_too_large",
    "page_limit_exceeded",
    "extraction_failed",
    "job_not_retryable",
    "not_implemented",
    "internal_error",
]


def _nonblank(value: str) -> str:
    if not value.strip():
        raise ValueError("Text must contain a non-whitespace character")
    return value


Text = Annotated[str, Field(min_length=1, pattern=r"\S"), AfterValidator(_nonblank)]
PositiveInt = Annotated[int, Field(strict=True, gt=0)]
NonnegativeInt = Annotated[int, Field(strict=True, ge=0)]
NonnegativeFloat = Annotated[float, Field(strict=True, ge=0, allow_inf_nan=False)]
Milliseconds = NonnegativeFloat
CitationId = Annotated[str, Field(pattern=r"^c[1-9][0-9]*$")]


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True, validate_default=True)


class ContractLimits(ContractModel):
    """Server processing config, never a client-controlled query override."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)
    documents_per_session: PositiveInt = 50
    file_bytes: PositiveInt = 100 * 1024 * 1024
    pages_per_file: PositiveInt = 1000
    history_messages: PositiveInt = 20
    history_tokens: PositiveInt = 8000
    question_characters: PositiveInt = 4000
    context_tokens: PositiveInt = 8000
    output_tokens: PositiveInt = 1024


INITIAL_LIMITS = ContractLimits()


class FileMeasurements(ContractModel):
    """Initial file limits on measured content, not trusted request declarations."""

    size_bytes: Annotated[int, Field(strict=True, gt=0, le=INITIAL_LIMITS.file_bytes)]
    pages: Annotated[int, Field(strict=True, gt=0, le=INITIAL_LIMITS.pages_per_file)] | None


class HistoryMessage(ContractModel):
    role: Literal["user", "assistant"]
    content: Text


class QueryRequest(ContractModel):
    model_config = ConfigDict(
        extra="forbid",
        hide_input_in_errors=True,
        validate_default=True,
        json_schema_extra={
            "allOf": [
                {
                    "if": {"properties": {"domain": {"const": "document"}}, "required": ["domain"]},
                    "then": {
                        "required": ["document_ids"],
                        "properties": {"document_ids": {"type": "array"}},
                    },
                },
                {
                    "if": {
                        "anyOf": [
                            {"not": {"required": ["domain"]}},
                            {"properties": {"domain": {"const": "default"}}},
                        ]
                    },
                    "then": {"not": {"required": ["document_ids"]}},
                },
            ],
            "x-runtime-enforcement": [
                "authenticated principal/current session/ready versions/subset ownership",
                "history truncation with metadata at 20 messages/8000 tokenizer tokens",
                "context 8000/output 1024 tokenizer tokens; scope revalidation",
            ],
        },
    )
    session_id: UUID
    domain: Domain = "default"
    question: Annotated[Text, Field(max_length=INITIAL_LIMITS.question_characters)]
    document_ids: (
        Annotated[
            list[UUID], Field(min_length=1, max_length=50, json_schema_extra={"uniqueItems": True})
        ]
        | None
    ) = Field(
        default=None,
        exclude_if=lambda value: value is None,
    )
    history: list[HistoryMessage] = Field(
        default_factory=list,
        description=(
            "Untrusted conversation, never factual evidence. Above-budget history is accepted; "
            "runtime must truncate and report counts, not silently reject or retain all."
        ),
    )
    corpus_languages: (
        Annotated[
            list[Language],
            Field(min_length=1, max_length=2, json_schema_extra={"uniqueItems": True}),
        ]
        | None
    ) = None
    answer_language: Language | None = None

    @model_validator(mode="after")
    def validate_subset(self) -> Self:
        if self.domain == "default" and "document_ids" in self.model_fields_set:
            raise ValueError("Default domain does not accept document_ids")
        if self.domain == "document" and self.document_ids is None:
            raise ValueError("Document domain requires nonempty document_ids")
        if self.document_ids is not None and len(set(self.document_ids)) != len(self.document_ids):
            raise ValueError("document_ids must be unique")
        if self.corpus_languages is not None and len(set(self.corpus_languages)) != len(
            self.corpus_languages
        ):
            raise ValueError("corpus_languages must be unique")
        return self


class SessionCreateRequest(ContractModel):
    external_session_id: Text


class SessionResponse(ContractModel):
    request_id: UUID
    session_id: UUID
    external_session_id: Text
    status: SessionStatus
    scope_revision: NonnegativeInt


class SourceReference(ContractModel):
    model_config = ConfigDict(
        extra="forbid",
        hide_input_in_errors=True,
        json_schema_extra={
            "anyOf": [
                {"required": ["version_id"], "properties": {"version_id": {"type": "string"}}},
                {"required": ["sha256"], "properties": {"sha256": {"type": "string"}}},
            ],
            "x-runtime-enforcement": "Trusted storage alias/bucket/prefix/owner/session; HEAD/GET only",
        },
    )
    storage_alias: Annotated[Text, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]*$")]
    bucket: Text
    key: Text
    version_id: Text | None = Field(
        default=None,
        description=("Opaque storage object version, distinct from the core DocumentVersion UUID."),
    )
    sha256: Annotated[str, Field(pattern=r"^[a-fA-F0-9]{64}$")] | None = None

    @model_validator(mode="after")
    def require_immutable_reference(self) -> Self:
        if self.version_id is None and self.sha256 is None:
            raise ValueError("Source requires version_id or SHA-256")
        return self


class DocumentRegisterRequest(ContractModel):
    external_upload_id: Text
    source: SourceReference
    filename: Text
    content_type: Text


class DocumentResponse(ContractModel):
    document_id: UUID
    version_id: UUID = Field(description="Core DocumentVersion UUID, not storage version_id")
    filename: Text
    link_status: LinkStatus
    state: JobState


class DocumentListResponse(ContractModel):
    request_id: UUID
    session_id: UUID
    scope_revision: NonnegativeInt
    documents: Annotated[list[DocumentResponse], Field(max_length=50)]
    next_cursor: Text | None


class ErrorDetail(ContractModel):
    """Safe structured detail: no input values, arbitrary debug text or credentials."""

    field: (
        Literal[
            "session_id",
            "domain",
            "question",
            "document_ids",
            "history",
            "corpus_languages",
            "answer_language",
            "source",
            "filename",
            "content_type",
            "idempotency_key",
        ]
        | None
    ) = None
    reason: Literal[
        "missing",
        "invalid",
        "too_large",
        "not_ready",
        "conflict",
        "scope_changed",
        "unsupported",
        "unavailable",
    ]


class ErrorBody(ContractModel):
    code: ErrorCode
    message: Text = Field(description="Public safe message; adapter must redact exception text")
    retryable: Annotated[bool, Field(strict=True)]
    details: list[ErrorDetail] | None = None


class ErrorEnvelope(ContractModel):
    error: ErrorBody
    request_id: UUID


class JobResponse(ContractModel):
    request_id: UUID
    job_id: UUID
    document_id: UUID
    version_id: UUID
    state: JobState
    progress: Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)] | None
    error: ErrorBody | None
    retryable: Annotated[bool, Field(strict=True)]


class DocumentRegisterResponse(ContractModel):
    request_id: UUID
    session_id: UUID
    scope_revision: NonnegativeInt
    document: DocumentResponse
    job: JobResponse


class DetachResponse(ContractModel):
    request_id: UUID
    session_id: UUID
    document_id: UUID
    link_status: Literal["detached"]
    scope_revision: NonnegativeInt


class OffsetRange(ContractModel):
    start: NonnegativeInt
    end: PositiveInt

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.end <= self.start:
            raise ValueError("Offset end must be greater than start (half-open range)")
        return self


class PdfLocator(ContractModel):
    kind: Literal["pdf"]
    page: PositiveInt = Field(description="Physical one-based page, never printed page label")
    printed_page_label: Text | None = None
    block: NonnegativeInt | None = None
    offsets: OffsetRange | None = None


class DocxLocator(ContractModel):
    kind: Literal["docx"]
    heading_path: list[Text]
    paragraph: NonnegativeInt | None = None
    table: NonnegativeInt | None = None
    offsets: OffsetRange | None = None

    @model_validator(mode="after")
    def require_position(self) -> Self:
        if self.paragraph is None and self.table is None:
            raise ValueError("DOCX requires paragraph or table index")
        return self


class XlsxLocator(ContractModel):
    kind: Literal["xlsx"]
    sheet: Text
    cell_range: Annotated[str, Field(pattern=r"^[A-Z]{1,3}[1-9][0-9]*(?::[A-Z]{1,3}[1-9][0-9]*)?$")]
    headers: list[Text] = Field(default_factory=list)
    unit: Text | None = None

    @model_validator(mode="after")
    def valid_excel_range(self) -> Self:
        positions = []
        for cell in self.cell_range.split(":"):
            match = re.fullmatch(r"([A-Z]+)([0-9]+)", cell)
            assert match is not None  # constrained field already checks the cell syntax
            column = 0
            for letter in match[1]:
                column = column * 26 + ord(letter) - ord("A") + 1
            row = int(match[2])
            if column > 16384 or row > 1048576:
                raise ValueError("Cell exceeds XLSX sheet bounds")
            positions.append((column, row))
        if len(positions) == 2 and any(a > b for a, b in zip(*positions, strict=True)):
            raise ValueError("Cell range must be ordered")
        return self


class PptxLocator(ContractModel):
    kind: Literal["pptx"]
    slide: PositiveInt
    shape: NonnegativeInt | None = None
    block: NonnegativeInt | None = None


class TextLocator(ContractModel):
    kind: Literal["txt", "md"]
    line_start: PositiveInt | None = None
    line_end: PositiveInt | None = None
    paragraph: NonnegativeInt | None = None
    offsets: OffsetRange | None = None

    @model_validator(mode="after")
    def valid_position(self) -> Self:
        if (self.line_start is None) != (self.line_end is None):
            raise ValueError("Text line range requires both boundaries")
        if self.line_start is None and self.paragraph is None:
            raise ValueError("Text requires a line range or paragraph index")
        if (
            self.line_start is not None
            and self.line_end is not None
            and self.line_end < (self.line_start)
        ):
            raise ValueError("Text line range must be ordered")
        return self


class CsvLocator(ContractModel):
    kind: Literal["csv"]
    row_start: PositiveInt
    row_end: PositiveInt
    columns: Annotated[list[Text], Field(min_length=1)]

    @model_validator(mode="after")
    def ordered_rows(self) -> Self:
        if self.row_end < self.row_start:
            raise ValueError("CSV row range must be ordered")
        return self


class HtmlLocator(ContractModel):
    kind: Literal["html"]
    heading_path: list[Text]
    block: NonnegativeInt
    offsets: OffsetRange | None = None


class BoundingBox(ContractModel):
    """Pixel coordinates in the original image; no inferred measurements."""

    x0: NonnegativeFloat
    y0: NonnegativeFloat
    x1: NonnegativeFloat
    y1: NonnegativeFloat

    @model_validator(mode="after")
    def ordered_box(self) -> Self:
        if self.x1 <= self.x0 or self.y1 <= self.y0:
            raise ValueError("Bounding box must have positive width and height")
        return self


class ImageLocator(ContractModel):
    kind: Literal["image"]
    image_id: Text
    ocr_block: NonnegativeInt | None = None
    bbox: BoundingBox | None = None


SourceLocator = Annotated[
    PdfLocator
    | DocxLocator
    | XlsxLocator
    | PptxLocator
    | TextLocator
    | CsvLocator
    | HtmlLocator
    | ImageLocator,
    Field(discriminator="kind"),
]


class Citation(ContractModel):
    id: CitationId
    document_id: UUID
    version_id: UUID
    chunk_id: Text
    filename: Text
    locator: SourceLocator
    quote: Text


class EvidenceContext(ContractModel):
    chunk_id: Text
    document_id: UUID
    text: Text
    citation_ids: Annotated[list[CitationId], Field(min_length=1)]


class Evidence(ContractModel):
    answerability: Answerability
    citations: list[Citation]
    contexts: list[EvidenceContext]

    @model_validator(mode="after")
    def validate_evidence_links(self) -> Self:
        ids = {citation.id: citation for citation in self.citations}
        if len(ids) != len(self.citations):
            raise ValueError("Citation IDs must be unique")
        if self.answerability == "supported" and not ids:
            raise ValueError("Supported evidence requires citations")
        chunks = set()
        for context in self.contexts:
            if context.chunk_id in chunks:
                raise ValueError("Evidence context chunk IDs must be unique")
            chunks.add(context.chunk_id)
            if len(set(context.citation_ids)) != len(context.citation_ids):
                raise ValueError("Context citation IDs must be unique")
            for citation_id in context.citation_ids:
                citation = ids.get(citation_id)
                if citation is None or (citation.document_id, citation.chunk_id) != (
                    context.document_id,
                    context.chunk_id,
                ):
                    raise ValueError("Context citation must reference the same document/chunk")
        return self


class Usage(ContractModel):
    provider: Text | None = None
    model: Text | None = None
    input_tokens: NonnegativeInt | None = None
    output_tokens: NonnegativeInt | None = None


class Timings(ContractModel):
    retrieval: Milliseconds | None = None
    generation: Milliseconds | None = None
    total: Milliseconds | None = None


class HistoryMetadata(ContractModel):
    received_messages: NonnegativeInt
    retained_messages: Annotated[int, Field(strict=True, ge=0, le=20)]
    received_tokens: NonnegativeInt | None
    retained_tokens: Annotated[int, Field(strict=True, ge=0, le=8000)] | None
    truncated: Annotated[bool, Field(strict=True)]

    @model_validator(mode="after")
    def consistent_counts(self) -> Self:
        if self.retained_messages > self.received_messages:
            raise ValueError("History retained messages exceed received messages")
        if (self.received_tokens is None) != (self.retained_tokens is None):
            raise ValueError("History token counts must both be known or both be null")
        tokens_removed = False
        if self.received_tokens is not None and self.retained_tokens is not None:
            if self.retained_tokens > self.received_tokens:
                raise ValueError("History retained tokens exceed received tokens")
            tokens_removed = self.retained_tokens < self.received_tokens
        if self.truncated != (self.retained_messages < self.received_messages or tokens_removed):
            raise ValueError("History truncated flag must match the measured counts")
        return self


class HistoryWarning(ContractModel):
    code: Literal["history_truncated"]
    message: Text
    history: HistoryMetadata

    @model_validator(mode="after")
    def require_truncation(self) -> Self:
        if not self.history.truncated:
            raise ValueError("history_truncated warning requires truncated metadata")
        return self


class QueryResponse(Evidence):
    request_id: UUID
    session_id: UUID
    scope_revision: NonnegativeInt
    domain: Domain
    answer: Text
    reason_code: ReasonCode | None
    usage: Usage
    timings_ms: Timings
    warnings: list[HistoryWarning]

    @model_validator(mode="after")
    def consistent_answer(self) -> Self:
        if (self.answerability == "supported") != (self.reason_code is None):
            raise ValueError(
                "Supported answer has null reason; insufficient answer requires reason"
            )
        if self.reason_code == "no_relevant_evidence" and (self.citations or self.contexts):
            raise ValueError("No relevant evidence cannot contain fabricated evidence")
        # This is structural ID checking, not factual support/quote/ownership validation.
        referenced = set(re.findall(r"\[(c[1-9][0-9]*)\]", self.answer))
        allowed = {citation.id for citation in self.citations}
        if not referenced <= allowed or (self.answerability == "supported" and not referenced):
            raise ValueError("Answer must use permitted citation IDs; supported answer must cite")
        return self


class CitationResolveResponse(ContractModel):
    request_id: UUID
    session_id: UUID
    scope_revision: NonnegativeInt
    citation: Citation


class LiveResponse(ContractModel):
    status: Literal["ok"]


class ReadyComponents(ContractModel):
    postgres: Literal["ok", "unavailable"]
    redis: Literal["ok", "unavailable"]
    qdrant: Literal["ok", "unavailable"]


class ReadyResponse(ContractModel):
    status: Literal["ready", "unavailable"]
    components: ReadyComponents
