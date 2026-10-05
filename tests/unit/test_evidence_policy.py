"""Supplemental budget/technical-error gates; actual weights are separate DoD tests."""

from dataclasses import replace
from uuid import uuid4

import pytest
from pydantic import ValidationError

from rag_core.application.evidence import EvidenceSelector
from rag_core.application.query import ScopedRetrievalContext, ScopedVectors
from rag_core.auth import Principal
from rag_core.contracts.v1 import PdfLocator
from rag_core.domain.chunking import Chunk, SourceSegment
from rag_core.domain.documents import SourceIdentity
from rag_core.domain.evidence import EvidenceError, EvidencePolicy
from rag_core.domain.metadata import ScopeSnapshot, VersionGeneration
from rag_core.domain.models import InferenceError, InferenceResult
from rag_core.domain.query import DomainDefinition, FrozenHistoryMetadata
from rag_core.domain.retrieval import RetrievalPolicy, RetrievalResult, RetrievalTrace
from rag_core.domain.vectors import VectorChunk, VectorHit

pytestmark = pytest.mark.unit
FINGERPRINT = "a" * 64


@pytest.mark.parametrize(
    "kwargs",
    [
        {"candidate_limit": 0},
        {"candidate_limit": 21},
        {"candidate_limit": True},
        {"passage_limit": 0},
        {"passage_limit": 9},
        {"passage_limit": 2, "candidate_limit": 1},
        {"minimum_passages": 2, "passage_limit": 1},
        {"minimum_passages": 0},
        {"context_tokens": 0},
        {"context_tokens": 8001},
        {"context_tokens": True},
        {"raw_score_floor": float("nan")},
        {"raw_score_floor": float("inf")},
        {"timeout_seconds": 0.0},
        {"timeout_seconds": 120.1},
        {"calibration": "complete"},
        {"revision": "unversioned"},
        {"confidence": 0.9},
        {"conflict_policy": "unbounded-semantic-agent"},
    ],
)
def test_invalid_evidence_config(kwargs):
    with pytest.raises(ValidationError):
        EvidencePolicy(**kwargs)


def test_policy_roundtrip_fingerprint_and_immutable():
    for policy in (
        EvidencePolicy(),
        EvidencePolicy(candidate_limit=1, passage_limit=1, context_tokens=1, timeout_seconds=0.001),
    ):
        assert EvidencePolicy.model_validate_json(policy.model_dump_json()) == policy
        with pytest.raises(ValidationError):
            policy.context_tokens = 9000
    assert EvidencePolicy().fingerprint != EvidencePolicy(raw_score_floor=1.0).fingerprint


class Tokenizer:
    fingerprint = "synthetic-only"

    def count(self, value):
        return len(value)


class Collaborators:
    def __init__(self, chunks, vectors):
        self.chunks, self.vectors = chunks, vectors
        self.response = InferenceResult(fingerprint=FINGERPRINT, scores=(1.0, 2.0))
        self.requests = []

    async def validate_snapshot(self, scope):
        pass

    async def fetch(self, scope, ids, *, languages=None):
        return tuple(VectorHit(v) for v in self.vectors if v.chunk_id in ids)

    async def hydrate(self, scope, candidates):
        return tuple(c for v in candidates for c in self.chunks if c.id == v.chunk_id)

    async def infer(self, request):
        self.requests.append(request)
        return self.response


