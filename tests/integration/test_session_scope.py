"""T10 acceptance: real PG ownership, atomic lifecycle and retained generations."""

import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine

from rag_core.adapters.persistence.database import build_engine
from rag_core.adapters.persistence.sessions import PostgresSessionRepository
from rag_core.auth import Principal
from rag_core.domain.metadata import ScopeError, Session

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


@dataclass
class Fixture:
    engine: AsyncEngine
    repo: PostgresSessionRepository
    principal: Principal
    session: Session

    async def version(
        self, *, ready: bool = True, owner: Principal | None = None
    ) -> tuple[UUID, UUID, UUID]:
        principal = owner or self.principal
        doc, version, generation = uuid4(), uuid4(), uuid4()
        params = {
            "app": principal.app_id,
            "owner": principal.user_id,
            "doc": doc,
            "version": version,
            "generation": generation,
        }
        async with self.engine.begin() as conn:
            await conn.execute(
                text("""
                INSERT INTO documents (document_id, app_id, owner_id, filename,
                    storage_alias, bucket, object_key)
                VALUES (:doc,:app,:owner,'fixture.txt','fixture','test-bucket','retained-source')
            """),
                params,
            )
            await conn.execute(
                text("""
                INSERT INTO document_versions (version_id, app_id, owner_id, document_id,
                    source_sha256, content_type, size_bytes, extraction_fingerprint, index_fingerprint)
                VALUES (:version,:app,:owner,:doc,repeat('a',64),'text/plain',10,'extract-v1','index-v1')
            """),
                params,
            )
            await conn.execute(
                text("""
                INSERT INTO index_generations (generation_id, app_id, owner_id, version_id,
                    state, index_fingerprint)
                VALUES (:generation,:app,:owner,:version,'ready','index-v1')
            """),
                params,
            )
            if ready:
                await conn.execute(
                    text("""
                    UPDATE document_versions SET state='ready', active_generation_id=:generation
                    WHERE version_id=:version
                """),
                    params,
                )
        return doc, version, generation

    async def attach(
        self, version: UUID, *, session: Session | None = None, registration: UUID | None = None
    ) -> Session:
        async with self.engine.begin() as conn:
            return await self.repo.attach_version(
                conn,
                self.principal,
                (session or self.session).session_id,
                version,
                registration or uuid4(),
            )


@pytest_asyncio.fixture
async def fixture(pg_url: URL) -> AsyncIterator[Fixture]:
    engine = build_engine(pg_url)
    repo = PostgresSessionRepository(engine)
    principal = Principal("app-" + uuid4().hex, "owner")
    session = await repo.create_session(principal, "external-chat")
    try:
        yield Fixture(engine, repo, principal, session)
    finally:
        await engine.dispose()


async def test_app_user_and_same_owner_session_isolation(fixture: Fixture) -> None:
    f = fixture
    doc, version, generation = await f.version()
    await f.attach(version)
    snapshot = await f.repo.resolve_scope(f.principal, f.session.session_id)
    assert [(p.document_id, p.version_id, p.generation_id) for p in snapshot.pairs] == [
        (doc, version, generation)
    ]
    for stranger in (Principal(f.principal.app_id, "other"), Principal("other-app", "owner")):
        own = await f.repo.create_session(stranger, "external-chat")
        assert own.session_id != f.session.session_id
        for method in (f.repo.get_session, f.repo.delete_session, f.repo.resolve_scope):
            with pytest.raises(ScopeError, match="not_found"):
                await method(stranger, f.session.session_id)
        with pytest.raises(ScopeError, match="not_found"):
            await f.repo.detach_document(stranger, f.session.session_id, doc)
        with pytest.raises(ScopeError, match="not_found"):
            async with f.engine.begin() as conn:
                await f.repo.attach_version(conn, stranger, own.session_id, version, uuid4())
    second = await f.repo.create_session(f.principal, "second-chat")
    with pytest.raises(ScopeError, match="no_session_documents"):
        await f.repo.resolve_scope(f.principal, second.session_id)
    with pytest.raises(ScopeError, match="not_found"):
        await f.repo.resolve_scope(f.principal, second.session_id, (doc,))
    await f.attach(version, session=second)
    await f.repo.detach_document(f.principal, f.session.session_id, doc)
    assert (await f.repo.resolve_scope(f.principal, second.session_id)).pairs == snapshot.pairs
    print("PASS isolation: app/user/current-session, explicit new registration, independent detach")


