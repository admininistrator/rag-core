"""T18 gates: actual Qdrant/PG; synthetic vectors test filtering, not model quality."""

import asyncio
import hashlib
import os
from collections.abc import AsyncIterator
from dataclasses import dataclass, replace
from typing import Any
from uuid import uuid4

import pytest
import pytest_asyncio
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qm
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine

from rag_core.adapters.persistence.database import build_engine
from rag_core.adapters.persistence.sessions import PostgresSessionRepository
from rag_core.adapters.persistence.vector_generations import PostgresGenerationAuthority
from rag_core.adapters.vectors.qdrant import PAYLOAD_INDEXES, QdrantVectorRepository
from rag_core.auth import Principal
from rag_core.contracts.v1 import PdfLocator
from rag_core.domain.metadata import ScopeError, Session, VersionGeneration
from rag_core.domain.models import Embedding
from rag_core.domain.vectors import (
    GenerationScope,
    IndexProfile,
    VectorChunk,
    VectorError,
    VectorWrite,
    point_id,
)

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


def embedding(*, strong: bool = False, sparse: float = 1) -> Embedding:
    return Embedding(
        dense=(1.0, 0.0) + (0.0,) * 1022 if strong else (0.8, 0.6) + (0.0,) * 1022,
        sparse_indices=(42,),
        sparse_values=(sparse,),
    )


class ObservedClient(AsyncQdrantClient):
    """Observe real requests; no mocked server/response or unscoped fallback."""

    def __init__(self, url: str) -> None:
        super().__init__(url=url, timeout=5, trust_env=False)
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.after_query = None
        self.after_scroll = None
        self.write_entered = None
        self.write_release = None

    async def query_points(self, *args: Any, **kwargs: Any) -> qm.QueryResponse:
        self.calls.append(("query", kwargs))
        response = await super().query_points(*args, **kwargs)
        if self.after_query is not None:
            await self.after_query()
        return response

    async def scroll(self, *args: Any, **kwargs: Any) -> Any:
        self.calls.append(("scroll", kwargs))
        response = await super().scroll(*args, **kwargs)
        if self.after_scroll is not None:
            await self.after_scroll()
        return response

    async def upsert(self, *args: Any, **kwargs: Any) -> Any:
        if self.write_entered is not None:
            self.write_entered.set()
            await self.write_release.wait()
        return await super().upsert(*args, **kwargs)


@dataclass
class Fixture:
    engine: AsyncEngine
    sessions: PostgresSessionRepository
    client: ObservedClient
    profile: IndexProfile
    repo: QdrantVectorRepository
    owner: Principal
    session: Session

    async def version(self, owner: Principal | None = None) -> GenerationScope:
        principal = owner or self.owner
        pair = VersionGeneration(uuid4(), uuid4(), uuid4())
        params = dict(
            app=principal.app_id,
            owner=principal.user_id,
            doc=pair.document_id,
            version=pair.version_id,
            generation=pair.generation_id,
            fingerprint=self.profile.fingerprint,
        )
        async with self.engine.begin() as conn:
            await conn.execute(
                text("""
                INSERT INTO documents (document_id,app_id,owner_id,filename,storage_alias,bucket,object_key)
                VALUES (:doc,:app,:owner,'fixture.pdf','fixture','test-bucket','retained-source')
            """),
                params,
            )
            await conn.execute(
                text("""
                INSERT INTO document_versions (version_id,app_id,owner_id,document_id,source_sha256,
                    content_type,size_bytes,index_fingerprint)
                VALUES (:version,:app,:owner,:doc,repeat('a',64),'application/pdf',10,:fingerprint)
            """),
                params,
            )
            await conn.execute(
                text("""
                INSERT INTO index_generations (generation_id,app_id,owner_id,version_id,index_fingerprint)
                VALUES (:generation,:app,:owner,:version,:fingerprint)
            """),
                params,
            )
        return GenerationScope(principal, pair)

    async def generation(self, target: GenerationScope) -> GenerationScope:
        pair = replace(target.pair, generation_id=uuid4())
        async with self.engine.begin() as conn:
            await conn.execute(
                text("""
                INSERT INTO index_generations (generation_id,app_id,owner_id,version_id,index_fingerprint)
                VALUES (:gen,:app,:owner,:version,:fingerprint)
            """),
                dict(
                    gen=pair.generation_id,
                    app=target.principal.app_id,
                    owner=target.principal.user_id,
                    version=pair.version_id,
                    fingerprint=self.profile.fingerprint,
                ),
            )
        return GenerationScope(target.principal, pair)

    def points(self, target: GenerationScope, *, strong: bool = False) -> tuple[VectorWrite, ...]:
        return tuple(
            VectorWrite(
                VectorChunk(
                    document_id=target.pair.document_id,
                    document_version_id=target.pair.version_id,
                    index_generation=target.pair.generation_id,
                    chunk_id=uuid4(),
                    language="vi" if i == 1 else "en",
                    ordinal=i,
                    unit_id="pdf-page-1" if i < 3 else "pdf-page-2",
                    locator=PdfLocator(kind="pdf", page=1 if i < 3 else 2),
                ),
                embedding(strong=strong, sparse=100 if strong else 1),
            )
            for i in range(4)
        )

    async def seed(
        self, target: GenerationScope, *, strong: bool = False
    ) -> tuple[VectorWrite, ...]:
        points = self.points(target, strong=strong)
        await self.repo.upsert(target, points, self.profile.model_fingerprint)
        return points

    async def publish(self, target: GenerationScope) -> None:
        async with self.engine.begin() as conn:
            # Publication uses normal UPDATE row locks, serialized with Qdrant write/cleanup.
            await conn.execute(
                text("""
                UPDATE document_versions SET state='ready', active_generation_id=:gen
                WHERE version_id=:version
            """),
                dict(gen=target.pair.generation_id, version=target.pair.version_id),
            )
            await conn.execute(
                text("UPDATE index_generations SET state='ready' WHERE generation_id=:gen"),
                dict(gen=target.pair.generation_id),
            )

    async def attach(self, target: GenerationScope, session: Session | None = None) -> None:
        async with self.engine.begin() as conn:
            await self.sessions.attach_version(
                conn,
                target.principal,
                (session or self.session).session_id,
                target.pair.version_id,
                uuid4(),
            )

    async def snapshot(self):
        return await self.sessions.resolve_scope(self.owner, self.session.session_id)