def setup(policy=None):
    pair = VersionGeneration(uuid4(), uuid4(), uuid4())
    locator = PdfLocator(kind="pdf", page=1)
    chunks = tuple(
        Chunk(
            uuid4(),
            SourceIdentity(
                document_id=pair.document_id, version_id=pair.version_id, sha256="a" * 64
            ),
            pair.generation_id,
            i,
            value,
            1,
            "a" * 64,
            "a" * 64,
            "a" * 64,
            (),
            (SourceSegment(0, len(value), i, 0, len(value), locator),),
        )
        for i, value in enumerate(("long passage", "short"))
    )
    vectors = tuple(
        VectorChunk(
            document_id=pair.document_id,
            document_version_id=pair.version_id,
            index_generation=pair.generation_id,
            chunk_id=c.id,
            language="en",
            ordinal=c.ordinal,
            unit_id="synthetic-unit",
            locator=locator,
        )
        for c in chunks
    )
    collaborators = Collaborators(chunks, vectors)
    scope = ScopeSnapshot(Principal("synthetic", "owner"), uuid4(), 1, None, (pair,))
    ctx = ScopedRetrievalContext(
        scope,
        DomainDefinition(id="default", subset_policy="all"),
        "question",
        "en",
        None,
        FrozenHistoryMetadata(
            received_messages=0,
            retained_messages=0,
            received_tokens=0,
            retained_tokens=0,
            truncated=False,
        ),
        ScopedVectors(collaborators, collaborators, scope, None),
    )
    retrieval = RetrievalResult(
        tuple(VectorHit(v) for v in vectors),
        RetrievalTrace(
            policy=RetrievalPolicy(),
            policy_fingerprint="test",
            model_fingerprint=FINGERPRINT,
            corpus_languages=None,
            allowed_documents=1,
            seed_count=2,
            neighbor_calls=0,
            neighbor_count=0,
            candidate_count=2,
            score_kind="rrf",
            elapsed_ms=0,
        ),
    )
    selector = EvidenceSelector(
        collaborators,
        collaborators,
        FINGERPRINT,
        Tokenizer(),
        {"bounded-v1": policy or EvidencePolicy()},
    )
    return ctx, retrieval, selector, collaborators


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "response,code",
    [
        (InferenceResult(fingerprint="b" * 64, scores=(1.0, 2.0)), "model_revision_mismatch"),
        (InferenceResult(fingerprint=FINGERPRINT, scores=(1.0,)), "model_invalid_response"),
        (
            InferenceResult.model_construct(fingerprint=FINGERPRINT, scores=(float("nan"), 2.0)),
            "model_invalid_response",
        ),
    ],
)
async def test_model_failure_never_becomes_insufficient(response, code):
    ctx, retrieval, selector, collaborators = setup()
    collaborators.response = response
    with pytest.raises(InferenceError, match=code):
        await selector.select(ctx, retrieval)


@pytest.mark.asyncio
async def test_ranking_skip_whole_passage_minimum_coverage_and_context_tamper():
    ctx, retrieval, selector, c = setup(EvidencePolicy(context_tokens=10, minimum_passages=2))
    selected = await selector.select(ctx, retrieval)
    assert (
        selected.answerability == "insufficient_evidence"
        and selected.reason == "insufficient_coverage"
    )
    assert selected.passages[0].chunk.text == "short"
    assert selected.passages[0].raw_score == 2.0
    assert c.requests[0].priority == "query" and c.requests[0].operation == "rerank"
    assert c.requests[0].texts == [chunk.text for chunk in c.chunks]
    assert await selector.context_for_generation(ctx, selected) == ("[e1]\nshort",)
    forged = replace(selected, passages=(replace(selected.passages[0], id="fake-evidence"),))
    with pytest.raises(EvidenceError, match="invalid_evidence_selection"):
        await selector.context_for_generation(ctx, forged)


@pytest.mark.asyncio
async def test_empty_scope_candidates_and_duplicate_inputs():
    ctx, retrieval, selector, c = setup()
    empty = await selector.select(ctx, replace(retrieval, candidates=()))
    assert empty.reason == "no_relevant_evidence" and not c.requests
    with pytest.raises(EvidenceError, match="invalid_evidence_candidates"):
        await selector.select(ctx, replace(retrieval, candidates=(retrieval.candidates[0],) * 2))


def test_bypass_constructed_policy_is_revalidated():
    with pytest.raises(ValidationError):
        setup(EvidencePolicy.model_construct(context_tokens=8001))
