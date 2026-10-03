"""Trusted runtime factory and full extraction/chunk/index revision fingerprints."""

import os
import subprocess
from dataclasses import asdict
from importlib.metadata import version
from pathlib import Path
from uuid import UUID

import httpx
from pydantic import BaseModel, ConfigDict, Field
from qdrant_client import AsyncQdrantClient

from rag_core.adapters.models.http import HttpModelInference
from rag_core.adapters.parsers.registry import ParserRegistry
from rag_core.adapters.persistence.database import build_engine, database_url_from_env
from rag_core.adapters.persistence.ingestion import PostgresIngestionRepository
from rag_core.adapters.persistence.sessions import PostgresSessionRepository
from rag_core.adapters.persistence.vector_generations import PostgresGenerationAuthority
from rag_core.adapters.storage.s3 import S3StorageReader, load_storage_registry
from rag_core.adapters.tokenizer import BgeM3Tokenizer
from rag_core.adapters.vectors.qdrant import QdrantVectorRepository
from rag_core.application.ingestion import IngestionPipeline
from rag_core.domain.chunking import StructuralChunker
from rag_core.domain.documents import OcrConfig, ParserLimits
from rag_core.domain.ingestion import digest
from rag_core.domain.vectors import IndexProfile


class WorkerConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)
    inference_url: str = Field(default="http://inference:8080", repr=False)
    qdrant_url: str = Field(default="http://qdrant:6333", repr=False)
    model_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    storage_config: Path = Path("/run/config/storage.json")
    tokenizer_path: Path = Path("/models/embedding/tokenizer.json")
    temp_root: Path = Path("/tmp/rag-ingestion")
    lease_seconds: int = Field(default=120, ge=10, le=600)
    heartbeat_seconds: float = Field(default=5, ge=0.1, le=30)
    timeout_seconds: float = Field(default=1800, ge=1, le=3600)


def extraction_revision(parser: ParserRegistry) -> str:
    import hashlib

    module = Path(__file__).parents[1]
    data = Path("/usr/share/tesseract-ocr/5/tessdata")
    engine = subprocess.run(["tesseract", "--version"], capture_output=True,
                            check=True, timeout=5).stdout.decode().splitlines()[0]
    files = tuple(sorted((module / "adapters/parsers").glob("*.py")))
    return digest({
        "revision": "extraction-v1", "limits": parser.limits.model_dump(),
        "ocr": parser.ocr.model_dump(mode="json"), "engine": engine,
        "languages": ["vie", "eng"], "dpi": 216, "image_scale": 1, "psm": 3,
        "traineddata": {name: hashlib.sha256((data / (name + ".traineddata")).read_bytes()).hexdigest()
                        for name in ("vie", "eng", "osd")},
        "code": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        "runtime": {name: version(name) for name in ("docling-parse", "docling-slim",
            "pypdfium2", "openpyxl", "pypdf", "python-docx", "python-pptx")},
    })


async def run_job(job_id: UUID, config: WorkerConfig) -> str:
    engine = build_engine(database_url_from_env())
    client = AsyncQdrantClient(url=config.qdrant_url, timeout=5, trust_env=False)
    config.temp_root.mkdir(parents=True, exist_ok=True)
    storage = S3StorageReader(load_storage_registry(config.storage_config,
        production=os.environ.get("APP_ENV") == "production"), temp_dir=config.temp_root)
    parser = ParserRegistry(config.temp_root, ParserLimits(), ocr=OcrConfig(enabled=True))
    chunker = StructuralChunker(BgeM3Tokenizer(config.tokenizer_path))
    profile = IndexProfile(config.model_fingerprint)
    extraction = extraction_revision(parser)
    pipeline = digest({"worker": "ingestion-v1", "extraction": extraction,
        "chunker": "structure-v1", "tokenizer": chunker.tokenizer.fingerprint,
        "chunk_code": digest(Path(__file__).parents[1].joinpath("domain/chunking.py").read_text()),
        "profile": asdict(chunker.profile), "index": profile.fingerprint})
    sessions = PostgresSessionRepository(engine)
    vectors = QdrantVectorRepository(client, profile, sessions, PostgresGenerationAuthority(engine))
    try:
        async with httpx.AsyncClient(base_url=config.inference_url, trust_env=False) as http:
            await vectors.ensure_collection()
            return await IngestionPipeline(
                PostgresIngestionRepository(engine, lease_seconds=config.lease_seconds),
                storage, parser, chunker, HttpModelInference(http, profile.model_fingerprint),
                vectors, profile, extraction_fingerprint=extraction, pipeline_fingerprint=pipeline,
                heartbeat_seconds=config.heartbeat_seconds, timeout_seconds=config.timeout_seconds,
            ).run(job_id)
    finally:
        await client.close()
        await engine.dispose()


def load_config() -> WorkerConfig:
    path = Path(os.environ.get("WORKER_CONFIG_FILE", "/run/config/worker.json"))
    try:
        if path.stat().st_size > 16384:
            raise ValueError
        config = WorkerConfig.model_validate_json(path.read_bytes())
        if config.heartbeat_seconds * 3 >= config.lease_seconds:
            raise ValueError
        return config
    except (OSError, ValueError):
        raise ValueError("invalid worker configuration") from None
