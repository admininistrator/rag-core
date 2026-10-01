"""Parser output is source data, never authorization or executable instructions."""

from typing import Annotated, Literal, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from rag_core.contracts.v1 import SourceLocator

DocumentFormat = Literal["pdf", "docx", "txt", "md", "html"]


class ParseError(Exception):
    """Public code only: never include source text, paths or backend exceptions."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class ParserLimits(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    max_bytes: int = Field(default=100 * 1024 * 1024, gt=0, le=100 * 1024 * 1024)
    max_pages: int = Field(default=1000, gt=0, le=1000)
    timeout_seconds: float = Field(default=60, gt=0, le=300, allow_inf_nan=False)
    max_archive_entries: int = Field(default=4096, gt=0)
    max_expanded_bytes: int = Field(default=256 * 1024 * 1024, gt=0)
    max_compression_ratio: int = Field(default=200, gt=0)
    max_blocks: int = Field(default=100_000, gt=0)
    max_text_chars: int = Field(default=8 * 1024 * 1024, gt=0)
    max_result_bytes: int = Field(default=32 * 1024 * 1024, gt=0)


class SourceIdentity(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    document_id: UUID
    version_id: UUID
    sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class Block(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal["paragraph", "heading", "table", "code", "header", "footer"]
    text: Annotated[str, Field(min_length=1)]
    locator: SourceLocator
    heading_path: tuple[str, ...] = ()
    # DOCX package member + XPath; PDF bbox uses native page coordinates.
    source_part: str | None = None
    source_path: str | None = None
    bbox: tuple[float, float, float, float] | None = None
    rows: tuple[tuple[str, ...], ...] = ()


class ParsedDocument(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    schema_version: Literal[1] = 1
    source: SourceIdentity
    format: DocumentFormat
    parser_revision: str
    blocks: Annotated[tuple[Block, ...], Field(min_length=1)]
    page_count: int | None = Field(default=None, gt=0)
    needs_ocr_pages: tuple[int, ...] = ()
    quality: Literal["text", "partial"] = "text"
    warnings: tuple[str, ...] = ()

    @model_validator(mode="after")
    def provenance(self) -> Self:
        if any(block.locator.kind != self.format for block in self.blocks):
            raise ValueError("Block format must match source")
        if self.format == "pdf":
            if self.page_count is None:
                raise ValueError("PDF requires physical page count")
            if any(
                block.locator.kind == "pdf" and block.locator.page > self.page_count
                for block in self.blocks
            ) or any(page < 1 or page > self.page_count for page in self.needs_ocr_pages):
                raise ValueError("PDF locator exceeds source")
        elif self.page_count is not None or self.needs_ocr_pages:
            raise ValueError("Non-PDF has no page numbers")
        if bool(self.needs_ocr_pages) != (self.quality == "partial"):
            raise ValueError("Partial extraction must identify missing pages")
        return self
