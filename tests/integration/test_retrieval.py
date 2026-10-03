"""T21: real CPU BGE-M3 HTTP, PostgreSQL and Qdrant; synthetic documents, no QA/gold input."""

import os
from dataclasses import replace
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio

from rag_core.adapters.models.http import HttpModelInference
from rag_core.adapters.persistence.database import build_engine
from rag_core.adapters.persistence.sessions import PostgresSessionRepository
from rag_core.adapters.persistence.vector_generations import PostgresGenerationAuthority
from rag_core.adapters.vectors.qdrant import QdrantVectorRepository
from rag_core.application.query import ScopedRetrievalContext, ScopedVectors
from rag_core.application.retrieval import RetrievalPipeline
from rag_core.auth import Principal
from rag_core.contracts.v1 import PdfLocator
from rag_core.domain.metadata import ScopeError, ScopeSnapshot
from rag_core.domain.models import InferenceError, InferenceRequest
from rag_core.domain.query import DomainConfig, DomainDefinition, FrozenHistoryMetadata
from rag_core.domain.retrieval import RetrievalPolicy
from rag_core.domain.vectors import IndexProfile, VectorChunk, VectorWrite
from tests.integration.test_qdrant_scope import Fixture, ObservedClient

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]

# Index every synthetic source, including distractors. Expected labels below are
# assertions only: none supplies an ID/filter/text to RetrievalPipeline.
SOURCES = (
    ("capital-en", "en", "Hanoi is the capital of Vietnam. The Red River flows through Hanoi."),
    ("capital-vi", "vi", "Hà Nội là thủ đô của Việt Nam. Sông Hồng chảy qua Hà Nội."),
    ("finance-en", "en", "Acme's 2025 revenue was 12.5 million USD. The report code is ZXQ-7419."),
    ("finance-vi", "vi", "Doanh thu năm 2025 của Acme là 12,5 triệu USD. Mã báo cáo là ZXQ-7419."),
    ("fish-en", "en", "Ocean fish live in salt water. Marine biology studies whales and dolphins."),
    ("garden-vi", "vi", "Hoa hồng cần ánh sáng và nước. Người làm vườn trồng cây vào mùa xuân."),
)


@pytest_asyncio.fixture
async def real_models():
    url = os.environ.get("RAG_TEST_INFERENCE_URL")
    if url != "http://127.0.0.1:58080":
        pytest.fail(
            "RAG_TEST_INFERENCE_URL=http://127.0.0.1:58080 required; no fake model fallback"
        )
    async with httpx.AsyncClient(base_url=url, trust_env=False, timeout=10) as client:
        response = await client.get("/health/ready")
        response.raise_for_status()
        health = response.json()
        assert health["device"] == "cpu" and health["model_instances"] == 2
        assert health["inference_processes"] == 1
        print(
            f"T21 REAL MODEL device=cpu pid={health['pid']} fingerprint={health['fingerprint']} "
            f"runtime={health['runtime']} load={health['load_seconds']:.3f}s"
        )
        yield HttpModelInference(client, health["fingerprint"])


