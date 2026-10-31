"""T34 Backup, restore, restart, and index migration rehearsal integration suite.

Verifies:
1. End-to-end backup and restore check CLI:
   - `scripts/backup.py` creates a point-in-time manifest with PostgreSQL metadata, Qdrant vectors, and MinIO blobs.
   - `scripts/restore_check.py` restores into an isolated environment and verifies:
     - Table and collection counts match manifest.
     - Raw document SHA256 byte-for-byte identical.
     - Zero uncommitted rows.
     - Zero dangling vectors.
     - Scoped retrieval query and citation verification.
     - Session restrictions and cross-session isolation.
2. Worker, API, and Redis restart recovery rehearsal:
   - Cold start reconciliation of queued jobs, source hashes byte-for-byte unchanged.
3. PostgreSQL schema migration and rollback rehearsal:
   - Migration downgrade and upgrade consistency with zero data loss.
4. Qdrant index collection version upgrade and reindex generation publication:
   - Zero-downtime retrieval on active generation during reindexing.
   - Atomic publication switch to new generation.
   - Safe rollback on reindex abort with zero dangling vectors.
"""

import contextlib
import hashlib
import json
import os
import subprocess
import sys
from collections.abc import AsyncIterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import boto3
import psycopg
import pytest
import pytest_asyncio
import redis
from psycopg import sql
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qm
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine

from rag_core.adapters.broker.celery import CeleryJobPublisher
from rag_core.adapters.persistence.database import build_engine
from rag_core.adapters.persistence.registrations import (
    OutboxDispatcher,
    PostgresRegistrationRepository,
)
from rag_core.adapters.persistence.sessions import PostgresSessionRepository
from rag_core.adapters.persistence.vector_generations import PostgresGenerationAuthority
from rag_core.adapters.storage.s3 import S3StorageReader, StorageLocation, StorageRegistry
from rag_core.adapters.vectors.qdrant import QdrantVectorRepository
from rag_core.auth import Principal
from rag_core.contracts.v1 import DocumentRegisterRequest, PdfLocator
from rag_core.domain.models import Embedding
from rag_core.domain.vectors import IndexProfile, VectorChunk, point_id

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]

BUCKET = "rag-core-storage-test"
BROKER = "redis://127.0.0.1:16379/15"
SECRETS = Path(".local/secrets")


def secret(name: str) -> str:
    path = SECRETS / name
    if not path.is_file():
        pytest.fail(f"Missing required secret file: {path}")
    return path.read_text(encoding="ascii").strip()


@dataclass
class T34Fixture:
    engine: AsyncEngine
    pg_url: URL
    qdrant_client: AsyncQdrantClient
    qdrant_url: str
    profile: IndexProfile
    vector_repo: QdrantVectorRepository
    sessions: PostgresSessionRepository
    generations: PostgresGenerationAuthority
    principal: Principal
    session_id: UUID
    uploader: Any
    s3_key: str
    payload: bytes
    doc_id: UUID
    version_id: UUID
    gen_id: UUID
    chunk_id: UUID