@pytest_asyncio.fixture
async def fixture(pg_url: URL) -> AsyncIterator[Fixture]:
    url = os.environ.get("RAG_TEST_QDRANT_URL")
    if url != "http://127.0.0.1:56333":
        pytest.fail(
            "RAG_TEST_QDRANT_URL=http://127.0.0.1:56333 required; real isolated Qdrant only"
        )
    engine = build_engine(pg_url)
    client = ObservedClient(url)
    sessions = PostgresSessionRepository(engine)
    profile = IndexProfile(hashlib.sha256(uuid4().bytes).hexdigest())
    owner = Principal("app-" + uuid4().hex, "user-1")
    session = await sessions.create_session(owner, "session-1")
    repo = QdrantVectorRepository(client, profile, sessions, PostgresGenerationAuthority(engine))
    f = Fixture(engine, sessions, client, profile, repo, owner, session)
    try:
        await repo.ensure_collection()
        yield f
    finally:
        # Only the random collection derived from this fixture's random model fingerprint.
        await client.delete_collection(profile.collection_name)
        await client.close()
        await engine.dispose()


@pytest.mark.parametrize("branch", ["dense", "sparse", "hybrid"])
async def test_isolation_every_branch_and_exact_pairs(fixture: Fixture, branch: str) -> None:
    f = fixture
    current = await f.version()
    active_points = await f.seed(current)
    await f.publish(current)
    await f.attach(current)
    second_allowed = await f.version()
    await f.seed(second_allowed)
    await f.publish(second_allowed)
    await f.attach(second_allowed)
    other_session = await f.sessions.create_session(f.owner, "session-2")
    retained = await f.version()
    other_points = await f.seed(retained, strong=True)
    await f.publish(retained)
    await f.attach(retained, other_session)
    strangers = [
        Principal(f.owner.app_id, "user-2"),
        Principal("other-app", "user-1"),
        Principal("other-app", "user-2"),
    ]
    for stranger in strangers:
        session = await f.sessions.create_session(stranger, "session-1")
        target = await f.version(stranger)
        await f.seed(target, strong=True)
        await f.publish(target)
        await f.attach(target, session)
    stale = await f.generation(current)
    await f.seed(stale, strong=True)
    # Adversarial wrong pair would pass independent version/generation MatchAny lists.
    crossed = active_points[0].chunk.model_copy(
        update={"index_generation": second_allowed.pair.generation_id, "chunk_id": uuid4()}
    )
    await f.client.upsert(
        f.profile.collection_name,
        [
            qm.PointStruct(
                id=str(point_id(f.owner, crossed)),
                vector={
                    "dense": list(embedding(strong=True).dense),
                    "sparse": qm.SparseVector(indices=[42], values=[1000]),
                },
                payload={
                    **crossed.model_dump(mode="json"),
                    "app_id": f.owner.app_id,
                    "owner_id": f.owner.user_id,
                },
            )
        ],
        wait=True,
    )
    snapshot = await f.snapshot()
    hits = await f.repo.search(
        snapshot, embedding(strong=True), f.profile.model_fingerprint, branch=branch, limit=1
    )
    assert len(hits) == 1 and hits[0].chunk.pair in snapshot.pairs
    # Payload inspection alone would not prove filters happened before top-1 selection.
    query_call = [kw for kind, kw in f.client.calls if kind == "query"][-1]
    assert query_call["query_filter"] is not None
    if branch == "hybrid":
        assert len(query_call["prefetch"]) == 2
        assert all(p.filter == query_call["query_filter"] for p in query_call["prefetch"])
    full = await f.repo.search(
        snapshot, embedding(strong=True), f.profile.model_fingerprint, branch=branch, limit=100
    )
    assert len(full) == 8 and {hit.chunk.pair for hit in full} == set(snapshot.pairs)
    selected = await f.sessions.resolve_scope(
        f.owner, f.session.session_id, (current.pair.document_id,)
    )
    assert (
        len(await f.repo.search(selected, embedding(), f.profile.model_fingerprint, branch=branch))
        == 4
    )
    second = await f.sessions.resolve_scope(f.owner, other_session.session_id)
    assert {
        h.chunk.chunk_id
        for h in await f.repo.search(
            second, embedding(), f.profile.model_fingerprint, branch=branch
        )
    } == {p.chunk.chunk_id for p in other_points}
    for stranger in strangers:
        with pytest.raises(ScopeError, match="not_found"):
            await f.sessions.resolve_scope(stranger, f.session.session_id)
    print(
        f"PASS {branch}: 2apps/2users/same-owner 2sessions, stale/crossed pairs, prefiltered top1/subset"
    )


