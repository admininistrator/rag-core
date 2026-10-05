"""Synthetic source documents; real PG/Qdrant/tokenizer/model, no evaluator gold."""

import json
from dataclasses import dataclass
from uuid import uuid4

import pytest_asyncio
from pydantic import TypeAdapter
from sqlalchemy import text

from rag_core.adapters.persistence.evidence import PostgresEvidenceRepository
from rag_core.adapters.tokenizer import BgeM3Tokenizer
from rag_core.application.evidence import EvidenceSelector
from rag_core.application.retrieval import RetrievalPipeline
from rag_core.auth import Principal
from rag_core.contracts.v1 import PdfLocator, XlsxLocator
from rag_core.domain.chunking import Chunk, StructuralChunker
from rag_core.domain.documents import Block, ParsedDocument, SourceIdentity
from rag_core.domain.ingestion import vector_unit_id
from rag_core.domain.models import InferenceRequest
from rag_core.domain.vectors import VectorChunk, VectorWrite
from tests.integration.test_retrieval import context

SOURCES = (
    ("capital-en", "en", "Hanoi is the capital of Vietnam. The Red River flows through Hanoi."),
    ("capital-vi", "vi", "Hà Nội là thủ đô của Việt Nam. Sông Hồng chảy qua Hà Nội."),
    ("revenue", "en", "Acme revenue in 2025: 12.5 million USD."),
    ("conflict", "en", "Acme revenue in 2025: 14.5 million USD."),
    ("fish", "en", "Ocean fish live in salt water. Marine biology studies whales and dolphins."),
    ("other-year", "en", "Acme revenue in 2024: 14.5 million USD."),
    ("table", "en", "table"),
)


@dataclass
class EvidenceFixture:
    f: object
    models: object
    tokenizer: BgeM3Tokenizer
    targets: dict
    chunks: dict
    vectors: dict
    foreign: tuple

    async def query(self, question, *, labels=None, languages=None, policy=None):
        ids = tuple(self.targets[k].pair.document_id for k in labels) if labels else None
        ctx = await context(self.f, question, languages=languages, document_ids=ids)
        retrieval = await RetrievalPipeline(self.models, self.models.expected_fingerprint).retrieve(
            ctx
        )
        selector = EvidenceSelector(
            PostgresEvidenceRepository(self.f.engine, self.f.sessions),
            self.models,
            self.models.expected_fingerprint,
            self.tokenizer,
            {"bounded-v1": policy} if policy is not None else None,
        )
        return ctx, retrieval, selector


async def seed(f, models, tokenizer, label, language, content, *, owner=None, session=None):
    target = await f.version(owner)
    locator = PdfLocator(kind="pdf", page=1)
    block = Block(kind="paragraph", text=content, locator=locator)
    format_ = "pdf"
    if label.startswith("table"):
        amount = "12.5" if content == "table" else content
        format_ = "xlsx"
        locator = XlsxLocator(kind="xlsx", sheet="Revenue", cell_range="A1:C2", unit="million USD")
        block = Block(
            kind="table",
            text=f"Company\tYear\tRevenue (million USD)\nAcme\t2025\t{amount}",
            locator=locator,
            rows=(("Company", "Year", "Revenue (million USD)"), ("Acme", "2025", amount)),
            table_headers=(("Company", "Year", "Revenue (million USD)"),),
        )
    document = ParsedDocument(
        source=SourceIdentity(
            document_id=target.pair.document_id, version_id=target.pair.version_id, sha256="a" * 64
        ),
        format=format_,
        parser_revision="synthetic-evidence-v1",
        blocks=(block,),
        page_count=1 if format_ == "pdf" else None,
    )
    chunks = StructuralChunker(tokenizer).chunk(document, generation_id=target.pair.generation_id)
    result = await models.infer(
        InferenceRequest(operation="embed", priority="index", texts=[c.text for c in chunks])
    )
    points = tuple(
        VectorWrite(
            VectorChunk(
                document_id=c.source.document_id,
                document_version_id=c.source.version_id,
                index_generation=c.generation_id,
                chunk_id=c.id,
                language=language,
                ordinal=c.ordinal,
                unit_id=vector_unit_id(c),
                locator=c.segments[0].locator,
            ),
            embedding,
        )
        for c, embedding in zip(chunks, result.embeddings, strict=True)
    )
    await f.repo.upsert(target, points, f.profile.model_fingerprint)
    adapter = TypeAdapter(Chunk)
    async with f.engine.begin() as conn:
        for c, p in zip(chunks, points, strict=True):
            await conn.execute(
                text("""
                INSERT INTO chunks (chunk_id,app_id,owner_id,version_id,generation_id,
                    ordinal,text,checksum,token_count,language,unit_id,source_map)
                VALUES (:id,:app,:owner,:version,:generation,:ordinal,:text,:sha,:tokens,
                    :language,:unit,CAST(:map AS jsonb))
            """),
                dict(
                    id=c.id,
                    app=target.principal.app_id,
                    owner=target.principal.user_id,
                    version=c.source.version_id,
                    generation=c.generation_id,
                    ordinal=c.ordinal,
                    text=c.text,
                    sha=c.checksum,
                    tokens=c.token_count,
                    language=language,
                    unit=p.chunk.unit_id,
                    map=json.dumps(adapter.dump_python(c, mode="json", exclude={"text"})),
                ),
            )
    await f.publish(target)
    await f.attach(target, session)
    return target, chunks[0], points[0].chunk


@pytest_asyncio.fixture
async def evidence_corpus(fixture, real_models):
    f = fixture
    # Fixture collection uses real model runtime profile rather than synthetic vector profile.
    from rag_core.adapters.persistence.vector_generations import PostgresGenerationAuthority
    from rag_core.adapters.vectors.qdrant import QdrantVectorRepository
    from rag_core.domain.vectors import IndexProfile

    original = f.repo
    f.profile = IndexProfile(real_models.expected_fingerprint)
    f.repo = QdrantVectorRepository(
        f.client, f.profile, f.sessions, PostgresGenerationAuthority(f.engine)
    )
    await f.repo.ensure_collection()
    tokenizer = BgeM3Tokenizer()
    targets, chunks, vectors = {}, {}, {}
    try:
        for label, language, content in SOURCES:
            targets[label], chunks[label], vectors[label] = await seed(
                f, real_models, tokenizer, label, language, content
            )
        foreign = []
        for owner in (
            f.owner,
            Principal(f.owner.app_id, "other-user"),
            Principal("other-" + uuid4().hex, f.owner.user_id),
        ):
            old = await f.sessions.create_session(owner, "retained-" + uuid4().hex)
            foreign.append(
                await seed(
                    f,
                    real_models,
                    tokenizer,
                    "foreign",
                    "en",
                    "SECRET OUTSIDE SESSION. Hanoi is Vietnam's capital.",
                    owner=owner,
                    session=old,
                )
            )
        yield EvidenceFixture(f, real_models, tokenizer, targets, chunks, vectors, tuple(foreign))
    finally:
        await f.client.delete_collection(f.profile.collection_name)
        f.repo = original
