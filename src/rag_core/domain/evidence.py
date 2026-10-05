"""Private, source-mapped evidence and versioned baseline gates, never confidence."""

import hashlib
from dataclasses import dataclass
from typing import Annotated, Literal

from pydantic import Field, model_validator

from rag_core.domain.chunking import Chunk
from rag_core.domain.metadata import ScopeSnapshot
from rag_core.domain.query import FrozenModel

EvidenceReason = Literal[
    "relevant_evidence",
    "no_relevant_evidence",
    "conflicting_evidence",
    "context_budget_exhausted",
    "insufficient_coverage",
]


class EvidenceError(Exception):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class EvidencePolicy(FrozenModel):
    revision: Literal["raw-m3-baseline-v1"] = "raw-m3-baseline-v1"
    calibration: Literal["pending-T31"] = "pending-T31"
    candidate_limit: Annotated[int, Field(strict=True, ge=1, le=20)] = 20
    passage_limit: Annotated[int, Field(strict=True, ge=1, le=8)] = 8
    context_tokens: Annotated[int, Field(strict=True, ge=1, le=8000)] = 8000
    minimum_passages: Annotated[int, Field(strict=True, ge=1, le=8)] = 1
    raw_score_floor: Annotated[float, Field(strict=True, allow_inf_nan=False)] = 0.0
    timeout_seconds: Annotated[float, Field(strict=True, gt=0, le=120, allow_inf_nan=False)] = 60.0

    @model_validator(mode="after")
    def budgets(self) -> "EvidencePolicy":
        if self.minimum_passages > self.passage_limit or self.passage_limit > self.candidate_limit:
            raise ValueError("invalid_evidence_budget")
        return self

    @property
    def fingerprint(self) -> str:
        return hashlib.sha256(self.model_dump_json().encode()).hexdigest()


@dataclass(frozen=True)
class EvidencePassage:
    id: str
    chunk: Chunk
    raw_score: float
    context_tokens: int

    @property
    def context_text(self) -> str:
        # This is untrusted evidence data, not a system prompt. T24 owns framing.
        return f"[{self.id}]\n{self.chunk.text}"


class EvidenceTrace(FrozenModel):
    schema_version: Literal[1] = 1
    policy: EvidencePolicy
    policy_fingerprint: str
    model_fingerprint: str
    tokenizer_fingerprint: str
    candidate_count: int
    relevant_count: int
    selected_count: int
    context_tokens: int
    budget_skipped: int
    elapsed_ms: float = Field(ge=0, allow_inf_nan=False)


@dataclass(frozen=True)
class EvidenceSelection:
    scope: ScopeSnapshot
    answerability: Literal["supported", "insufficient_evidence"]
    reason: EvidenceReason
    passages: tuple[EvidencePassage, ...]
    trace: EvidenceTrace