async def test_fetch_neighbors_and_languages(fixture: Fixture) -> None:
    f = fixture
    target = await f.version()
    points = await f.seed(target)
    await f.publish(target)
    await f.attach(target)
    outsider = await f.version()
    other_points = await f.seed(outsider)
    await f.publish(outsider)
    snapshot = await f.snapshot()
    neighbors = await f.repo.fetch_neighbors(snapshot, points[1].chunk.chunk_id, radius=3)
    assert [h.chunk.ordinal for h in neighbors] == [0, 1, 2]  # Never cross page-2 hard boundary.
    assert all(h.chunk.locator.page == 1 for h in neighbors)
    assert await f.repo.fetch_neighbors(snapshot, other_points[0].chunk.chunk_id) == ()
    assert await f.repo.fetch(snapshot, (other_points[0].chunk.chunk_id,)) == ()
    assert await f.repo.fetch_neighbors(snapshot, points[1].chunk.chunk_id, languages=("en",)) == ()
    hits = await f.repo.search(
        snapshot, embedding(), f.profile.model_fingerprint, languages=("vi",)
    )
    assert [h.chunk.chunk_id for h in hits] == [points[1].chunk.chunk_id]
    assert (
        len(
            await f.repo.fetch(snapshot, tuple(p.chunk.chunk_id for p in points), languages=("en",))
        )
        == 3
    )
    assert all(kw.get("scroll_filter") for kind, kw in f.client.calls if kind == "scroll")
    print(
        "PASS fetch/neighbor: scoped anchor + unit/ordinal/language; foreign chunk IDs return empty"
    )


async def test_empty_scope_no_qdrant_request(fixture: Fixture) -> None:
    f = fixture
    target = await f.version()
    points = await f.seed(target)
    await f.publish(target)
    await f.attach(target)
    empty = replace(await f.snapshot(), pairs=())
    before = len(f.client.calls)
    for branch in ("dense", "sparse", "hybrid"):
        assert (
            await f.repo.search(empty, embedding(), f.profile.model_fingerprint, branch=branch)
            == ()
        )
    assert await f.repo.fetch(empty, (points[0].chunk.chunk_id,)) == ()
    assert await f.repo.fetch_neighbors(empty, points[0].chunk.chunk_id) == ()
    assert len(f.client.calls) == before
    print("PASS empty allowed set: zero Qdrant query/scroll calls across all read methods")


