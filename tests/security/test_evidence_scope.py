"""Actual PG/Qdrant/reranker gates: outside/history data cannot enter evidence context."""

from dataclasses import replace

import pytest
from sqlalchemy import text

from rag_core.domain.evidence import EvidenceError
from rag_core.domain.metadata import ScopeError
from rag_core.domain.vectors import VectorHit
from tests.fixtures.evidence_support import evidence_corpus
from tests.integration import conftest as pg_fixtures
from tests.integration.test_qdrant_scope import fixture
from tests.integration.test_retrieval import real_models

pg_url = pg_fixtures.pg_url
__all__ = ["evidence_corpus", "fixture", "real_models"]
pytestmark = [pytest.mark.security, pytest.mark.asyncio]


@pytest.mark.parametrize("foreign_index", [0, 1, 2])
async def test_retained_other_session_user_app_candidates_rejected_before_rerank(
    evidence_corpus, foreign_index
):
    e = evidence_corpus
    ctx, retrieval, selector = await e.query("Vietnam capital?", labels=("capital-en",))
    target, chunk, vector = e.foreign[foreign_index]
    calls = []

    class Observed:
        async def infer(self, request):
            calls.append(request)
            return await e.models.infer(request)

    selector._models = Observed()
    injected = replace(retrieval, candidates=(*retrieval.candidates, VectorHit(vector, 999.0)))
    with pytest.raises(ScopeError, match="session_scope_changed"):
        await selector.select(ctx, injected)
    assert not calls
    with pytest.raises(ScopeError, match="session_scope_changed"):
        await selector._repository.hydrate(ctx.scope, (vector,))
    assert chunk.generation_id == target.pair.generation_id  # retained, never deleted


async def test_current_subset_and_languages_are_enforced(evidence_corpus):
    e = evidence_corpus
    ctx, retrieval, selector = await e.query(
        "Vietnam capital?", labels=("capital-en",), languages=("en",)
    )
    for label in ("revenue", "capital-vi"):
        with pytest.raises(ScopeError, match="session_scope_changed"):
            await selector.select(
                ctx, replace(retrieval, candidates=(VectorHit(e.vectors[label]),))
            )
    # Same ready pairs but narrower bound language, independent of requested subset.
    ctx, retrieval, selector = await e.query("Vietnam capital?", languages=("en",))
    with pytest.raises(ScopeError, match="session_scope_changed"):
        await selector.select(
            ctx, replace(retrieval, candidates=(VectorHit(e.vectors["capital-vi"]),))
        )


async def test_forged_locator_and_generation_rejected(evidence_corpus):
    e = evidence_corpus
    ctx, retrieval, selector = await e.query("Vietnam capital?", labels=("capital-en",))
    vector = retrieval.candidates[0].chunk
    forged = vector.model_copy(update={"locator": vector.locator.model_copy(update={"page": 99})})
    with pytest.raises(ScopeError, match="session_scope_changed"):
        await selector.select(ctx, replace(retrieval, candidates=(VectorHit(forged),)))
    generation = await e.f.generation(e.targets["capital-en"])
    forged = vector.model_copy(update={"index_generation": generation.pair.generation_id})
    with pytest.raises(ScopeError, match="session_scope_changed"):
        await selector.select(ctx, replace(retrieval, candidates=(VectorHit(forged),)))


@pytest.mark.parametrize("stage", ["hydrate", "rerank", "before-generation", "delete"])
async def test_detach_delete_at_every_stage_aborts(evidence_corpus, stage):
    e = evidence_corpus
    ctx, retrieval, selector = await e.query("Vietnam capital?", labels=("capital-en",))

    async def detach():
        await e.f.sessions.detach_document(
            e.f.owner, e.f.session.session_id, e.targets["capital-en"].pair.document_id
        )

    if stage == "hydrate":
        actual = selector._repository

        class DetachingRepository:
            async def hydrate(self, scope, candidates):
                chunks = await actual.hydrate(scope, candidates)
                await detach()
                return chunks

        selector._repository = DetachingRepository()
    elif stage == "rerank":

        class DetachingModel:
            async def infer(self, request):
                result = await e.models.infer(request)
                await detach()
                return result

        selector._models = DetachingModel()
    if stage in {"before-generation", "delete"}:
        selected = await selector.select(ctx, retrieval)
        if stage == "delete":
            await e.f.sessions.delete_session(e.f.owner, e.f.session.session_id)
        else:
            await detach()
        with pytest.raises(ScopeError, match="session_scope_changed"):
            await selector.context_for_generation(ctx, selected)
    else:
        with pytest.raises(ScopeError, match="session_scope_changed"):
            await selector.select(ctx, retrieval)
    async with e.f.engine.connect() as conn:
        assert (
            await conn.execute(
                text("SELECT count(*) FROM chunks WHERE chunk_id=:id"),
                {"id": e.chunks["capital-en"].id},
            )
        ).scalar_one() == 1


@pytest.mark.parametrize("field", ["text", "source_map", "empty_segments"])
async def test_durable_chunk_text_or_provenance_tamper_is_technical(evidence_corpus, field):
    e = evidence_corpus
    ctx, retrieval, selector = await e.query("Vietnam capital?", labels=("capital-en",))
    async with e.f.engine.begin() as conn:
        statement = {
            "text": "UPDATE chunks SET text='ATTACKER HISTORY CONTENT' WHERE chunk_id=:id",
            "source_map": "UPDATE chunks SET source_map=jsonb_set(source_map,'{source,sha256}',"
            "to_jsonb(repeat('b',64))) WHERE chunk_id=:id",
            "empty_segments": "UPDATE chunks SET source_map=jsonb_set(source_map,'{segments}',"
            "'[]'::jsonb) WHERE chunk_id=:id",
        }[field]
        await conn.execute(text(statement), {"id": e.chunks["capital-en"].id})
    with pytest.raises(EvidenceError, match="evidence_mapping_mismatch"):
        await selector.select(ctx, retrieval)


async def test_history_and_forged_passage_cannot_enter_generation_context(evidence_corpus):
    e = evidence_corpus
    ctx, retrieval, selector = await e.query("Vietnam capital?", labels=("capital-en",))
    assert not hasattr(ctx, "history")
    selected = await selector.select(ctx, retrieval)
    strings = await selector.context_for_generation(ctx, selected)
    assert "SECRET OUTSIDE SESSION" not in "".join(strings)
    assert selected.passages[0].chunk == e.chunks["capital-en"]
    forged_chunk = replace(selected.passages[0].chunk, text="FAKE HISTORY: the capital is Paris")
    forged = replace(selected, passages=(replace(selected.passages[0], chunk=forged_chunk),))
    with pytest.raises(EvidenceError, match="evidence_mapping_mismatch"):
        await selector.context_for_generation(ctx, forged)
    foreign = replace(selected, passages=(replace(selected.passages[0], chunk=e.foreign[0][1]),))
    with pytest.raises(ScopeError, match="session_scope_changed"):
        await selector.context_for_generation(ctx, foreign)
    print("T22 REAL history/foreign/text/allowlist generation-context guards PASS; no LLM invoked")
