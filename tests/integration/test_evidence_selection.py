"""T22 required acceptance: real multilingual reranker, PG source maps and Qdrant."""

import asyncio
from dataclasses import replace

import pytest

from rag_core.domain.evidence import EvidenceError, EvidencePolicy
from rag_core.domain.models import InferenceError
from tests.fixtures.evidence_support import evidence_corpus, seed
from tests.integration.test_qdrant_scope import fixture
from tests.integration.test_retrieval import real_models

__all__ = ["evidence_corpus", "fixture", "real_models"]
pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


@pytest.mark.parametrize(
    "question,language,label",
    [
        ("What is Vietnam's capital?", "vi", "capital-vi"),
        ("Thủ đô của Việt Nam là gì?", "en", "capital-en"),
    ],
)
async def test_relevant_cross_language_and_provenance(evidence_corpus, question, language, label):
    e = evidence_corpus
    ctx, retrieval, selector = await e.query(
        question, labels=(label, "fish"), languages=(language,)
    )
    selected = await selector.select(ctx, retrieval)
    assert selected.answerability == "supported" and selected.reason == "relevant_evidence"
    assert selected.passages[0].chunk == e.chunks[label]
    assert selected.passages[0].chunk.segments[0].locator.page == 1
    strings = await selector.context_for_generation(ctx, selected)
    assert strings[0] == selected.passages[0].context_text
    trace = selected.trace.model_dump_json()
    assert question not in trace and str(ctx.scope.session_id) not in trace
    assert not any(str(p.chunk.id) in trace or p.chunk.text in trace for p in selected.passages)
    print(f"T22 REAL cross-language {language} supported raw={selected.passages[0].raw_score:.4f}")


async def test_irrelevant_nearest_neighbor_is_insufficient(evidence_corpus):
    ctx, retrieval, selector = await evidence_corpus.query(
        "What is Vietnam's capital?", labels=("fish",)
    )
    assert retrieval.candidates  # nearest neighbor exists, has no answer
    selected = await selector.select(ctx, retrieval)
    assert selected.answerability == "insufficient_evidence"
    assert selected.reason == "no_relevant_evidence" and selected.passages == ()
    assert await selector.context_for_generation(ctx, selected) == ()
    print("T22 REAL irrelevant nearest neighbor -> insufficient / zero context")


@pytest.mark.parametrize(
    "policy", [EvidencePolicy(), EvidencePolicy(passage_limit=1), EvidencePolicy(context_tokens=1)]
)
async def test_actual_conflicting_numbers_fail_closed_before_passage_budget(
    evidence_corpus, policy
):
    e = evidence_corpus
    ctx, retrieval, selector = await e.query(
        "Acme revenue in 2025 in million USD?",
        labels=("revenue", "conflict", "fish"),
        policy=policy,
    )
    selected = await selector.select(ctx, retrieval)
    assert selected.answerability == "insufficient_evidence"
    assert selected.reason == "conflicting_evidence" and selected.trace.conflict_count == 1
    assert selected.trace.relevant_count == 2
    assert selected.trace.context_tokens <= policy.context_tokens
    if policy.passage_limit > 1 and policy.context_tokens > 1:
        assert {p.chunk.id for p in selected.passages} == {
            e.chunks["revenue"].id,
            e.chunks["conflict"].id,
        }
    else:
        assert len(selected.passages) <= 1
    await selector.context_for_generation(ctx, selected)
    print(
        f"T22 REAL conflicting12.5/14.5 million USD ->insufficient/conflicting "
        f"passage_limit={policy.passage_limit} tokens={policy.context_tokens}"
    )


async def test_actual_different_periods_remain_supported(evidence_corpus):
    ctx, retrieval, selector = await evidence_corpus.query(
        "Acme revenue in 2024 and 2025?", labels=("revenue", "other-year")
    )
    selected = await selector.select(ctx, retrieval)
    assert selected.answerability == "supported" and selected.trace.conflict_count == 0
    assert len(selected.passages) == 2


async def test_actual_conflicting_table_values_keep_headers_and_source_maps(evidence_corpus):
    e = evidence_corpus
    (
        e.targets["table-conflict"],
        e.chunks["table-conflict"],
        e.vectors["table-conflict"],
    ) = await seed(e.f, e.models, e.tokenizer, "table-conflict", "en", "14.5")
    ctx, retrieval, selector = await e.query(
        "Acme revenue in 2025 in million USD?", labels=("table", "table-conflict")
    )
    selected = await selector.select(ctx, retrieval)
    assert (
        selected.answerability == "insufficient_evidence"
        and selected.reason == "conflicting_evidence"
    )
    assert selected.trace.conflict_count == 1 and len(selected.passages) == 2
    assert all(
        "Revenue (million USD)" in p.chunk.text and p.chunk.segments for p in selected.passages
    )
    assert all(s.locator.kind == "xlsx" for p in selected.passages for s in p.chunk.segments)
    assert len(await selector.context_for_generation(ctx, selected)) == 2
    print(
        "T22 REAL conflicting XLSX14.5/12.5 ->insufficient/conflicting; both headers/maps retained"
    )


