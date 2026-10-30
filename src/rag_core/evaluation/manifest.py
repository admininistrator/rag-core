"""Evaluation report and manifest schemas for RAG Core benchmarks."""

from pydantic import BaseModel, ConfigDict, Field

from rag_core.evaluation.protocol import SplitKind


class RetrievalMetricsSummary(BaseModel):
    """Aggregated retrieval metrics."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    recall_at_1: float = Field(ge=0.0, le=1.0)
    recall_at_5: float = Field(ge=0.0, le=1.0)
    recall_at_10: float = Field(ge=0.0, le=1.0)
    recall_at_20: float = Field(ge=0.0, le=1.0)
    mrr: float = Field(ge=0.0, le=1.0)
    ndcg_at_10: float = Field(ge=0.0, le=1.0)
    page_recall_at_5: float | None = Field(default=None, ge=0.0, le=1.0)
    page_recall_at_10: float | None = Field(default=None, ge=0.0, le=1.0)
    supporting_doc_recall_at_10: float | None = Field(default=None, ge=0.0, le=1.0)


class GenerationMetricsSummary(BaseModel):
    """Aggregated generation, faithfulness, and citation metrics."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    exact_match: float = Field(ge=0.0, le=1.0)
    f1: float = Field(ge=0.0, le=1.0)
    numeric_accuracy: float = Field(ge=0.0, le=1.0)
    citation_validity: float = Field(ge=0.0, le=1.0)
    faithfulness: float = Field(ge=0.0, le=1.0)


class SliceEvaluationReport(BaseModel):
    """Evaluation metrics for a specific domain slice and split."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    domain: str
    slice_name: str
    split: SplitKind
    sample_count: int = Field(ge=0)
    retrieval_baseline: RetrievalMetricsSummary
    retrieval_tuned: RetrievalMetricsSummary
    generation: GenerationMetricsSummary | None = None
    timings_ms: dict[str, float] = Field(default_factory=dict)


class EvaluationGateStatus(BaseModel):
    """Gate verification status."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    gate_name: str
    passed: bool
    expected: str
    actual: str
    details: str = ""


class EvaluationRunManifest(BaseModel):
    """Root evaluation run manifest."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: int = 1
    run_id: str
    timestamp: str
    git_commit: str
    platform: dict[str, str]
    mode: str
    config_fingerprint: str
    domains: dict[str, list[SliceEvaluationReport]]
    gates: list[EvaluationGateStatus]
    passed_all_gates: bool
    limitations: list[str] = Field(default_factory=list)
