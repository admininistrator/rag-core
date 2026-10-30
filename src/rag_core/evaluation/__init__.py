"""Evaluation harness and protocol against leakage for RAG Core."""

from rag_core.evaluation.adapters import (
    BaseGoldAdapter,
    BilingualGoldAdapter,
    DefaultGoldAdapter,
    FinanceBenchGoldAdapter,
)
from rag_core.evaluation.manifest import (
    EvaluationGateStatus,
    EvaluationRunManifest,
    GenerationMetricsSummary,
    RetrievalMetricsSummary,
    SliceEvaluationReport,
)
from rag_core.evaluation.metrics import (
    calculate_retrieval_metrics,
    citation_validity,
    compute_token_f1,
    exact_match,
    extract_numbers,
    f1_score,
    normalize_text,
    numeric_match,
    page_recall,
)
from rag_core.evaluation.protocol import (
    DatasetSplits,
    EvalSample,
    EvaluationLeakageError,
    EvaluationStage,
    GoldEvidence,
    SplitKind,
    generate_deterministic_splits,
    is_ingestable_document,
    load_splits,
)
from rag_core.evaluation.runner import EvaluationRunner

__all__ = [
    "BaseGoldAdapter",
    "BilingualGoldAdapter",
    "DatasetSplits",
    "DefaultGoldAdapter",
    "EvalSample",
    "EvaluationGateStatus",
    "EvaluationLeakageError",
    "EvaluationRunManifest",
    "EvaluationRunner",
    "EvaluationStage",
    "FinanceBenchGoldAdapter",
    "GenerationMetricsSummary",
    "GoldEvidence",
    "RetrievalMetricsSummary",
    "SliceEvaluationReport",
    "SplitKind",
    "calculate_retrieval_metrics",
    "citation_validity",
    "compute_token_f1",
    "exact_match",
    "extract_numbers",
    "f1_score",
    "generate_deterministic_splits",
    "is_ingestable_document",
    "load_splits",
    "normalize_text",
    "numeric_match",
    "page_recall",
]