@pytest.mark.parametrize("change", ["detach", "delete", "reindex", "forged"])
async def test_pg_snapshot_is_authority(fixture: Fixture, change: str) -> None:
    f = fixture
    target = await f.version()
    points = await f.seed(target)
    await f.publish(target)
    await f.attach(target)
    old = await f.snapshot()
    if change == "detach":
        await f.sessions.detach_document(f.owner, f.session.session_id, target.pair.document_id)
    elif change == "delete":
        await f.sessions.delete_session(f.owner, f.session.session_id)
    elif change == "reindex":
        new = await f.generation(target)
        await f.seed(new)
        await f.publish(new)
        assert (await f.snapshot()).scope_revision == old.scope_revision
    else:
        foreign = await f.version()
        old = replace(old, pairs=(foreign.pair,))
    before = len(f.client.calls)
    with pytest.raises(ScopeError, match="session_scope_changed"):
        await f.repo.search(old, embedding(), f.profile.model_fingerprint)
    with pytest.raises(ScopeError, match="session_scope_changed"):
        await f.repo.fetch(old, (points[0].chunk.chunk_id,))
    with pytest.raises(ScopeError, match="session_scope_changed"):
        await f.repo.fetch_neighbors(old, points[0].chunk.chunk_id)
    assert len(f.client.calls) == before
    assert await f.repo.count_generation(target) == 4  # Retained vectors confer no authority.
    print(f"PASS PG {change}: stale/forged snapshot rejected before Qdrant; retained4vectors")


@pytest.mark.parametrize("read", ["query", "fetch", "neighbor-anchor", "neighbor-expansion"])
async def test_detach_after_actual_query_rejects_result(fixture: Fixture, read: str) -> None:
    f = fixture
    target = await f.version()
    points = await f.seed(target)
    await f.publish(target)
    await f.attach(target)
    snapshot = await f.snapshot()

    remaining = 2 if read == "neighbor-expansion" else 1

    async def detach() -> None:
        nonlocal remaining
        remaining -= 1
        if remaining == 0:
            await f.sessions.detach_document(f.owner, f.session.session_id, target.pair.document_id)

    if read == "query":
        f.client.after_query = detach
    else:
        f.client.after_scroll = detach
    with pytest.raises(ScopeError, match="session_scope_changed"):
        if read == "query":
            await f.repo.search(snapshot, embedding(), f.profile.model_fingerprint)
        elif read == "fetch":
            await f.repo.fetch(snapshot, (points[0].chunk.chunk_id,))
        else:
            await f.repo.fetch_neighbors(snapshot, points[0].chunk.chunk_id)
    assert remaining == 0
    print(f"PASS actual {read} completed then PG detach committed: no stale result returned")


async def test_idempotent_update_cleanup_and_retention(fixture: Fixture) -> None:
    f = fixture
    target = await f.version()
    points = await f.seed(target)
    await f.repo.upsert(target, points, f.profile.model_fingerprint)
    assert await f.repo.count_generation(target) == 4
    updated = tuple(replace(p, chunk=p.chunk.model_copy(update={"language": "vi"})) for p in points)
    await f.repo.upsert(target, updated, f.profile.model_fingerprint)
    assert [point_id(f.owner, p.chunk) for p in updated] == [
        point_id(f.owner, p.chunk) for p in points
    ]
    assert await f.repo.count_generation(target) == 4
    await f.publish(target)
    await f.attach(target)
    assert all(
        h.chunk.language == "vi"
        for h in await f.repo.fetch(await f.snapshot(), tuple(p.chunk.chunk_id for p in points))
    )
    with pytest.raises(VectorError, match="active_generation_immutable"):
        await f.repo.cleanup_generation(target)
    with pytest.raises(VectorError, match="active_generation_immutable"):
        await f.repo.upsert(target, points, f.profile.model_fingerprint)
    stale = await f.generation(target)
    await f.seed(stale)
    other = await f.version(Principal("other-app", "user-2"))
    await f.seed(other)
    for forged in (
        replace(stale, principal=other.principal),
        replace(stale, pair=replace(stale.pair, document_id=other.pair.document_id)),
    ):
        with pytest.raises(VectorError, match="generation_not_authorized"):
            await f.repo.cleanup_generation(forged)
    await f.repo.cleanup_generation(stale)
    await f.repo.cleanup_generation(stale)
    assert await f.repo.count_generation(stale) == 0
    assert await f.repo.count_generation(target) == await f.repo.count_generation(other) == 4
    await f.sessions.delete_session(f.owner, f.session.session_id)
    assert await f.repo.count_generation(target) == 4
    fresh = await f.sessions.create_session(f.owner, "new-session")
    with pytest.raises(ScopeError, match="no_session_documents"):
        await f.sessions.resolve_scope(f.owner, fresh.session_id)
    print(
        "PASS update/retry stableIDs count4; exact cleanup0; active/other owner retained4; new session empty"
    )