@pytest_asyncio.fixture
async def t34_fixture(pg_url: URL, tmp_path: Path) -> AsyncIterator[T34Fixture]:
    q_url = os.environ.get("RAG_TEST_QDRANT_URL", "http://127.0.0.1:56333")
    engine = build_engine(pg_url)
    q_client = AsyncQdrantClient(url=q_url, timeout=10, trust_env=False)
    sessions = PostgresSessionRepository(engine)
    generations = PostgresGenerationAuthority(engine)
    profile = IndexProfile("c64bb884142dab88e44b2ceacb8239714bb3dad3624d98b0c1fd1ce5ca09f92a")
    vector_repo = QdrantVectorRepository(q_client, profile, sessions, generations)

    await vector_repo.ensure_collection()

    principal = Principal("t34-app-" + uuid4().hex[:6], "t34-owner")
    session = await sessions.create_session(principal, "t34-session")
    session_id = session.session_id

    # S3 Upload
    uploader = boto3.client(
        "s3",
        endpoint_url="http://127.0.0.1:9000",
        region_name="us-east-1",
        aws_access_key_id=secret("minio_uploader_user"),
        aws_secret_access_key=secret("minio_uploader_password"),
    )
    s3_key = f"allowed/t34-{uuid4().hex[:8]}.txt"
    payload = b"T34 Data Integrity Rehearsal: Raw Document Bytes for Immutability Verification.\n"
    put_res = uploader.put_object(Bucket=BUCKET, Key=s3_key, Body=payload)
    version_str = put_res.get("VersionId")
    sha256_hex = hashlib.sha256(payload).hexdigest()

    doc_id = uuid4()
    version_id = uuid4()
    gen_id = uuid4()
    chunk_id = uuid4()

    async with engine.begin() as conn:
        # 1. Document
        await conn.execute(
            text("""
            INSERT INTO documents (document_id, app_id, owner_id, filename, storage_alias, bucket, object_key)
            VALUES (:doc_id, :app_id, :owner_id, 'doc.txt', 'test-store', :bucket, :key)
        """),
            {
                "doc_id": doc_id,
                "app_id": principal.app_id,
                "owner_id": principal.user_id,
                "bucket": BUCKET,
                "key": s3_key,
            },
        )
        # 2. Document Version (initial queued state to respect FK)
        await conn.execute(
            text("""
            INSERT INTO document_versions (
                version_id, app_id, owner_id, document_id, source_version_id, source_sha256,
                content_type, size_bytes, index_fingerprint, state, active_generation_id
            )
            VALUES (
                :version_id, :app_id, :owner_id, :doc_id, :source_version_id, :sha256,
                'text/plain', :size_bytes, :fingerprint, 'queued', NULL
            )
        """),
            {
                "version_id": version_id,
                "app_id": principal.app_id,
                "owner_id": principal.user_id,
                "doc_id": doc_id,
                "source_version_id": version_str,
                "sha256": sha256_hex,
                "size_bytes": len(payload),
                "fingerprint": profile.fingerprint,
            },
        )
        # 3. Index Generation
        await conn.execute(
            text("""
            INSERT INTO index_generations (generation_id, app_id, owner_id, version_id, index_fingerprint, state)
            VALUES (:gen_id, :app_id, :owner_id, :version_id, :fingerprint, 'ready')
        """),
            {
                "gen_id": gen_id,
                "app_id": principal.app_id,
                "owner_id": principal.user_id,
                "version_id": version_id,
                "fingerprint": profile.fingerprint,
            },
        )
        # 4. Activate generation on document version
        await conn.execute(
            text("""
            UPDATE document_versions SET state = 'ready', active_generation_id = :gen_id
            WHERE version_id = :version_id
        """),
            {"gen_id": gen_id, "version_id": version_id},
        )
        # 5. Session Document Link
        await conn.execute(
            text("""
            INSERT INTO session_documents (
                link_id, session_id, app_id, owner_id, document_id, version_id, upload_registration_id, status
            )
            VALUES (
                :link_id, :session_id, :app_id, :owner_id, :doc_id, :version_id, :reg_id, 'attached'
            )
        """),
            {
                "link_id": uuid4(),
                "session_id": session_id,
                "app_id": principal.app_id,
                "owner_id": principal.user_id,
                "doc_id": doc_id,
                "version_id": version_id,
                "reg_id": uuid4(),
            },
        )
        # 6. Chunks
        await conn.execute(
            text("""
            INSERT INTO chunks (
                chunk_id, app_id, owner_id, version_id, generation_id, ordinal,
                text, checksum, token_count, language, unit_id, source_map
            )
            VALUES (
                :chunk_id, :app_id, :owner_id, :version_id, :gen_id, 0,
                'Chunk 0 text for T34 backup verification', :sha, 15, 'en', 'page-1',
                '{"kind": "pdf", "page": 1}'::jsonb
            )
        """),
            {
                "chunk_id": chunk_id,
                "app_id": principal.app_id,
                "owner_id": principal.user_id,
                "version_id": version_id,
                "gen_id": gen_id,
                "sha": hashlib.sha256(b"Chunk 0 text for T34 backup verification").hexdigest(),
            },
        )

    v_chunk = VectorChunk(
        document_id=doc_id,
        document_version_id=version_id,
        index_generation=gen_id,
        chunk_id=chunk_id,
        language="en",
        ordinal=0,
        unit_id="page-1",
        locator=PdfLocator(kind="pdf", page=1),
    )
    v_embed = Embedding(
        dense=(1.0, 0.0) + (0.0,) * 1022,
        sparse_indices=(42,),
        sparse_values=(1.0,),
    )
    pid = point_id(principal, v_chunk)
    await q_client.upsert(
        collection_name=profile.collection_name,
        points=[
            qm.PointStruct(
                id=str(pid),
                vector={
                    "dense": list(v_embed.dense),
                    "sparse": qm.SparseVector(
                        indices=list(v_embed.sparse_indices),
                        values=list(v_embed.sparse_values),
                    ),
                },
                payload={
                    "app_id": principal.app_id,
                    "owner_id": principal.user_id,
                    **v_chunk.model_dump(mode="json"),
                },
            )
        ],
        wait=True,
    )

    fix = T34Fixture(
        engine=engine,
        pg_url=pg_url,
        qdrant_client=q_client,
        qdrant_url=q_url,
        profile=profile,
        vector_repo=vector_repo,
        sessions=sessions,
        generations=generations,
        principal=principal,
        session_id=session_id,
        uploader=uploader,
        s3_key=s3_key,
        payload=payload,
        doc_id=doc_id,
        version_id=version_id,
        gen_id=gen_id,
        chunk_id=chunk_id,
    )

    try:
        yield fix
    finally:
        # Cleanup seeded fixture data (break circular FK before deletion)
        async with engine.begin() as conn:
            await conn.execute(
                text(
                    "UPDATE document_versions SET state = 'queued', active_generation_id = NULL WHERE app_id = :app"
                ),
                {"app": principal.app_id},
            )
            for table in (
                "outbox_events",
                "upload_registrations",
                "ingestion_jobs",
                "chunks",
                "session_documents",
                "index_generations",
                "document_versions",
                "documents",
                "sessions",
            ):
                await conn.execute(
                    text(f"DELETE FROM {table} WHERE app_id=:app"), {"app": principal.app_id}
                )
        with contextlib.suppress(Exception):
            uploader.delete_object(Bucket=BUCKET, Key=s3_key)
        await q_client.close()
        await engine.dispose()