@pytest_asyncio.fixture
async def corpus(pg_url, real_models):
    assert os.environ.get("RAG_TEST_QDRANT_URL") == "http://127.0.0.1:56333"
    engine = build_engine(pg_url)
    client = ObservedClient(os.environ["RAG_TEST_QDRANT_URL"])
    sessions = PostgresSessionRepository(engine)
    owner = Principal("t21-" + uuid4().hex, "user-1")
    session = await sessions.create_session(owner, "current")
    profile = IndexProfile(real_models.expected_fingerprint)
    repo = QdrantVectorRepository(client, profile, sessions, PostgresGenerationAuthority(engine))
    f = Fixture(engine, sessions, client, profile, repo, owner, session)
    labels = {}
    targets = []
    try:
        await repo.ensure_collection()
        texts = [text for _, _, text in SOURCES]
        embedded = await real_models.infer(
            InferenceRequest(operation="embed", priority="index", texts=texts)
        )
        appendix = await real_models.infer(
            InferenceRequest(
                operation="embed",
                priority="index",
                texts=[
                    "Appendix: roses need sunlight and water.",
                    "Phụ lục: hoa hồng cần ánh sáng và nước.",
                ],
            )
        )
        for (label, language, _), embedding in zip(SOURCES, embedded.embeddings, strict=True):
            target = await f.version()
            targets.append(target)
            points = tuple(
                VectorWrite(
                    VectorChunk(
                        document_id=target.pair.document_id,
                        document_version_id=target.pair.version_id,
                        index_generation=target.pair.generation_id,
                        chunk_id=uuid4(),
                        language=language,
                        ordinal=i,
                        unit_id="page-1" if i < 2 else "page-2",
                        locator=PdfLocator(kind="pdf", page=1 if i < 2 else 2),
                    ),
                    embedding if i < 2 else appendix.embeddings[0 if language == "en" else 1],
                )
                for i in range(4)
            )
            await repo.upsert(target, points, profile.model_fingerprint)
            await f.publish(target)
            await f.attach(target)
            labels.update({p.chunk.chunk_id: label for p in points})
        # Strong exact-answer retained vectors in SAME OWNER other session, plus
        # another user/app; every branch must exclude them before top-k.
        for foreign in (
            owner,
            Principal(owner.app_id, "user-2"),
            Principal("other-" + uuid4().hex, "user-1"),
        ):
            target = await f.version(foreign)
            point = VectorWrite(
                VectorChunk(
                    document_id=target.pair.document_id,
                    document_version_id=target.pair.version_id,
                    index_generation=target.pair.generation_id,
                    chunk_id=uuid4(),
                    language="en",
                    ordinal=0,
                    unit_id="page-1",
                    locator=PdfLocator(kind="pdf", page=1),
                ),
                embedded.embeddings[0],
            )
            await repo.upsert(target, (point,), profile.model_fingerprint)
            await f.publish(target)
            old = await sessions.create_session(foreign, "retained-" + uuid4().hex)
            await f.attach(target, old)
        client.calls.clear()
        yield f, real_models, labels, targets
    finally:
        # Own isolated tmpfs server; tests run serially, collection is the real
        # CPU fingerprint and never an application endpoint/collection.
        await client.delete_collection(profile.collection_name)
        await client.close()
        await engine.dispose()


async def context(
    f, question, *, languages=None, policy="hybrid-v1", session=None, document_ids=None
):
    scope = await f.sessions.resolve_scope(f.owner, (session or f.session).session_id, document_ids)
    return ScopedRetrievalContext(
        scope,
        DomainDefinition(
            id="multilingual",
            subset_policy="optional",
            config=DomainConfig(retrieval_policy=policy),
        ),
        question,
        "en",
        languages,
        FrozenHistoryMetadata(
            received_messages=0,
            retained_messages=0,
            received_tokens=0,
            retained_tokens=0,
            truncated=False,
        ),
        ScopedVectors(f.repo, f.sessions, scope, languages),
    )


@pytest.mark.parametrize("branch", ["dense", "hybrid"])
@pytest.mark.parametrize(
    "question,language,expected",
    [
        ("What is the capital of Vietnam?", "vi", "capital-vi"),
        ("Thủ đô của Việt Nam là gì?", "en", "capital-en"),
        ("ZXQ-7419 revenue 2025 12.5 million USD", "en", "finance-en"),
        ("Mã ZXQ-7419 doanh thu năm 2025 là bao nhiêu?", "vi", "finance-vi"),
    ],
)
async def test_real_relevance_cross_language_keyword_numeric_and_branch_filters(
    corpus, branch, question, language, expected
):
    f, models, labels, _ = corpus
    ctx = await context(f, question, languages=(language,), policy=branch + "-v1")
    result = await RetrievalPipeline(models, models.expected_fingerprint).retrieve(ctx)
    assert result.candidates and labels[result.candidates[0].chunk.chunk_id] == expected
    assert all(
        h.chunk.pair in ctx.scope.pairs and h.chunk.language == language for h in result.candidates
    )
    queries = [kw for name, kw in f.client.calls if name == "query"]
    assert len(queries) == 1
    filters = [queries[0]["query_filter"]]
    if branch == "hybrid":
        assert len(queries[0]["prefetch"]) == 2
        assert {p.using for p in queries[0]["prefetch"]} == {"dense", "sparse"}
        assert all(p.limit == 30 for p in queries[0]["prefetch"])
        filters += [p.filter for p in queries[0]["prefetch"]]
    for filter_ in filters:
        payload = filter_.model_dump_json()
        assert '"language"' in payload and language in payload
        assert str(f.session.session_id) not in payload  # PG pairs grant session access.
        assert f.owner.app_id in payload and f.owner.user_id in payload
        assert all(str(p.generation_id) in payload for p in ctx.scope.pairs)
    assert result.trace.score_kind == ("cosine" if branch == "dense" else "rrf")
    trace = result.trace.model_dump_json()
    assert question not in trace and f.owner.app_id not in trace
    assert not any(str(h.chunk.chunk_id) in trace for h in result.candidates)
    print(f"T21 REAL {branch} corpus={language} top1={expected} scope/filter/trace PASS")


