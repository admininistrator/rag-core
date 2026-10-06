"""Trusted answer policy and source-mapped citations; model text grants no authority."""

import re
from dataclasses import dataclass
from typing import Annotated, Literal

from pydantic import Field

from rag_core.contracts.v1 import Citation, OffsetRange
from rag_core.domain.chunking import Chunk
from rag_core.domain.query import FrozenModel


class AnswerError(Exception):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class AnswerPolicy(FrozenModel):
    revision: Literal["mapped-quotes-v1"] = "mapped-quotes-v1"
    prompt_tokens: Annotated[int, Field(strict=True, ge=1, le=8000)] = 8000
    prompt_bytes: Annotated[int, Field(strict=True, ge=1, le=32768)] = 32768
    citation_limit: Annotated[int, Field(strict=True, ge=1, le=256)] = 256
    max_output_tokens: Annotated[int, Field(strict=True, ge=1, le=1024)] = 1024
    timeout_seconds: Annotated[float, Field(strict=True, gt=0, le=300, allow_inf_nan=False)] = 60.0


@dataclass(frozen=True)
class CitationSource:
    chunk: Chunk
    filename: str


class CitationDeclaration(FrozenModel):
    id: Annotated[str, Field(pattern=r"^c[1-9][0-9]*$", max_length=8)]
    quote: Annotated[str, Field(strict=True, min_length=1, max_length=32768, repr=False)]


class ModelAnswer(FrozenModel):
    answer: Annotated[str, Field(strict=True, min_length=1, max_length=32768, repr=False)]
    citations: Annotated[tuple[CitationDeclaration, ...], Field(max_length=256)]


def source_citations(source: CitationSource, first_id: int = 1) -> tuple[Citation, ...]:
    """Only verbatim mapped segments get IDs; separators and policy metadata do not.

    Quotes are canonical whole segments. Requiring exact echo prevents a model from
    substituting text, offsets, a locator or a version. Paragraphs/cells/OCR words
    can have separate IDs even in one embedding chunk.
    """
    chunk = source.chunk
    result: list[Citation] = []
    for segment in chunk.segments:
        if segment.role == "metadata":
            continue
        if (
            not 0 <= segment.start < segment.end <= len(chunk.text)
            or segment.source_start < 0
            or segment.source_end - segment.source_start != segment.end - segment.start
        ):
            raise AnswerError("citation_mapping_invalid")
        quote = chunk.text[segment.start : segment.end]
        if not quote.strip():
            continue
        locator = segment.locator.model_copy(deep=True)
        offsets = getattr(locator, "offsets", None)
        # Markup locators describe original raw spans, whereas chunk quotes are
        # normalized text. Keep those coarse spans; do not invent exact raw offsets.
        if segment.row is None and offsets is not None and locator.kind not in {"html", "md"}:
            if segment.source_end > offsets.end - offsets.start:
                raise AnswerError("citation_mapping_invalid")
            locator = locator.model_copy(
                update={
                    "offsets": OffsetRange(
                        start=offsets.start + segment.source_start,
                        end=offsets.start + segment.source_end,
                    )
                }
            )
        result.append(
            Citation(
                id=f"c{first_id + len(result)}",
                document_id=chunk.source.document_id,
                version_id=chunk.source.version_id,
                chunk_id=str(chunk.id),
                filename=source.filename,
                locator=locator,
                quote=quote,
            )
        )
    if not result:
        raise AnswerError("citation_mapping_invalid")
    return tuple(result)


def validate_answer(
    result: ModelAnswer, allowed: tuple[Citation, ...], *, supported: bool
) -> tuple[Citation, ...]:
    ids = {c.id: c for c in allowed}
    declared = {c.id: c for c in result.citations}
    # Detect malformed/unknown citation-shaped markers as well as syntactically valid IDs.
    markers = re.findall(r"\[([ce][^\]]*)\]", result.answer, flags=re.IGNORECASE)
    if (
        not result.answer.strip()
        or len(declared) != len(result.citations)
        or set(markers) != set(declared)
        or not set(declared) <= ids.keys()
        or (supported and not declared)
        or (not supported and (declared or markers))
        or any(c.quote != ids[c.id].quote for c in result.citations if c.id in ids)
    ):
        raise AnswerError("invalid_citation")
    # Core constructs all fields; model cannot supply document/version/locator/filename.
    return tuple(ids[c.id].model_copy(deep=True) for c in result.citations)
