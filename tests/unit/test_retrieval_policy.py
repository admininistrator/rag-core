"""Supplemental config/deadline/cancel gates; real retrieval success is tested separately."""

import asyncio
from uuid import uuid4

import pytest
from pydantic import ValidationError

from rag_core.application.query import ScopedRetrievalContext, ScopedVectors
from rag_core.application.retrieval import RetrievalPipeline
from rag_core.auth import Principal
from rag_core.domain.metadata import ScopeError, ScopeSnapshot, VersionGeneration
from rag_core.domain.models import InferenceError, InferenceResult
from rag_core.domain.query import DomainConfig, DomainDefinition, FrozenHistoryMetadata
from rag_core.domain.retrieval import RetrievalError, RetrievalPolicy

pytestmark = pytest.mark.unit
FINGERPRINT = "a" * 64


@pytest.mark.parametrize(
    "kwargs",
    [
        {"prefetch_limit": 0},
        {"prefetch_limit": 101},
        {"prefetch_limit": True},
        {"top_k": 0},
        {"top_k": 21},
        {"candidate_budget": 0},
        {"candidate_budget": 21},
        {"prefetch_limit": 1, "top_k": 2},
        {"top_k": 2, "candidate_budget": 1},
        {"neighbor_anchors": -1},
        {"neighbor_anchors": 21},
        {"top_k": 1, "neighbor_anchors": 2},
        {"neighbor_radius": -1},
        {"neighbor_radius": 4},
        {"branch": "global"},
        {"timeout_seconds": 0.0},
        {"timeout_seconds": 120.1},
        {"timeout_seconds": float("nan")},
        {"timeout_seconds": float("inf")},
        {"fusion": "raw-score-sum"},
        {"gold_document_ids": []},
    ],
)
def test_invalid_profiles_fail_closed(kwargs):
    with pytest.raises(ValidationError):
        RetrievalPolicy(**kwargs)


def test_profile_exact_min_max_json_and_frozen():
    for policy in (
        RetrievalPolicy(
            prefetch_limit=1,
            top_k=1,
            candidate_budget=1,
            neighbor_anchors=1,
            neighbor_radius=0,
            timeout_seconds=0.001,
        ),
        RetrievalPolicy(
            prefetch_limit=100, neighbor_anchors=20, neighbor_radius=3, timeout_seconds=120.0
        ),
    ):
        round_trip = RetrievalPolicy.model_validate_json(policy.model_dump_json())
        assert round_trip == policy and round_trip.fingerprint == policy.fingerprint
        with pytest.raises(ValidationError):
            policy.top_k = 2
    assert RetrievalPolicy().fingerprint != RetrievalPolicy(branch="dense").fingerprint


class Sessions:
    stale = False

    async def validate_snapshot(self, scope):
        if self.stale:
            raise ScopeError("session_scope_changed")


class BlockedModel:
    def __init__(self):
        self.entered = asyncio.Event()
        self.cancelled = False
        self.calls = []

    async def infer(self, request):
        self.calls.append(request)
        self.entered.set()
        try:
            await asyncio.Event().wait()
        finally:
            self.cancelled = True


def context(sessions, *, pairs=None, policy="hybrid-v1"):
    scope = ScopeSnapshot(
        Principal("synthetic", "user"),
        uuid4(),
        1,
        None,
        pairs if pairs is not None else (VersionGeneration(uuid4(), uuid4(), uuid4()),),
    )
    return ScopedRetrievalContext(
        scope,
        DomainDefinition(
            id="default", subset_policy="all", config=DomainConfig(retrieval_policy=policy)
        ),
        "synthetic question",
        "en",
        None,
        FrozenHistoryMetadata(
            received_messages=0,
            retained_messages=0,
            received_tokens=0,
            retained_tokens=0,
            truncated=False,
        ),
        ScopedVectors(None, sessions, scope, None),
    )


@pytest.mark.asyncio
async def test_deadline_and_external_cancellation_propagate_to_model():
    sessions = Sessions()
    models = BlockedModel()
    with pytest.raises(RetrievalError, match="retrieval_timeout"):
        await RetrievalPipeline(
            models, FINGERPRINT, {"hybrid-v1": RetrievalPolicy(timeout_seconds=0.01)}
        ).retrieve(context(sessions))
    assert models.cancelled and models.calls[0].priority == "query"
    models = BlockedModel()
    task = asyncio.create_task(RetrievalPipeline(models, FINGERPRINT).retrieve(context(sessions)))
    await models.entered.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert models.cancelled


@pytest.mark.asyncio
async def test_unknown_stale_and_empty_have_no_inference_or_unscoped_reads():
    models = BlockedModel()
    sessions = Sessions()
    pipeline = RetrievalPipeline(models, FINGERPRINT)
    with pytest.raises(RetrievalError, match="unknown_retrieval_policy"):
        await pipeline.retrieve(context(sessions, policy="unknown"))
    sessions.stale = True
    with pytest.raises(ScopeError, match="session_scope_changed"):
        await pipeline.retrieve(context(sessions))
    sessions.stale = False
    empty = await pipeline.retrieve(context(sessions, pairs=()))
    assert not empty.candidates and empty.trace.score_kind == "none" and not models.calls


@pytest.mark.parametrize(
    "result,code",
    [
        (InferenceResult(fingerprint="b" * 64), "model_revision_mismatch"),
        (InferenceResult(fingerprint=FINGERPRINT), "model_invalid_response"),
        (InferenceResult(fingerprint=FINGERPRINT, scores=(1.0,)), "model_invalid_response"),
    ],
)
@pytest.mark.asyncio
async def test_invalid_model_results_are_technical_not_empty_success(result, code):
    class Model:
        async def infer(self, request):
            return result

    with pytest.raises(InferenceError, match=code):
        await RetrievalPipeline(Model(), FINGERPRINT).retrieve(context(Sessions()))


def test_constructed_bad_profile_revalidated_and_empty_registry_rejected():
    with pytest.raises(ValidationError):
        RetrievalPipeline(
            BlockedModel(),
            FINGERPRINT,
            {"hybrid-v1": RetrievalPolicy.model_construct(prefetch_limit=0)},
        )
    with pytest.raises(RetrievalError, match="invalid_retrieval_profiles"):
        RetrievalPipeline(BlockedModel(), FINGERPRINT, {})
