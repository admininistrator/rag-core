"""Standalone server subprocess runner for RAG Core test client."""

from __future__ import annotations

import asyncio
import contextlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import boto3
import httpx
import psycopg
from _pytest.monkeypatch import MonkeyPatch
from psycopg import sql

from rag_core.adapters.persistence.database import build_engine
from rag_core.adapters.persistence.registrations import (
    PostgresRegistrationRepository,
)
from rag_core.adapters.storage.s3 import S3StorageReader, StorageLocation, StorageRegistry
from rag_core.auth import Principal
from rag_core.workers.runtime import WorkerConfig
from tests.fixtures.public_support import public_environment

SECRET_DIR = Path(".local/secrets").resolve()
BUCKET = "rag-core-storage-test"


async def run_server() -> None:
    temp_dir = tempfile.TemporaryDirectory()
    tmp_path = Path(temp_dir.name)

    # 1. Database
    pg_pass = (SECRET_DIR / "t10_postgres_password").read_text().strip()
    admin_dsn = f"postgresql://rag_core_test:{pg_pass}@127.0.0.1:55432/t10_acceptance"
    db_name = f"t35_test_{uuid4().hex}"

    with psycopg.connect(admin_dsn, autocommit=True) as admin_conn:
        admin_conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))

    from sqlalchemy.engine import make_url

    test_db_url = make_url(
        f"postgresql+psycopg://rag_core_test:{pg_pass}@127.0.0.1:55432/{db_name}"
    )

    os.environ["DATABASE_URL"] = test_db_url.set(drivername="postgresql").render_as_string(
        hide_password=False
    )
    env = os.environ.copy()
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        env=env,
        check=True,
        capture_output=True,
    )

    # 2. Configs & endpoints
    inference_url = os.environ.get("INFERENCE_URL", "http://127.0.0.1:58080")
    qdrant_url = os.environ.get("QDRANT_URL", "http://127.0.0.1:56333")
    redis_url = os.environ.get("REDIS_URL", "redis://127.0.0.1:16379/15")
    s3_endpoint = os.environ.get("S3_ENDPOINT", "http://127.0.0.1:9000")
    os.environ["REDIS_URL"] = redis_url

    async with httpx.AsyncClient(trust_env=False) as client:
        resp = await client.get(f"{inference_url}/health/ready", timeout=5)
        model_fingerprint = resp.json().get("fingerprint")

    principal = Principal("test-app", "test-user")

    # Storage config
    registry = StorageRegistry(
        locations=(
            StorageLocation(
                app_id=principal.app_id,
                alias="fixture",
                endpoint=s3_endpoint,
                allow_loopback_http=True,
                bucket=BUCKET,
                region="us-east-1",
                prefix="allowed/",
                access_key_file=SECRET_DIR / "minio_reader_user",
                secret_key_file=SECRET_DIR / "minio_reader_password",
            ),
        )
    )
    storage_config_path = tmp_path / "storage.json"
    storage_config_path.write_text(registry.model_dump_json())

    worker_config = WorkerConfig(
        model_fingerprint=model_fingerprint,
        inference_url=inference_url,
        qdrant_url=qdrant_url,
        storage_config=storage_config_path,
        tokenizer_path=Path(".local/tokenizers/bge-m3/tokenizer.json").resolve(),
        temp_root=tmp_path / "worker-temp",
        lease_seconds=10,
        heartbeat_seconds=1,
    )
    worker_path = tmp_path / "worker.json"
    worker_path.write_text(worker_config.model_dump_json())

    engine = build_engine(test_db_url)
    repo = PostgresRegistrationRepository(
        engine, S3StorageReader(registry, temp_dir=tmp_path / "reg-temp")
    )
    uploader = boto3.client(
        "s3",
        endpoint_url=s3_endpoint,
        region_name="us-east-1",
        aws_access_key_id=(SECRET_DIR / "minio_uploader_user").read_text().strip(),
        aws_secret_access_key=(SECRET_DIR / "minio_uploader_password").read_text().strip(),
    )

    # Background ingestion processor (processes queued jobs directly without requiring Celery daemon or tesseract)
    import rag_core.workers.runtime as rt

    rt.extraction_revision = lambda parser: "test-extraction-rev"

    stop_event = asyncio.Event()

    async def ingestion_worker_task():
        from sqlalchemy import text

        while not stop_event.is_set():
            try:
                async with engine.connect() as conn:
                    res = await conn.execute(
                        text("SELECT job_id FROM ingestion_jobs WHERE state='queued' LIMIT 1")
                    )
                    row = res.fetchone()
                if row:
                    job_id = row[0]
                    await rt.run_job(job_id, worker_config)
                else:
                    await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                import traceback

                print(f"Ingestion error: {exc}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                await asyncio.sleep(0.1)

    ingest_task = asyncio.create_task(ingestion_worker_task())

    f = SimpleNamespace(
        tmp=tmp_path,
        config=worker_config,
        pg_url=test_db_url,
        principal=principal,
        uploader=uploader,
        repo=repo,
        engine=engine,
        start_worker=lambda: None,
    )

    monkeypatch = MonkeyPatch()
    try:
        async with public_environment(f, "deepseek", monkeypatch) as e:
            headers = e.headers()
            token = headers["Authorization"].removeprefix("Bearer ").strip()
            service_key = headers["X-RAG-Service-Key"]

            other_user_headers = e.headers(user="other-user")
            other_user_token = other_user_headers["Authorization"].removeprefix("Bearer ").strip()

            other_app_headers = e.headers(app_id="other-app")
            other_app_token = other_app_headers["Authorization"].removeprefix("Bearer ").strip()
            other_app_service_key = other_app_headers["X-RAG-Service-Key"]

            handshake = {
                "ready": True,
                "base_url": e.base_url,
                "auth_token": token,
                "service_key": service_key,
                "other_user_token": other_user_token,
                "other_app_token": other_app_token,
                "other_app_service_key": other_app_service_key,
                "app_id": principal.app_id,
                "user_id": principal.user_id,
                "db_name": db_name,
                "model_fingerprint": model_fingerprint,
                "qdrant_url": qdrant_url,
                "s3_endpoint": s3_endpoint,
                "bucket": BUCKET,
            }
            sys.stdout.write(json.dumps(handshake) + "\n")
            sys.stdout.flush()

            # Wait for stdin EOF
            loop = asyncio.get_running_loop()
            with contextlib.suppress(Exception):
                await loop.run_in_executor(None, sys.stdin.readline)
    except BaseException:
        import traceback

        traceback.print_exc(file=sys.stderr)
        raise

    # Cleanup
    stop_event.set()
    ingest_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await ingest_task

    await engine.dispose()

    with psycopg.connect(admin_dsn, autocommit=True) as admin_conn:
        admin_conn.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(db_name)))

    temp_dir.cleanup()


if __name__ == "__main__":
    asyncio.run(run_server())