async def test_concurrent_create_unique_mapping_and_no_resurrection(fixture: Fixture) -> None:
    f = fixture
    sessions = await asyncio.gather(
        *(f.repo.create_session(f.principal, "same-external") for _ in range(8))
    )
    assert len({s.session_id for s in sessions}) == 1
    assert all(s.scope_revision == 0 for s in sessions)
    deleted = await f.repo.delete_session(f.principal, sessions[0].session_id)
    assert deleted.status == "deleted" and deleted.scope_revision == 1
    assert await f.repo.delete_session(f.principal, deleted.session_id) == deleted
    with pytest.raises(ScopeError, match="session_deleted"):
        await f.repo.create_session(f.principal, "same-external")
    with pytest.raises(ScopeError, match="session_deleted"):
        await f.repo.get_session(f.principal, deleted.session_id)


@pytest.mark.parametrize(
    "state",
    ["queued", "fetching", "parsing", "chunking", "embedding", "indexing", "failed", "cancelled"],
)
async def test_nonready_selection_never_silently_narrows(fixture: Fixture, state: str) -> None:
    f = fixture
    doc, version, _ = await f.version()
    other_doc, pending, _ = await f.version(ready=False)
    await f.attach(version)
    await f.attach(pending)
    async with f.engine.begin() as conn:
        await conn.execute(
            text("UPDATE document_versions SET state=:state WHERE version_id=:id"),
            {"state": state, "id": pending},
        )
    for subset in (None, (doc, other_doc), (other_doc,)):
        with pytest.raises(ScopeError, match="documents_not_ready"):
            await f.repo.resolve_scope(f.principal, f.session.session_id, subset)
    scoped = await f.repo.resolve_scope(f.principal, f.session.session_id, (doc,))
    assert len(scoped.pairs) == 1 and scoped.pairs[0].version_id == version
    with pytest.raises(ScopeError, match="not_found"):
        await f.repo.resolve_scope(f.principal, f.session.session_id, (doc, uuid4()))


async def test_empty_deleted_and_invalid_scope(fixture: Fixture) -> None:
    f = fixture
    with pytest.raises(ScopeError, match="no_session_documents"):
        await f.repo.resolve_scope(f.principal, f.session.session_id)
    for subset in ((), (uuid4(),) * 2, tuple(uuid4() for _ in range(51))):
        with pytest.raises(ScopeError, match="invalid_request"):
            await f.repo.resolve_scope(f.principal, f.session.session_id, subset)
    with pytest.raises(ScopeError, match="invalid_request"):
        await f.repo.create_session(f.principal, " \t")
    await f.repo.delete_session(f.principal, f.session.session_id)
    with pytest.raises(ScopeError, match="session_deleted"):
        await f.repo.resolve_scope(f.principal, f.session.session_id)
    with pytest.raises(ScopeError, match="not_found"):
        await f.repo.resolve_scope(f.principal, uuid4())


async def test_delete_idempotent_preserves_sources_versions_generations_jobs_outbox(
    fixture: Fixture,
) -> None:
    f = fixture
    doc, version, _ = await f.version()
    await f.attach(version)
    _, pending, _ = await f.version(ready=False)
    await f.attach(pending)
    job = uuid4()
    async with f.engine.begin() as conn:
        await conn.execute(
            text("""
            INSERT INTO ingestion_jobs (job_id,app_id,owner_id,version_id,task_fingerprint)
            VALUES (:job,:app,:owner,:version,'task-v1')
        """),
            {
                "job": job,
                "app": f.principal.app_id,
                "owner": f.principal.user_id,
                "version": pending,
            },
        )
        await conn.execute(
            text("""
            INSERT INTO outbox_events (event_id,app_id,owner_id,job_id,event_type)
            VALUES (:event,:app,:owner,:job,'ingest_requested')
        """),
            {"event": uuid4(), "app": f.principal.app_id, "owner": f.principal.user_id, "job": job},
        )
    tables = (
        "documents",
        "document_versions",
        "index_generations",
        "ingestion_jobs",
        "outbox_events",
    )

    async def retained() -> list[list[object]]:
        async with f.engine.connect() as conn:
            return [
                list(
                    (
                        await conn.execute(
                            text(
                                f"SELECT to_jsonb(t) FROM {table} t WHERE app_id=:app ORDER BY to_jsonb(t)::text"
                            ),
                            {"app": f.principal.app_id},
                        )
                    ).scalars()
                )
                for table in tables
            ]

    before = await retained()
    snapshot = await f.repo.resolve_scope(f.principal, f.session.session_id, (doc,))
    results = await asyncio.gather(
        *(f.repo.delete_session(f.principal, f.session.session_id) for _ in range(5))
    )
    assert all(r == results[0] for r in results)
    assert results[0].scope_revision == snapshot.scope_revision + 1
    assert before == await retained()
    with pytest.raises(ScopeError, match="session_scope_changed"):
        await f.repo.validate_snapshot(snapshot)
    with pytest.raises(ScopeError, match="session_deleted"):
        await f.attach(version)
    async with f.engine.begin() as conn:
        # A finishing worker cannot recreate links, even if it publishes a generation.
        await conn.execute(
            text("""
            UPDATE document_versions v SET state='ready', active_generation_id=g.generation_id
            FROM index_generations g WHERE v.version_id=:version AND g.version_id=v.version_id
        """),
            {"version": pending},
        )
        attached = (
            await conn.execute(
                text("""
            SELECT count(*) FROM session_documents WHERE session_id=:session AND status='attached'
        """),
                {"session": f.session.session_id},
            )
        ).scalar_one()
        assert attached == 0
    with pytest.raises(ScopeError, match="session_deleted"):
        await f.repo.resolve_scope(f.principal, f.session.session_id)
    print(
        "PASS repeated/concurrent delete: one revision, retained rows byte-equivalent, no resurrection"
    )


