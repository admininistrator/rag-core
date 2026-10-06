"""Adversarial citation/JSON validation and trusted policy bounds, no service substitutes."""

from dataclasses import replace
from uuid import UUID

import pytest
from pydantic import ValidationError

from rag_core.application.answers import _model_answer
from rag_core.contracts.v1 import HtmlLocator, OffsetRange, PdfLocator, TextLocator
from rag_core.domain.answers import (
    AnswerError,
    AnswerPolicy,
    CitationSource,
    ModelAnswer,
    source_citations,
    validate_answer,
)
from rag_core.domain.chunking import Chunk, SourceSegment
from rag_core.domain.documents import SourceIdentity

pytestmark = pytest.mark.unit


def source():
    return CitationSource(
        Chunk(
            UUID(int=1),
            SourceIdentity(document_id=UUID(int=2), version_id=UUID(int=3), sha256="a" * 64),
            UUID(int=4),
            0,
            "Revenue 120 USD.\nsynthetic policy",
            8,
            "b" * 64,
            "c" * 64,
            "d" * 64,
            (),
            (SourceSegment(0, 16, 0, 0, 16, PdfLocator(kind="pdf", page=2)),),
        ),
        "report.pdf",
    )


@pytest.mark.parametrize(
    "answer,declared",
    [
        ("claim [c999]", [{"id": "c999", "quote": "Revenue 120 USD."}]),
        ("claim [c1]", [{"id": "c1", "quote": "forged"}]),
        ("claim [c1]", []),
        ("claim", [{"id": "c1", "quote": "Revenue 120 USD."}]),
        ("claim [c1] [e1]", [{"id": "c1", "quote": "Revenue 120 USD."}]),
        ("claim [c1] [C1]", [{"id": "c1", "quote": "Revenue 120 USD."}]),
        ("claim [c1] [c0]", [{"id": "c1", "quote": "Revenue 120 USD."}]),
        ("claim [c1] [c 2]", [{"id": "c1", "quote": "Revenue 120 USD."}]),
        ("claim [c1]", [{"id": "c1", "quote": "Revenue 120 USD."}] * 2),
    ],
)
def test_model_cannot_invent_or_hide_id_quote_declaration(answer, declared):
    with pytest.raises(AnswerError, match="invalid_citation"):
        validate_answer(
            ModelAnswer(answer=answer, citations=declared),
            source_citations(source()),
            supported=True,
        )


@pytest.mark.parametrize(
    "text",
    [
        "{}",
        "[]",
        "null",
        "{",
        '{"answer":"x","answer":"y","citations":[]}',
        '{"answer":"x","citations":[],"locator":{}}',
        '{"answer":"x","citations":[{"id":"c1","quote":"q","version_id":"override"}]}',
        "x" * 65537,
        '{"answer":"\\ud800","citations":[]}',
    ],
    ids=[
        "empty-object",
        "array",
        "null",
        "broken",
        "duplicate",
        "extra-field",
        "extra-citation-field",
        "overlimit",
        "invalid-unicode",
    ],
)
def test_invalid_json_and_metadata_are_safe_code_only(text):
    with pytest.raises(AnswerError) as error:
        _model_answer(text)
    assert str(error.value) == "invalid_citation"


def test_source_id_locator_and_synthetic_metadata():
    s = source()
    c = source_citations(s)[0]
    assert c.id == "c1" and c.locator.page == 2 and c.quote == "Revenue 120 USD."
    assert "synthetic" not in c.quote
    c.locator.page = 99
    assert s.chunk.segments[0].locator.page == 2
    bad = replace(s, chunk=replace(s.chunk, segments=(replace(s.chunk.segments[0], end=999),)))
    with pytest.raises(AnswerError, match="citation_mapping_invalid"):
        source_citations(bad)
    metadata = replace(
        s, chunk=replace(s.chunk, segments=(replace(s.chunk.segments[0], role="metadata"),))
    )
    with pytest.raises(AnswerError, match="citation_mapping_invalid"):
        source_citations(metadata)


def test_insufficient_cannot_echo_citations():
    result = ModelAnswer(
        answer="No evidence [c1]", citations=[{"id": "c1", "quote": "Revenue 120 USD."}]
    )
    with pytest.raises(AnswerError, match="invalid_citation"):
        validate_answer(result, source_citations(source()), supported=False)


@pytest.mark.parametrize("kind", ["md", "html"])
def test_normalized_markup_quote_preserves_coarse_original_span(kind):
    s = source()
    # Original markup contains syntax; normalized quote positions cannot narrow it.
    locator = (
        TextLocator(kind="md", line_start=1, line_end=1, offsets=OffsetRange(start=10, end=40))
        if kind == "md"
        else HtmlLocator(
            kind="html", heading_path=[], block=0, offsets=OffsetRange(start=10, end=40)
        )
    )
    mapped = replace(s.chunk.segments[0], locator=locator, source_start=3, source_end=19)
    citation = source_citations(replace(s, chunk=replace(s.chunk, segments=(mapped,))))[0]
    assert citation.quote == "Revenue 120 USD." and citation.locator.offsets == locator.offsets


@pytest.mark.parametrize(
    "field,value",
    [
        ("prompt_tokens", 0),
        ("prompt_tokens", 8001),
        ("prompt_bytes", 32769),
        ("citation_limit", 257),
        ("max_output_tokens", 1025),
        ("timeout_seconds", float("nan")),
        ("revision", "bypass"),
    ],
)
def test_trusted_profile_bounds(field, value):
    with pytest.raises(ValidationError):
        AnswerPolicy(**{field: value})