async def test_publication_waits_for_acknowledged_write(fixture: Fixture) -> None:
    f = fixture
    target = await f.version()
    f.client.write_entered, f.client.write_release = asyncio.Event(), asyncio.Event()
    writing = asyncio.create_task(f.seed(target))
    await asyncio.wait_for(f.client.write_entered.wait(), 3)
    publishing = asyncio.create_task(f.publish(target))
    try:
        # Observe the actual PG lock waiter, not merely unfinished Python scheduling.
        async with asyncio.timeout(3):
            while True:
                async with f.engine.connect() as conn:
                    blocked = (
                        await conn.execute(
                            text("""
                        SELECT count(*) FROM pg_stat_activity
                        WHERE datname=current_database() AND wait_event_type='Lock'
                          AND cardinality(pg_blocking_pids(pid)) > 0
                    """)
                        )
                    ).scalar_one()
                if blocked:
                    break
                await asyncio.sleep(0.02)
        assert not publishing.done()
        f.client.write_release.set()
        await asyncio.wait_for(writing, 5)
        await asyncio.wait_for(publishing, 5)
    finally:
        f.client.write_release.set()
        await asyncio.gather(writing, publishing, return_exceptions=True)
    assert await f.repo.count_generation(target) == 4
    print("PASS PG publication blocked by generation write lock until actual Qdrant wait=true ack")


async def test_payload_corruption_and_real_dependency_failure(fixture: Fixture) -> None:
    f = fixture
    target = await f.version()
    points = await f.seed(target)
    await f.publish(target)
    await f.attach(target)
    snapshot = await f.snapshot()
    await f.client.set_payload(
        f.profile.collection_name,
        payload={"locator": {"kind": "pdf", "page": 0}},
        points=[str(point_id(f.owner, points[0].chunk))],
        wait=True,
    )
    with pytest.raises(VectorError, match="invalid_vector_payload"):
        await f.repo.fetch(snapshot, (points[0].chunk.chunk_id,))
    # Real server 404, translated to a technical error without response/URL/payload text.
    await f.client.delete_collection(f.profile.collection_name)
    with pytest.raises(VectorError) as caught:
        await f.repo.search(snapshot, embedding(), f.profile.model_fingerprint)
    assert str(caught.value) == "vector_dependency_unavailable"
    await f.repo.ensure_collection()  # Restore only this fixture collection for teardown.
    print(
        "PASS actual corrupted payload rejected; actual missing collection -> sanitized technical error"
    )


async def test_collection_config_and_invalid_requests(fixture: Fixture) -> None:
    f = fixture
    await f.repo.ensure_collection()  # Existing compatible collection/index setup is idempotent.
    info = await f.client.get_collection(f.profile.collection_name)
    assert info.config.params.vectors["dense"].size == 1024
    assert set(info.config.params.sparse_vectors) == {"sparse"}
    assert {key: info.payload_schema[key].data_type for key in PAYLOAD_INDEXES} == PAYLOAD_INDEXES
    target = await f.version()
    points = await f.seed(target)
    await f.publish(target)
    await f.attach(target)
    scope = await f.snapshot()
    with pytest.raises(VectorError, match="index_model_mismatch"):
        await f.repo.search(scope, embedding(), "0" * 64)
    for languages in ((), ("fr",)):
        with pytest.raises(VectorError, match="invalid_vector_languages"):
            await f.repo.search(
                scope, embedding(), f.profile.model_fingerprint, languages=languages
            )
    with pytest.raises(VectorError, match="invalid_vector_write"):
        await f.repo.upsert(target, (points[0], points[0]), f.profile.model_fingerprint)
    invalid = replace(target, pair=replace(target.pair, document_id=uuid4()))
    with pytest.raises(VectorError, match="invalid_vector_write"):
        await f.repo.upsert(invalid, points, f.profile.model_fingerprint)
    other_profile = IndexProfile("f" * 64)
    assert other_profile.collection_name != f.profile.collection_name
    # Use this fixture's owned collection to prove fail-closed config handling, not user data.
    await f.client.delete_collection(f.profile.collection_name)
    await f.client.create_collection(
        f.profile.collection_name,
        vectors_config={"dense": qm.VectorParams(size=2, distance=qm.Distance.DOT)},
    )
    with pytest.raises(VectorError, match="incompatible_vector_collection"):
        await f.repo.ensure_collection()
    print(
        "PASS dense1024 Cosine/sparse/noIDF/9payload indexes/versioned fingerprint; incompatible rejected"
    )
