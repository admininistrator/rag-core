"""Trusted public API composition; one pool/model client and shared query admission."""

from collections.abc import AsyncIterator
from contextlib import AsyncExitStack, asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

import httpx
import httpx2
from pydantic import BaseModel, ConfigDict, Field
from qdrant_client import AsyncQdrantClient

from rag_core.adapters.llm.anthropic import AnthropicProvider
from rag_core.adapters.llm.config import AnthropicSettings, DeepSeekSettings, load_provider_settings
from rag_core.adapters.llm.deepseek import DeepSeekProvider
from rag_core.adapters.models.http import HttpModelInference
from rag_core.adapters.persistence.citations import PostgresCitationRepository
from rag_core.adapters.persistence.database import build_engine, database_url
from rag_core.adapters.persistence.evidence import PostgresEvidenceRepository
from rag_core.adapters.persistence.registrations import PostgresRegistrationRepository
from rag_core.adapters.persistence.sessions import PostgresSessionRepository
from rag_core.adapters.persistence.vector_generations import PostgresGenerationAuthority
from rag_core.adapters.storage.s3 import S3StorageReader, load_storage_registry
from rag_core.adapters.tokenizer import BgeM3Tokenizer
from rag_core.adapters.vectors.qdrant import QdrantVectorRepository
from rag_core.application.admission import QueryAdmission
from rag_core.application.answers import AnswerAssembler, AnswerPipeline
from rag_core.application.citations import CitationResolver
from rag_core.application.evidence import EvidenceSelector
from rag_core.application.query import QueryPreparation
from rag_core.application.retrieval import RetrievalPipeline
from rag_core.application.streaming import StreamingAnswerPipeline
from rag_core.config import Settings
from rag_core.domain.llm import Provider
from rag_core.domain.query import DomainRegistry, builtin_domains
from rag_core.domain.streaming import StreamPolicy
from rag_core.domain.vectors import IndexProfile


class ApiConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)
    provider: Provider
    model_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    inference_url: str = "http://inference:8080"
    tokenizer_path: Path = Path("/models/embedding/tokenizer.json")
    temp_root: Path = Path("/tmp/rag-api")
    stream: StreamPolicy = Field(default_factory=StreamPolicy)


@dataclass(frozen=True)
class PublicServices:
    sessions: PostgresSessionRepository
    registrations: PostgresRegistrationRepository
    answers: AnswerPipeline
    citations: CitationResolver
    streaming: StreamingAnswerPipeline
    admission: QueryAdmission
    policy: StreamPolicy


@asynccontextmanager
async def public_services(settings: Settings, config: ApiConfig) -> AsyncIterator[PublicServices]:
    """No migrations/model loading here. Caller owns lifetime through ASGI lifespan."""
    async with AsyncExitStack() as stack:
        engine = build_engine(
            database_url(str(settings.database_url), settings.database_password_file)
        )
        stack.push_async_callback(engine.dispose)
        client = AsyncQdrantClient(url=str(settings.qdrant_url), timeout=5, trust_env=False)
        stack.push_async_callback(client.close)
        sessions = PostgresSessionRepository(engine)
        profile = IndexProfile(config.model_fingerprint)
        vectors = QdrantVectorRepository(
            client, profile, sessions, PostgresGenerationAuthority(engine)
        )
        model_http = await stack.enter_async_context(
            httpx.AsyncClient(base_url=config.inference_url, trust_env=False, timeout=30)
        )
        models = HttpModelInference(model_http, config.model_fingerprint)
        tokenizer = BgeM3Tokenizer(config.tokenizer_path)
        if settings.storage_config_file is None:
            raise ValueError("STORAGE_CONFIG_FILE is required for public API")
        config.temp_root.mkdir(parents=True, exist_ok=True)
        storage = S3StorageReader(
            load_storage_registry(
                settings.storage_config_file, production=settings.app_env == "production"
            ),
            temp_dir=config.temp_root,
        )
        provider_config = load_provider_settings(config.provider)
        provider: DeepSeekProvider | AnthropicProvider
        if config.provider == "deepseek":
            assert isinstance(provider_config, DeepSeekSettings)
            pool = await stack.enter_async_context(httpx.AsyncClient(trust_env=False))
            provider = DeepSeekProvider(provider_config, pool)
        else:
            assert isinstance(provider_config, AnthropicSettings)
            pool2 = await stack.enter_async_context(httpx2.AsyncClient(trust_env=False))
            provider = AnthropicProvider(provider_config, pool2)
        preparation = QueryPreparation(
            DomainRegistry(builtin_domains()), sessions, vectors, tokenizer, provider
        )
        retrieval = RetrievalPipeline(models, config.model_fingerprint)
        selector = EvidenceSelector(
            PostgresEvidenceRepository(engine, sessions),
            models,
            config.model_fingerprint,
            tokenizer,
        )
        citations = PostgresCitationRepository(engine, sessions)
        assembler = AnswerAssembler(selector, citations, provider, tokenizer)
        yield PublicServices(
            sessions,
            PostgresRegistrationRepository(engine, storage),
            AnswerPipeline(preparation, retrieval, selector, assembler),
            CitationResolver(citations, sessions),
            StreamingAnswerPipeline(preparation, retrieval, selector, assembler, config.stream),
            QueryAdmission(
                config.stream.concurrency, config.stream.queue_size, config.stream.queue_timeout
            ),
            config.stream,
        )


def load_api_config(path: Path) -> ApiConfig:
    try:
        if path.stat().st_size > 16384:
            raise ValueError
        return ApiConfig.model_validate_json(path.read_bytes())
    except (OSError, ValueError):
        raise ValueError("Invalid API_CONFIG_FILE") from None
