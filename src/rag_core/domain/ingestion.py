"""Framework-independent worker lease and derivative manifest."""

import hashlib
import json
from dataclasses import dataclass
from uuid import UUID

from pydantic import TypeAdapter

from rag_core.auth import Principal
from rag_core.domain.chunking import Chunk
from rag_core.domain.vectors import GenerationScope
from rag_core.ports.storage import SourceObject


class IngestionError(Exception):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class IngestionLease:
    job_id: UUID
    principal: Principal
    session_id: UUID
    scope: GenerationScope
    owner: str
    source: SourceObject
    filename: str
    content_type: str
    size_bytes: int


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode()).hexdigest()


def chunk_manifest(chunks: tuple[Chunk, ...]) -> str:
    adapter = TypeAdapter(Chunk)
    return digest([(str(c.id), c.ordinal, c.checksum,
                    digest(adapter.dump_python(c, mode="json", exclude={"text"}))) for c in chunks])


def vector_unit_id(chunk: Chunk) -> str:
    """Conservative source boundary, never crossing page/table/heading/slide/region."""
    content = tuple(s for s in chunk.segments if s.role == "content") or chunk.segments
    first = content[0]
    loc = first.locator.model_dump(mode="json")
    boundary = {k: loc[k] for k in ("kind", "page", "sheet", "slide", "shape", "image_id")
                if k in loc}
    return digest([boundary, chunk.heading_path, first.block_index, first.source_part,
                   first.source_path])