async def test_real_multi_document_and_bounded_neighbors(corpus):
    f, models, labels, _ = corpus
    policy = RetrievalPolicy(top_k=4, candidate_budget=8, neighbor_anchors=2, neighbor_radius=3)
    ctx = await context(f, "What is Vietnam's capital and Acme's 2025 revenue?", languages=("en",))
    result = await RetrievalPipeline(
        models, models.expected_fingerprint, {"hybrid-v1": policy}
    ).retrieve(ctx)
    found = {labels[h.chunk.chunk_id] for h in result.candidates[:4]}
    assert {"capital-en", "finance-en"} <= found
    assert len(result.candidates) <= 8 and len(
        {h.chunk.chunk_id for h in result.candidates}
    ) == len(result.candidates)
    assert result.trace.neighbor_calls <= 2
    for hit in result.candidates[4:]:
        assert hit.score is None
        assert any(
            hit.chunk.pair == seed.chunk.pair and hit.chunk.unit_id == seed.chunk.unit_id
            for seed in result.candidates[:2]
        )
    print(
        f"T21 REAL multi-doc labels={sorted(found)} candidates={len(result.candidates)} neighbor_calls={result.trace.neighbor_calls}"
    )


async def test_real_empty_language_no_match_and_empty_scope(corpus):
    f, models, _, targets = corpus
    # User-selected EN source with an explicit VI corpus filter: valid request
    # combination with no matching points, not an evidence-ID/gold optimization.
    ctx = await context(
        f, "Unknown material", languages=("vi",), document_ids=(targets[0].pair.document_id,)
    )
    result = await RetrievalPipeline(models, models.expected_fingerprint).retrieve(ctx)
    assert result.candidates == () and result.trace.candidate_count == 0
    f.client.calls.clear()
    empty = await f.sessions.create_session(f.owner, "empty")
    # Public T10 semantics are no_session_documents. A hand-constructed empty
    # context cannot bypass authoritative validation, even without vector I/O.
    with pytest.raises(ScopeError, match="no_session_documents"):
        await f.sessions.resolve_scope(f.owner, empty.session_id)
    scope = ScopeSnapshot(f.owner, empty.session_id, empty.scope_revision, None, ())
    ctx = replace(ctx, scope=scope, vectors=ScopedVectors(f.repo, f.sessions, scope, None))

    class NoModelCalls:
        async def infer(self, request):
            pytest.fail("Empty PG scope must fail before model inference")

    with pytest.raises(ScopeError, match="session_scope_changed"):
        await RetrievalPipeline(NoModelCalls(), models.expected_fingerprint).retrieve(ctx)
    assert not f.client.calls
    print(
        "T21 REAL no-match language -> zero candidates; empty session rejected before model/vector"
    )


@pytest.mark.parametrize(
    "language,question", [("en", "Vietnam capital?"), ("vi", "Thủ đô Việt Nam?")]
)
async def test_real_neighbor_expansion_same_page_scope_language_and_detach(
    corpus, language, question
):
    f, models, _, targets = corpus
    policy = RetrievalPolicy(top_k=1, candidate_budget=2, neighbor_anchors=1, neighbor_radius=3)
    ctx = await context(f, question, languages=(language,))
    pipeline = RetrievalPipeline(models, models.expected_fingerprint, {"hybrid-v1": policy})
    result = await pipeline.retrieve(ctx)
    assert len(result.candidates) == 2
    seed, neighbor = result.candidates
    assert (
        seed.chunk.pair == neighbor.chunk.pair
        and seed.chunk.unit_id == neighbor.chunk.unit_id == "page-1"
    )
    assert seed.chunk.language == neighbor.chunk.language == language
    assert (
        neighbor.score is None and result.trace.neighbor_count == result.trace.neighbor_calls == 1
    )
    scrolls = [kw["scroll_filter"] for name, kw in f.client.calls if name == "scroll"]
    assert len(scrolls) == 2
    assert all(
        '"language"' in v.model_dump_json() and language in v.model_dump_json() for v in scrolls
    )

    async def detach():
        await f.sessions.detach_document(f.owner, f.session.session_id, targets[0].pair.document_id)

    f.client.after_scroll = detach
    with pytest.raises(ScopeError, match="session_scope_changed"):
        await pipeline.retrieve(ctx)
    print(
        f"T21 REAL neighbor corpus={language} adds1 same-page/pair/filter; detach on scroll aborts"
    )