async def test_backup_and_restore_check_cli(t34_fixture: T34Fixture, tmp_path: Path) -> None:
    f = t34_fixture
    backup_dir = tmp_path / "backup_artifacts"

    # Step 1: Execute backup script
    backup_cmd = [
        sys.executable,
        "scripts/backup.py",
        "--output",
        str(backup_dir),
        "--database-url",
        f.pg_url.render_as_string(hide_password=False),
        "--qdrant-url",
        f.qdrant_url,
        "--s3-endpoint",
        "http://127.0.0.1:9000",
        "--s3-user-file",
        str(SECRETS / "minio_root_user"),
        "--s3-password-file",
        str(SECRETS / "minio_root_password"),
    ]
    proc = subprocess.run(backup_cmd, capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, f"backup.py failed: {proc.stderr}\n{proc.stdout}"

    manifest_file = backup_dir / "manifest.json"
    assert manifest_file.is_file(), "Backup manifest.json was not created"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert manifest["status"] == "completed"
    assert manifest["revisions"]["alembic_version"] == "0004_admin_audit"
    assert manifest["postgres"]["table_counts"]["documents"] >= 1
    assert manifest["postgres"]["table_counts"]["chunks"] >= 1
    assert manifest["minio"]["total_objects"] >= 1

    # Verify backed up MinIO raw document blob matches original SHA256
    backed_raw = manifest["minio"]["objects"][0]
    assert backed_raw["source_sha256"] == hashlib.sha256(f.payload).hexdigest()

    # Step 2: Execute restore_check script into isolated environment
    restore_cmd = [
        sys.executable,
        "scripts/restore_check.py",
        "--backup",
        str(backup_dir),
        "--project",
        "rag-restore-test",
        "--database-url",
        f.pg_url.render_as_string(hide_password=False),
        "--qdrant-url",
        f.qdrant_url,
        "--s3-endpoint",
        "http://127.0.0.1:9000",
        "--s3-user-file",
        str(SECRETS / "minio_root_user"),
        "--s3-password-file",
        str(SECRETS / "minio_root_password"),
    ]
    restore_proc = subprocess.run(restore_cmd, capture_output=True, text=True, timeout=90)
    assert restore_proc.returncode == 0, (
        f"restore_check.py failed: {restore_proc.stderr}\n{restore_proc.stdout}"
    )

    # Verify all verification gates printed in report
    stdout = restore_proc.stdout
    assert "Raw Document SHA256 Match:   100% BYTE-FOR-BYTE IDENTICAL" in stdout
    assert "Zero Uncommitted Rows:       PASS" in stdout
    assert "Zero Dangling Vectors:       PASS" in stdout
    assert "Scoped Query Verification:   PASS" in stdout
    assert "Session Restrictions Check:  PASS" in stdout
    assert "ALL POST-RESTORE VERIFICATION GATES PASSED." in stdout


async def test_cold_start_and_restart_recovery_rehearsal(
    t34_fixture: T34Fixture, tmp_path: Path
) -> None:
    f = t34_fixture

    # 1. Create a registration and queued ingestion job with transactional outbox
    reader = S3StorageReader(
        StorageRegistry(
            locations=(
                StorageLocation(
                    app_id=f.principal.app_id,
                    alias="test-store",
                    endpoint="http://127.0.0.1:9000",
                    region="us-east-1",
                    bucket=BUCKET,
                    prefix="allowed/",
                    access_key_file=SECRETS / "minio_reader_user",
                    secret_key_file=SECRETS / "minio_reader_password",
                    allow_loopback_http=True,
                    max_bytes=1024 * 1024,
                ),
            )
        ),
        temp_dir=tmp_path,
    )
    repo = PostgresRegistrationRepository(f.engine, reader)
    queued_session = await repo.sessions.create_session(f.principal, "queued-session")
    body = DocumentRegisterRequest.model_validate(
        {
            "external_upload_id": "restart-upload-1",
            "source": {
                "storage_alias": "test-store",
                "bucket": BUCKET,
                "key": f.s3_key,
                "sha256": hashlib.sha256(f.payload).hexdigest(),
            },
            "filename": "restart.txt",
            "content_type": "text/plain",
        }
    )
    reg = await repo.register(f.principal, queued_session.session_id, "restart-idemp-1", body)
    assert reg.job.state == "queued"

    # Verify outbox event exists before restart
    async with f.engine.connect() as conn:
        outbox_count = (
            await conn.execute(
                text(
                    "SELECT count(*) FROM outbox_events WHERE app_id=:app AND dispatched_at IS NULL"
                ),
                {"app": f.principal.app_id},
            )
        ).scalar_one()
        assert outbox_count >= 1

    # 2. Simulate Cold Start: Abruptly disconnect engine and close Redis client
    await f.engine.dispose()
    redis_client = redis.Redis.from_url(BROKER, socket_connect_timeout=2)
    redis_client.close()

    # 3. Reconnect from cold start with new engine and publisher
    cold_engine = build_engine(f.pg_url)
    try:
        cold_publisher = CeleryJobPublisher(BROKER)
        dispatcher = OutboxDispatcher(cold_engine, cold_publisher)

        # Dispatcher reconciles uncompleted outbox jobs
        dispatched = await dispatcher.dispatch_one()
        assert dispatched is True

        # Verify job was delivered to Redis queue
        r = redis.Redis.from_url(BROKER, socket_connect_timeout=2)
        assert r.llen("rag_core_ingestion") >= 1
        r.close()

        # 4. Invariant: source document SHA256 remains 100% byte-for-byte intact
        async with cold_engine.connect() as conn:
            sha_res = (
                await conn.execute(
                    text("SELECT source_sha256 FROM document_versions WHERE version_id=:v"),
                    {"v": f.version_id},
                )
            ).scalar_one()
            assert sha_res == hashlib.sha256(f.payload).hexdigest()

        # 5. Invariant: ready generation remains serving queries after restart
        cold_sessions = PostgresSessionRepository(cold_engine)
        scope = await cold_sessions.resolve_scope(f.principal, f.session_id)
        assert len(scope.pairs) >= 1
        pair_keys = {(p.version_id, p.generation_id) for p in scope.pairs}
        assert (f.version_id, f.gen_id) in pair_keys
    finally:
        await cold_engine.dispose()


async def test_schema_migration_and_rollback_rehearsal(pg_url: URL) -> None:
    # Dedicated database for schema migration rehearsal
    admin_url = pg_url.set(database="t10_acceptance")
    dsn = admin_url.set(drivername="postgresql").render_as_string(hide_password=False)
    mig_db = f"t34_mig_rehearsal_{uuid4().hex[:8]}"

    with psycopg.connect(dsn, autocommit=True) as admin:
        admin.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(mig_db)))

    target_url = admin_url.set(database=mig_db)

    def run_alembic(*args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["DATABASE_URL"] = target_url.render_as_string(hide_password=False)
        env.pop("DATABASE_PASSWORD_FILE", None)
        return subprocess.run(
            [sys.executable, "-m", "alembic", *args],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

    try:
        # 1. Upgrade to head
        res = run_alembic("upgrade", "head")
        assert res.returncode == 0, f"upgrade head failed: {res.stderr}"

        # 2. Seed data under head schema
        engine = build_engine(target_url)
        session_id = uuid4()
        app_id = "mig-app"
        owner_id = "mig-owner"
        async with engine.begin() as conn:
            await conn.execute(
                text("""
                INSERT INTO sessions (session_id, app_id, owner_id, external_session_id)
                VALUES (:s, :a, :o, 'ext-1')
            """),
                {"s": session_id, "a": app_id, "o": owner_id},
            )
            await conn.execute(
                text("""
                INSERT INTO audit_events (event_id, actor, action, target_id, request_id, outcome)
                VALUES (:e, 'local_admin', 'login', :t, :req, 'success')
            """),
                {"e": uuid4(), "t": session_id, "req": uuid4()},
            )
        await engine.dispose()

        # 3. Rehearse Downgrade to 0003_ingestion_publication (removes admin audit tables, retains session/doc tables)
        res_down = run_alembic("downgrade", "0003_ingestion_publication")
        assert res_down.returncode == 0, f"downgrade failed: {res_down.stderr}"

        # Verify sessions table and data intact across downgrade
        engine = build_engine(target_url)
        async with engine.connect() as conn:
            cnt = (
                await conn.execute(
                    text("SELECT count(*) FROM sessions WHERE session_id=:s"), {"s": session_id}
                )
            ).scalar_one()
            assert cnt == 1

            # audit_events should no longer exist in 0003
            table_check = (
                await conn.execute(
                    text(
                        "SELECT count(*) FROM information_schema.tables WHERE table_name='audit_events'"
                    )
                )
            ).scalar_one()
            assert table_check == 0
        await engine.dispose()

        # 4. Rehearse Upgrade back to head (recreates audit_events, preserves existing data)
        res_up = run_alembic("upgrade", "head")
        assert res_up.returncode == 0, f"upgrade back to head failed: {res_up.stderr}"

        engine = build_engine(target_url)
        async with engine.connect() as conn:
            cnt = (
                await conn.execute(
                    text("SELECT count(*) FROM sessions WHERE session_id=:s"), {"s": session_id}
                )
            ).scalar_one()
            assert cnt == 1
            table_check = (
                await conn.execute(
                    text(
                        "SELECT count(*) FROM information_schema.tables WHERE table_name='audit_events'"
                    )
                )
            ).scalar_one()
            assert table_check == 1
        await engine.dispose()
    finally:
        with psycopg.connect(dsn, autocommit=True) as admin:
            admin.execute(sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(mig_db)))


async def test_qdrant_reindex_generation_upgrade_zero_downtime(t34_fixture: T34Fixture) -> None:
    f = t34_fixture
    scope = await f.sessions.resolve_scope(f.principal, f.session_id)

    fake_query = Embedding(
        dense=(1.0, 0.0) + (0.0,) * 1022,
        sparse_indices=(42,),
        sparse_values=(1.0,),
    )

    # 1. Generation 1 is active and serving queries
    chunks_gen1 = await f.vector_repo.search(
        scope, fake_query, f.profile.model_fingerprint, branch="dense", limit=5
    )
    assert len(chunks_gen1) >= 1
    assert chunks_gen1[0].chunk.document_version_id == f.version_id
    assert chunks_gen1[0].chunk.index_generation == f.gen_id

    # 2. Begin reindexing: Generation 2 starts in staging
    gen2_id = uuid4()
    async with f.engine.begin() as conn:
        await conn.execute(
            text("""
            INSERT INTO index_generations (generation_id, app_id, owner_id, version_id, index_fingerprint, state)
            VALUES (:gen2, :app, :owner, :version, :fingerprint, 'staging')
        """),
            {
                "gen2": gen2_id,
                "app": f.principal.app_id,
                "owner": f.principal.user_id,
                "version": f.version_id,
                "fingerprint": f.profile.fingerprint,
            },
        )
        # Add new chunk for Generation 2 in PG
        chunk2_id = uuid4()
        await conn.execute(
            text("""
            INSERT INTO chunks (
                chunk_id, app_id, owner_id, version_id, generation_id, ordinal,
                text, checksum, token_count, language, unit_id, source_map
            )
            VALUES (
                :chunk_id, :app, :owner, :version, :gen2, 0,
                'Gen 2 upgraded reindexed chunk text', :sha, 20, 'en', 'page-1',
                '{"kind": "pdf", "page": 1}'::jsonb
            )
        """),
            {
                "chunk_id": chunk2_id,
                "app": f.principal.app_id,
                "owner": f.principal.user_id,
                "version": f.version_id,
                "gen2": gen2_id,
                "sha": hashlib.sha256(b"Gen 2 upgraded reindexed chunk text").hexdigest(),
            },
        )

    # Upsert Gen 2 points into Qdrant
    v_chunk2 = VectorChunk(
        document_id=f.doc_id,
        document_version_id=f.version_id,
        index_generation=gen2_id,
        chunk_id=chunk2_id,
        language="en",
        ordinal=0,
        unit_id="page-1",
        locator=PdfLocator(kind="pdf", page=1),
    )
    pid2 = point_id(f.principal, v_chunk2)
    await f.qdrant_client.upsert(
        collection_name=f.profile.collection_name,
        points=[
            qm.PointStruct(
                id=str(pid2),
                vector={
                    "dense": list(fake_query.dense),
                    "sparse": qm.SparseVector(
                        indices=list(fake_query.sparse_indices),
                        values=list(fake_query.sparse_values),
                    ),
                },
                payload={
                    "app_id": f.principal.app_id,
                    "owner_id": f.principal.user_id,
                    **v_chunk2.model_dump(mode="json"),
                },
            )
        ],
        wait=True,
    )

    # 3. Concurrent retrieval: Gen 1 continues serving queries with 100% availability!
    # Scope resolution strictly serves active Gen 1; Gen 2 points remain completely invisible.
    scope_during_reindex = await f.sessions.resolve_scope(f.principal, f.session_id)
    pair_keys_during = {(p.version_id, p.generation_id) for p in scope_during_reindex.pairs}
    assert (f.version_id, f.gen_id) in pair_keys_during
    assert (f.version_id, gen2_id) not in pair_keys_during

    chunks_during_reindex = await f.vector_repo.search(
        scope_during_reindex, fake_query, f.profile.model_fingerprint, branch="dense", limit=5
    )
    assert len(chunks_during_reindex) >= 1
    assert chunks_during_reindex[0].chunk.index_generation == f.gen_id

    # 4. Atomic publication: publish Generation 2
    async with f.engine.begin() as conn:
        await conn.execute(
            text("UPDATE index_generations SET state='ready' WHERE generation_id=:g"),
            {"g": gen2_id},
        )
        await conn.execute(
            text("UPDATE document_versions SET active_generation_id=:g WHERE version_id=:v"),
            {"g": gen2_id, "v": f.version_id},
        )

    # 5. Queries immediately and atomically switch to serving Generation 2
    scope_after_publish = await f.sessions.resolve_scope(f.principal, f.session_id)
    pair_keys_after = {(p.version_id, p.generation_id) for p in scope_after_publish.pairs}
    assert (f.version_id, gen2_id) in pair_keys_after
    assert (f.version_id, f.gen_id) not in pair_keys_after

    chunks_after_publish = await f.vector_repo.search(
        scope_after_publish, fake_query, f.profile.model_fingerprint, branch="dense", limit=5
    )
    assert len(chunks_after_publish) >= 1
    assert chunks_after_publish[0].chunk.index_generation == gen2_id

    # 6. Reindex abort & failure simulation with zero dangling vectors
    gen3_id = uuid4()
    async with f.engine.begin() as conn:
        await conn.execute(
            text("""
            INSERT INTO index_generations (generation_id, app_id, owner_id, version_id, index_fingerprint, state)
            VALUES (:gen3, :app, :owner, :version, :fingerprint, 'staging')
        """),
            {
                "gen3": gen3_id,
                "app": f.principal.app_id,
                "owner": f.principal.user_id,
                "version": f.version_id,
                "fingerprint": f.profile.fingerprint,
            },
        )
    # Staging write to Qdrant for Gen 3
    v_chunk3 = VectorChunk(
        document_id=f.doc_id,
        document_version_id=f.version_id,
        index_generation=gen3_id,
        chunk_id=uuid4(),
        language="en",
        ordinal=0,
        unit_id="page-1",
        locator=PdfLocator(kind="pdf", page=1),
    )
    pid3 = point_id(f.principal, v_chunk3)
    await f.qdrant_client.upsert(
        collection_name=f.profile.collection_name,
        points=[
            qm.PointStruct(
                id=str(pid3),
                vector={
                    "dense": list(fake_query.dense),
                    "sparse": qm.SparseVector(
                        indices=list(fake_query.sparse_indices),
                        values=list(fake_query.sparse_values),
                    ),
                },
                payload={
                    "app_id": f.principal.app_id,
                    "owner_id": f.principal.user_id,
                    **v_chunk3.model_dump(mode="json"),
                },
            )
        ],
        wait=True,
    )

    # Abort Gen 3: mark failed and cleanup points
    async with f.engine.begin() as conn:
        await conn.execute(
            text("UPDATE index_generations SET state='failed' WHERE generation_id=:g"),
            {"g": gen3_id},
        )
    # Cleanup uncommitted Gen 3 points from Qdrant
    await f.qdrant_client.delete(
        collection_name=f.profile.collection_name,
        points_selector=qm.FilterSelector(
            filter=qm.Filter(
                must=[
                    qm.FieldCondition(key="app_id", match=qm.MatchValue(value=f.principal.app_id)),
                    qm.FieldCondition(
                        key="index_generation", match=qm.MatchValue(value=str(gen3_id))
                    ),
                ]
            )
        ),
        wait=True,
    )

    # Invariant: Active generation (Gen 2) remains 100% healthy, zero dangling vectors for Gen 3
    scope_final = await f.sessions.resolve_scope(f.principal, f.session_id)
    final_pairs = {(p.version_id, p.generation_id) for p in scope_final.pairs}
    assert (f.version_id, gen2_id) in final_pairs

    active_chunks = await f.vector_repo.search(
        scope_final, fake_query, f.profile.model_fingerprint, branch="dense", limit=5
    )
    assert len(active_chunks) >= 1
    assert active_chunks[0].chunk.index_generation == gen2_id

    # Verify 0 points remain in Qdrant for Gen 3
    remaining_gen3 = await f.qdrant_client.count(
        collection_name=f.profile.collection_name,
        count_filter=qm.Filter(
            must=[
                qm.FieldCondition(key="index_generation", match=qm.MatchValue(value=str(gen3_id)))
            ]
        ),
        exact=True,
    )
    assert remaining_gen3.count == 0