async def test_detach_snapshot_race_and_reregistration(fixture: Fixture) -> None:
    f = fixture
    doc, version, _ = await f.version()
    registration = uuid4()
    await f.attach(version, registration=registration)
    before = await f.repo.resolve_scope(f.principal, f.session.session_id)
    async with f.engine.begin() as writer:
        # An uncommitted writer holds the session lock; real detach must wait.
        await writer.execute(
            text("SELECT 1 FROM sessions WHERE session_id=:id FOR UPDATE"),
            {"id": f.session.session_id},
        )
        detach = asyncio.create_task(f.repo.detach_document(f.principal, f.session.session_id, doc))
        try:
            async with asyncio.timeout(5):
                while True:
                    async with f.engine.connect() as observer:
                        waiting = (
                            await observer.execute(
                                text("""
                            SELECT count(*) FROM pg_stat_activity WHERE datname=current_database()
                            AND wait_event_type='Lock' AND query LIKE '%FOR UPDATE%'
                        """)
                            )
                        ).scalar_one()
                    if waiting:
                        break
                    await asyncio.sleep(0.01)
            assert not detach.done()
            assert await f.repo.resolve_scope(f.principal, f.session.session_id) == before
        except BaseException:
            detach.cancel()
            await asyncio.gather(detach, return_exceptions=True)
            raise
    changed = await detach
    assert changed.scope_revision == before.scope_revision + 1
    with pytest.raises(ScopeError, match="session_scope_changed"):
        await f.repo.validate_snapshot(before)
    assert await f.repo.detach_document(f.principal, f.session.session_id, doc) == changed
    assert await f.attach(version, registration=registration) == changed
    with pytest.raises(ScopeError, match="no_session_documents"):
        await f.repo.resolve_scope(f.principal, f.session.session_id)
    new = await f.attach(version)  # Explicit new backend registration, not worker completion.
    assert new.scope_revision == changed.scope_revision + 1
    print(
        "PASS real lock race: old coherent snapshot then revision invalidation; replay stays detached"
    )


async def test_exact_generation_pairs_and_reindex_invalidates_snapshot(fixture: Fixture) -> None:
    f = fixture
    _, first, gen1 = await f.version()
    _, second, gen2 = await f.version()
    await f.attach(first)
    await f.attach(second)
    snapshot = await f.repo.resolve_scope(f.principal, f.session.session_id)
    assert {(p.version_id, p.generation_id) for p in snapshot.pairs} == {
        (first, gen1),
        (second, gen2),
    }
    await f.repo.validate_snapshot(snapshot)
    with pytest.raises(IntegrityError):
        async with f.engine.begin() as conn:
            await conn.execute(
                text("UPDATE document_versions SET active_generation_id=:g WHERE version_id=:v"),
                {"g": gen2, "v": first},
            )
    new_gen = uuid4()
    async with f.engine.begin() as conn:
        await conn.execute(
            text("""
            INSERT INTO index_generations (generation_id,app_id,owner_id,version_id,state,index_fingerprint)
            VALUES (:g,:app,:owner,:v,'staging','index-v2')
        """),
            {"g": new_gen, "app": f.principal.app_id, "owner": f.principal.user_id, "v": first},
        )
    assert await f.repo.resolve_scope(f.principal, f.session.session_id) == snapshot
    async with f.engine.begin() as conn:
        await conn.execute(
            text("UPDATE index_generations SET state='ready' WHERE generation_id=:g"),
            {"g": new_gen},
        )
        await conn.execute(
            text("UPDATE document_versions SET active_generation_id=:g WHERE version_id=:v"),
            {"g": new_gen, "v": first},
        )
    with pytest.raises(ScopeError, match="session_scope_changed"):
        await f.repo.validate_snapshot(snapshot)
    current = await f.repo.resolve_scope(f.principal, f.session.session_id)
    assert current.scope_revision == snapshot.scope_revision
    assert {(p.version_id, p.generation_id) for p in current.pairs} == {
        (first, new_gen),
        (second, gen2),
    }