async def test_real_sparse_no_lexical_match(corpus):
    f, models, _, _ = corpus
    ctx = await context(f, "𓀀", policy="lexical")
    result = await RetrievalPipeline(
        models, models.expected_fingerprint, {"lexical": RetrievalPolicy(branch="sparse")}
    ).retrieve(ctx)
    assert result.candidates == ()
    print("T21 REAL sparse absent lexical tokens -> zero candidates")


async def test_real_detach_during_embedding_and_after_search(corpus):
    f, models, _, targets = corpus
    ctx = await context(f, "What is Vietnam's capital?")

    class DetachingModel:
        async def infer(self, request):
            result = await models.infer(request)
            await f.sessions.detach_document(
                f.owner, f.session.session_id, targets[0].pair.document_id
            )
            return result

    with pytest.raises(ScopeError, match="session_scope_changed"):
        await RetrievalPipeline(DetachingModel(), models.expected_fingerprint).retrieve(ctx)
    assert not f.client.calls
    ctx = await context(f, "Acme revenue?")

    async def detach():
        await f.sessions.detach_document(f.owner, f.session.session_id, targets[1].pair.document_id)

    f.client.after_query = detach
    with pytest.raises(ScopeError, match="session_scope_changed"):
        await RetrievalPipeline(models, models.expected_fingerprint).retrieve(ctx)
    print("T21 REAL detach after model / Qdrant -> abort, no stale candidates")


async def test_real_model_over_token_budget_is_technical_failure(corpus):
    f, models, _, _ = corpus
    ctx = await context(f, "hello " * 600)
    with pytest.raises(InferenceError, match="model_token_limit"):
        await RetrievalPipeline(models, models.expected_fingerprint).retrieve(ctx)
    assert not f.client.calls


async def test_real_dense_hybrid_toggle_reproducible_and_max_budget(corpus):
    f, models, labels, _ = corpus
    # Caller-supplied trusted config survives JSON round-trip; request has no tunables.
    policies = {
        branch + "-v1": RetrievalPolicy.model_validate_json(
            RetrievalPolicy(
                branch=branch,
                prefetch_limit=100,
                top_k=20,
                candidate_budget=20,
                neighbor_anchors=20,
            ).model_dump_json()
        )
        for branch in ("dense", "hybrid")
    }
    pipeline = RetrievalPipeline(models, models.expected_fingerprint, policies)
    for branch in ("dense", "hybrid"):
        ctx = await context(f, "Vietnam capital?", policy=branch + "-v1")
        first = await pipeline.retrieve(ctx)
        second = await pipeline.retrieve(ctx)
        assert first.candidates == second.candidates
        assert (
            first.trace.policy_fingerprint
            == second.trace.policy_fingerprint
            == policies[branch + "-v1"].fingerprint
        )
        assert len(first.candidates) == 20 and {
            labels[h.chunk.chunk_id] for h in first.candidates
        } <= {s[0] for s in SOURCES}
        assert first.trace.neighbor_calls == 0  # Full budget leaves no room for expansion.
    minimum = RetrievalPipeline(
        models,
        models.expected_fingerprint,
        {
            "minimum": RetrievalPolicy(
                prefetch_limit=1, top_k=1, candidate_budget=1, neighbor_anchors=1, neighbor_radius=0
            ),
        },
    )
    result = await minimum.retrieve(await context(f, "Vietnam capital?", policy="minimum"))
    assert len(result.candidates) == 1 and result.trace.neighbor_calls == 0
    print("T21 REAL reproducible dense/hybrid, prefetch100/candidate20/anchors20 boundaries PASS")