async def test_multiple_sources_and_number_unit_headers_preserved(evidence_corpus):
    e = evidence_corpus
    ctx, retrieval, selector = await e.query(
        "What is Vietnam's capital and Acme's revenue in 2025 in million USD?",
        labels=("capital-en", "revenue", "table", "fish"),
    )
    selected = await selector.select(ctx, retrieval)
    found = {p.chunk.id for p in selected.passages}
    assert {e.chunks[k].id for k in ("capital-en", "revenue", "table")} <= found
    table = next(p for p in selected.passages if p.chunk.id == e.chunks["table"].id)
    assert "Revenue (million USD)" in table.context_text and "12.5" in table.context_text
    assert any(s.role == "context" for s in table.chunk.segments)
    assert all(
        s.locator.kind == "xlsx" and s.locator.unit == "million USD" for s in table.chunk.segments
    )
    assert selected.trace.context_tokens == sum(p.context_tokens for p in selected.passages)
    print(f"T22 REAL multi-evidence={len(selected.passages)} numeric/unit/header/source-map PASS")


async def test_whole_passage_exact_token_budget_and_zero_match(evidence_corpus):
    e = evidence_corpus
    count = e.tokenizer.count("[e1]\n" + e.chunks["revenue"].text)
    for budget, expected in ((count, "supported"), (count - 1, "insufficient_evidence")):
        ctx, retrieval, selector = await e.query(
            "Acme revenue in 2025?",
            labels=("revenue",),
            policy=EvidencePolicy(context_tokens=budget),
        )
        selected = await selector.select(ctx, retrieval)
        assert selected.answerability == expected
        assert selected.trace.context_tokens <= budget
        if budget < count:
            assert selected.reason == "context_budget_exhausted" and not selected.passages
    ctx, retrieval, selector = await e.query(
        "Acme revenue?", labels=("revenue",), languages=("vi",)
    )
    selected = await selector.select(ctx, retrieval)
    assert not selected.passages and selected.reason == "no_relevant_evidence"


async def test_actual_rerank_cancellation_cleanup_and_recovery(evidence_corpus):
    e = evidence_corpus
    ctx, retrieval, selector = await e.query("What is Vietnam's capital?", labels=("capital-en",))
    # Cancel while actual HTTP inference is entered; no fake score/output.
    entered = asyncio.Event()

    class Observed:
        async def infer(self, request):
            entered.set()
            return await e.models.infer(request)

    selector._models = Observed()
    task = asyncio.create_task(selector.select(ctx, retrieval))
    await asyncio.wait_for(entered.wait(), 10)
    await asyncio.sleep(0.03)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert (await selector.select(ctx, retrieval)).answerability == "supported"
    print("T22 REAL HTTP rerank cancelled; subsequent real rerank supported")


async def test_actual_rerank_pair_over_limit_is_technical(evidence_corpus):
    e = evidence_corpus
    ctx, retrieval, selector = await e.query("Vietnam capital?", labels=("capital-en",))
    ctx = replace(ctx, question="hello " * 800)
    with pytest.raises(InferenceError, match="model_token_limit"):
        await selector.select(ctx, retrieval)


async def test_deadline_covers_hydration(evidence_corpus):
    e = evidence_corpus
    ctx, retrieval, selector = await e.query(
        "Vietnam capital?", labels=("capital-en",), policy=EvidencePolicy(timeout_seconds=0.00001)
    )
    with pytest.raises(EvidenceError, match="evidence_timeout"):
        await selector.select(ctx, retrieval)


async def test_actual_twenty_candidates_eight_passages_and_reproducible_threshold(evidence_corpus):
    e = evidence_corpus
    targets = []
    for i in range(20):
        target, _, _ = await seed(
            e.f, e.models, e.tokenizer, f"limit-{i}", "en", "Hanoi is the capital of Vietnam."
        )
        targets.append(target.pair.document_id)
    from rag_core.application.retrieval import RetrievalPipeline
    from tests.integration.test_retrieval import context

    ctx = await context(e.f, "What is Vietnam's capital?", document_ids=tuple(targets))
    retrieval = await RetrievalPipeline(e.models, e.models.expected_fingerprint).retrieve(ctx)
    _, _, selector = await e.query("What is Vietnam's capital?")
    selected = await selector.select(ctx, retrieval)
    assert selected.trace.candidate_count == selected.trace.relevant_count == 20
    assert len(selected.passages) == 8
    assert len({p.chunk.id for p in selected.passages}) == 8
    assert all(p.raw_score >= selected.trace.policy.raw_score_floor for p in selected.passages)
    again = await selector.select(ctx, retrieval)
    assert again.passages == selected.passages
    assert again.trace.policy_fingerprint == selected.trace.policy_fingerprint
    assert selected.trace.policy.calibration == "pending-T31"
    print(
        "T22 REAL20 rerank candidates ->8 passages; stable config/raw ranking, calibration pending"
    )