async def test_constraints_reject_cross_owner_links_and_duplicate_registration(
    fixture: Fixture,
) -> None:
    f = fixture
    doc, version, _ = await f.version()
    registration = uuid4()
    await f.attach(version, registration=registration)
    same = await f.attach(version, registration=registration)
    assert same.scope_revision == 1
    foreign_doc, foreign_version, _ = await f.version(owner=Principal("foreign", "owner"))
    cases = [
        ("foreign", "owner", f.session.session_id, foreign_doc, foreign_version, uuid4()),
        (f.principal.app_id, "owner", f.session.session_id, foreign_doc, foreign_version, uuid4()),
        (f.principal.app_id, "owner", f.session.session_id, doc, version, registration),
        (f.principal.app_id, "owner", f.session.session_id, doc, version, uuid4()),
    ]
    for app, owner, session, document, ver, reg in cases:
        with pytest.raises(IntegrityError):
            async with f.engine.begin() as conn:
                await conn.execute(
                    text("""
                    INSERT INTO session_documents
                    (link_id,app_id,owner_id,session_id,document_id,version_id,upload_registration_id)
                    VALUES (:id,:app,:owner,:session,:doc,:ver,:reg)
                """),
                    {
                        "id": uuid4(),
                        "app": app,
                        "owner": owner,
                        "session": session,
                        "doc": document,
                        "ver": ver,
                        "reg": reg,
                    },
                )


async def test_limit_and_caller_transaction_rollback(fixture: Fixture) -> None:
    f = fixture
    _, version, _ = await f.version()
    with pytest.raises(RuntimeError, match="caller rollback"):
        async with f.engine.begin() as conn:
            await f.repo.attach_version(conn, f.principal, f.session.session_id, version, uuid4())
            raise RuntimeError("caller rollback")
    assert (await f.repo.get_session(f.principal, f.session.session_id)).scope_revision == 0
    for _ in range(50):
        _, ver, _ = await f.version()
        await f.attach(ver)
    with pytest.raises(ScopeError, match="invalid_request"):
        await f.attach(version)
    assert len((await f.repo.resolve_scope(f.principal, f.session.session_id)).pairs) == 50


async def test_unpublished_generation_and_immutable_source_constraints(fixture: Fixture) -> None:
    f = fixture
    _, version, generation = await f.version()
    await f.attach(version)
    async with f.engine.begin() as conn:
        await conn.execute(
            text("UPDATE index_generations SET state='staging' WHERE generation_id=:g"),
            {"g": generation},
        )
    with pytest.raises(ScopeError, match="documents_not_ready"):
        await f.repo.resolve_scope(f.principal, f.session.session_id)
    statements = [
        "UPDATE document_versions SET source_sha256=NULL, source_version_id=NULL WHERE version_id=:v",
        "UPDATE document_versions SET active_generation_id=NULL WHERE version_id=:v",
        "UPDATE document_versions SET source_sha256='bad' WHERE version_id=:v",
    ]
    for statement in statements:
        with pytest.raises(IntegrityError):
            async with f.engine.begin() as conn:
                await conn.execute(text(statement), {"v": version})


async def test_job_outbox_and_generation_owner_constraints(fixture: Fixture) -> None:
    f = fixture
    _, version, _ = await f.version()
    job = uuid4()
    params = {
        "job": job,
        "app": f.principal.app_id,
        "owner": f.principal.user_id,
        "v": version,
        "g": uuid4(),
        "e": uuid4(),
    }
    async with f.engine.begin() as conn:
        await conn.execute(
            text("""
            INSERT INTO ingestion_jobs (job_id,app_id,owner_id,version_id,task_fingerprint)
            VALUES (:job,:app,:owner,:v,'fixture')
        """),
            params,
        )
    statements = [
        """INSERT INTO ingestion_jobs (job_id,app_id,owner_id,version_id,task_fingerprint)
           VALUES (:e,'foreign',:owner,:v,'foreign')""",
        """INSERT INTO index_generations (generation_id,app_id,owner_id,version_id,index_fingerprint)
           VALUES (:g,:app,'foreign',:v,'foreign')""",
        """INSERT INTO outbox_events (event_id,app_id,owner_id,job_id,event_type)
           VALUES (:e,:app,'foreign',:job,'ingest_requested')""",
        "UPDATE ingestion_jobs SET attempts=max_attempts+1 WHERE job_id=:job",
        "UPDATE ingestion_jobs SET lease_owner='worker-without-expiry' WHERE job_id=:job",
    ]
    for statement in statements:
        with pytest.raises(IntegrityError):
            async with f.engine.begin() as conn:
                await conn.execute(text(statement), params)
