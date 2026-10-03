"""Trusted retrieval profiles and metadata-only diagnostics, independent of SDKs."""

import hashlib
from dataclasses import dataclass
from typing import Annotated, Literal

from pydantic import Field, model_validator

from rag_core.domain.query import FrozenModel
from rag_core.domain.vectors import SearchBranch, VectorHit

ScoreKind = Literal["cosine", "sparse-dot", "rrf", "none"]


class RetrievalError(Exception):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class RetrievalPolicy(FrozenModel):
    branch: SearchBranch = "hybrid"
    # T18 Qdrant RRF uses equal weights and zero-based rank + k=2.
    fusion: Literal["qdrant-rrf-k2-v1"] = "qdrant-rrf-k2-v1"
    prefetch_limit: Annotated[int, Field(strict=True, ge=1, le=100)] = 30
    top_k: Annotated[int, Field(strict=True, ge=1, le=20)] = 20
    candidate_budget: Annotated[int, Field(strict=True, ge=1, le=20)] = 20
    neighbor_anchors: Annotated[int, Field(strict=True, ge=0, le=20)] = 0
    neighbor_radius: Annotated[int, Field(strict=True, ge=0, le=3)] = 1
    timeout_seconds: Annotated[float, Field(strict=True, gt=0, le=120, allow_inf_nan=False)] = 60.0

    @model_validator(mode="after")
    def budgets(self) -> "RetrievalPolicy":
        if self.top_k > min(self.prefetch_limit, self.candidate_budget):
            raise ValueError("invalid_retrieval_budget")
        if self.neighbor_anchors > self.top_k:
            raise ValueError("invalid_neighbor_budget")
        return self

    @property
    def fingerprint(self) -> str:
        return hashlib.sha256(self.model_dump_json().encode()).hexdigest()


class RetrievalTrace(FrozenModel):
    """Safe to serialize explicitly for evaluation; no query/content/identity/IDs.

    Vector metadata in RetrievalResult remains scoped private data, not a log payload.
    Scores are rankings only; neither cosine nor RRF establishes factual support.
    """

    schema_version: Literal[1] = 1
    policy: RetrievalPolicy
    policy_fingerprint: str
    model_fingerprint: str
    corpus_languages: tuple[str, ...] | None
    allowed_documents: int
    seed_count: int
    neighbor_calls: int
    neighbor_count: int
    candidate_count: int
    score_kind: ScoreKind
    elapsed_ms: float = Field(ge=0, allow_inf_nan=False)


@dataclass(frozen=True)
class RetrievalResult:
    # Ranked seeds first; unscored neighbors follow in anchor/ordinal order.
    # A neighbor's None score is never mixed into cosine/RRF ranking.
    candidates: tuple[VectorHit, ...]
    trace: RetrievalTrace
