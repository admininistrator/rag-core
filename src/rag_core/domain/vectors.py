"""Vector metadata and generation capabilities; no Qdrant/SQL/framework imports."""

import hashlib
import json
from dataclasses import dataclass
from typing import Literal
from uuid import NAMESPACE_URL, UUID, uuid5

from pydantic import BaseModel, ConfigDict, Field

from rag_core.auth import Principal
from rag_core.contracts.v1 import SourceLocator
from rag_core.domain.metadata import VersionGeneration
from rag_core.domain.models import Embedding

SearchBranch = Literal["dense", "sparse", "hybrid"]
GenerationOperation = Literal["write", "count", "cleanup"]


class VectorError(Exception):
    """Technical failures, never insufficient-evidence or upstream exception text."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class IndexProfile:
    # T17 runtime/model fingerprint, supplied by trusted operator/worker, not request body.
    model_fingerprint: str

    def __post_init__(self) -> None:
        if len(self.model_fingerprint) != 64 or any(
            c not in "0123456789abcdef" for c in self.model_fingerprint
        ):
            raise VectorError("invalid_index_profile")

    @property
    def fingerprint(self) -> str:
        value = {
            "schema": 1,
            "model": self.model_fingerprint,
            "dense": 1024,
            "distance": "Cosine",
            "sparse": "bge-m3-no-idf",
        }
        return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()

    @property
    def collection_name(self) -> str:
        return "rag_chunks_v1_" + self.fingerprint


@dataclass(frozen=True)
class GenerationScope:
    """Internal worker target; PG must verify owner/pair/fingerprint and lock it."""

    principal: Principal
    pair: VersionGeneration


class VectorChunk(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", hide_input_in_errors=True)
    document_id: UUID
    document_version_id: UUID
    index_generation: UUID
    chunk_id: UUID
    language: Literal["en", "vi", "und"]
    ordinal: int = Field(ge=0, le=10_000_000)
    # Trusted T16 structural unit (page/section/table region); never a caller scope.
    unit_id: str = Field(min_length=1, max_length=256)
    locator: SourceLocator

    @property
    def pair(self) -> VersionGeneration:
        return VersionGeneration(self.document_id, self.document_version_id, self.index_generation)


@dataclass(frozen=True)
class VectorWrite:
    chunk: VectorChunk
    embedding: Embedding


@dataclass(frozen=True)
class VectorHit:
    chunk: VectorChunk
    score: float | None = None


def point_id(principal: Principal, chunk: VectorChunk) -> UUID:
    """Separate owner namespaces even when chunk IDs are identical; retries replace."""
    identity = [
        principal.app_id,
        principal.user_id,
        str(chunk.document_id),
        str(chunk.document_version_id),
        str(chunk.index_generation),
        str(chunk.chunk_id),
    ]
    return uuid5(NAMESPACE_URL, json.dumps(identity, ensure_ascii=False))
