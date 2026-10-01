"""Actual pinned embedding tokenizer budgets and source-preserving structural behavior."""

from dataclasses import replace
from pathlib import Path
from uuid import UUID

import pytest

from rag_core.adapters.tokenizer import BgeM3Tokenizer
from rag_core.contracts.v1 import DocxLocator, OffsetRange, TextLocator
from rag_core.domain.chunking import ChunkingError, ChunkProfile, ChunkProfiles, StructuralChunker
from rag_core.domain.documents import Block, ParsedDocument, SourceIdentity

pytestmark = pytest.mark.unit
GENERATION = UUID(int=3)
SOURCE = SourceIdentity(document_id=UUID(int=1), version_id=UUID(int=2), sha256="a" * 64)


@pytest.fixture(scope="module")
def tokenizer() -> BgeM3Tokenizer:
    # Missing artifacts fail. Never skip or download during a unit test.
    return BgeM3Tokenizer()


def document(*texts: str) -> ParsedDocument:
    offset = 0
    blocks = []
    for i, text in enumerate(texts):
        blocks.append(
            Block(
                kind="paragraph",
                text=text,
                locator=TextLocator(
                    kind="txt",
                    paragraph=i,
                    offsets=OffsetRange(start=offset, end=offset + len(text)),
                ),
            )
        )
        offset += len(text) + 2
    return ParsedDocument(
        source=SOURCE, format="txt", parser_revision="fixture-v1", blocks=tuple(blocks)
    )


@pytest.mark.parametrize(
    "text",
    [
        "Doanh thu quý một đạt 120 triệu đồng. " * 250,
        "Vietnamese English financial report. " * 250,
        "Tiếng Việt e\u0301 👩🏽‍💻 🇻🇳 漢字 العربية\r\n" * 200,
        "supercalifragilisticexpialidocious" * 250,
        "<s> </s> <mask>\t\n" * 250,
    ],
    ids=["vietnamese", "english", "combining-emoji-scripts", "unbroken", "special-token-text"],
)
def test_real_token_windows_unicode_coverage_overlap_and_quotes(tokenizer, text):
    parsed = document(text)
    chunks = StructuralChunker(tokenizer).chunk(parsed, generation_id=GENERATION)
    assert len(chunks) > 1
    recovered = ""
    last_end = 0
    for i, chunk in enumerate(chunks):
        assert chunk.token_count == tokenizer.count(chunk.text) <= 512
        assert chunk.checksum and chunk.pipeline_fingerprint
        segment = chunk.segments[-1]
        assert segment.source_end > last_end
        recovered += parsed.blocks[0].text[last_end : segment.source_end]
        last_end = segment.source_end
        quotes = chunk.quotes(parsed, 0, len(chunk.text))
        assert "".join(q.text for q in quotes) == chunk.text
        overlap = "".join(q.text for q in quotes if q.segment.role == "overlap")
        assert tokenizer.count(overlap, special_tokens=False) <= 64
        if i:
            assert overlap
            assert chunks[i - 1].text.endswith(overlap)
    assert recovered == text and last_end == len(text)


def test_real_token_budget_includes_special_tokens(tokenizer):
    parsed = document("word " * 1800)
    chunks = StructuralChunker(tokenizer, ChunkProfile(max_tokens=34, overlap_tokens=7)).chunk(
        parsed, generation_id=GENERATION
    )
    assert tokenizer.count("") == 2
    assert all(c.token_count <= 34 for c in chunks)
    assert max(c.token_count for c in chunks) == 34


def test_paragraph_heading_units_and_overlap(tokenizer):
    parsed = document(*[f"Paragraph {i}: " + "doanh thu " * 15 for i in range(40)])
    chunks = StructuralChunker(tokenizer, ChunkProfile(max_tokens=128, overlap_tokens=16)).chunk(
        parsed, generation_id=GENERATION
    )
    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk.token_count <= 128
        # Each newly introduced paragraph ends at its boundary, no arbitrary cut.
        final = chunk.segments[-1]
        assert final.source_end == len(parsed.blocks[final.block_index].text)
    assert any(s.role == "overlap" for c in chunks for s in c.segments)
    heading = Block(
        kind="heading",
        text="New section",
        heading_path=("New section",),
        locator=TextLocator(kind="txt", paragraph=41),
    )
    after = parsed.blocks[0].model_copy(update={"heading_path": ("New section",)})
    separate = parsed.model_copy(update={"blocks": (*parsed.blocks, heading, after)})
    result = StructuralChunker(tokenizer).chunk(separate, generation_id=GENERATION)
    assert result[-2].text == "New section"
    assert result[-1].heading_path == ("New section",)
    assert all(s.role != "overlap" for s in result[-1].segments)


def table_document(rows):
    block = Block(
        kind="table",
        text="\n".join("\t".join(r) for r in rows),
        rows=tuple(rows),
        table_headers=(rows[0],),
        locator=DocxLocator(kind="docx", table=0, heading_path=["Revenue"]),
        heading_path=("Revenue",),
    )
    return ParsedDocument(
        source=SOURCE, format="docx", parser_revision="fixture-v1", blocks=(block,)
    )


def test_long_table_row_groups_headers_units_and_exact_cells(tokenizer):
    rows = [("Quarter", "Revenue (triệu đồng)")] + [(f"Q{i}", f"{i * 120}") for i in range(1, 301)]
    parsed = table_document(rows)
    chunks = StructuralChunker(tokenizer).chunk(parsed, generation_id=GENERATION)
    assert len(chunks) > 1
    covered = set()
    for chunk in chunks:
        assert chunk.text.startswith("Quarter\tRevenue (triệu đồng)\n")
        assert tokenizer.count(chunk.text) <= 512
        assert any(s.role == "context" and s.row == 0 for s in chunk.segments)
        for q in chunk.quotes(parsed, 0, len(chunk.text)):
            s = q.segment
            assert q.text == rows[s.row][s.column]
            if s.role == "content":
                covered.add(s.row)
        body_rows = sorted({s.row for s in chunk.segments if s.role == "content"})
        assert body_rows == list(range(body_rows[0], body_rows[-1] + 1))
    assert covered == set(range(1, 301))


@pytest.mark.parametrize("case", ["cell", "header"])
def test_oversized_table_cell_or_header_fails_without_silent_truncation(tokenizer, case):
    huge = "very long " * 700
    rows = [
        (huge if case == "header" else "Column", "Unit (VND)"),
        (huge if case == "cell" else "Row", "120"),
    ]
    with pytest.raises(
        ChunkingError, match="table_header_too_large" if case == "header" else "table_row_too_large"
    ):
        StructuralChunker(tokenizer).chunk(table_document(rows), generation_id=GENERATION)


def test_stable_ids_and_versioned_fingerprints(tokenizer):
    parsed = document("Doanh thu " * 250)
    chunker = StructuralChunker(tokenizer)
    initial = chunker.chunk(parsed, generation_id=GENERATION)
    assert initial == chunker.chunk(
        ParsedDocument.model_validate_json(parsed.model_dump_json()), generation_id=GENERATION
    )
    for changed in [
        parsed.model_copy(
            update={"source": SOURCE.model_copy(update={"version_id": UUID(int=10)})}
        ),
        parsed.model_copy(
            update={"source": SOURCE.model_copy(update={"document_id": UUID(int=10)})}
        ),
        parsed.model_copy(update={"parser_revision": "fixture-v2"}),
        document("Different contents"),
    ]:
        assert initial[0].id != chunker.chunk(changed, generation_id=GENERATION)[0].id
    assert initial[0].id != chunker.chunk(parsed, generation_id=UUID(int=10))[0].id
    for config in [
        replace(chunker.profile, revision="2"),
        replace(chunker.profile, max_tokens=256),
        replace(chunker.profile, overlap_tokens=32),
    ]:
        other = StructuralChunker(tokenizer, config).chunk(parsed, generation_id=GENERATION)
        assert initial[0].id != other[0].id
        assert initial[0].pipeline_fingerprint != other[0].pipeline_fingerprint
    other = chunker.chunk(parsed, generation_id=GENERATION, extraction_fingerprint="extract-v2")
    assert initial[0].pipeline_fingerprint != other[0].pipeline_fingerprint


def test_source_quote_version_ranges_and_output_limits(tokenizer):
    parsed = document("Evidence " * 500)
    first = StructuralChunker(tokenizer).chunk(parsed, generation_id=GENERATION)[0]
    with pytest.raises(ChunkingError, match="source_mapping_mismatch"):
        first.quotes(document("Different source"), 0, 1)
    for start, end in [(-1, 2), (0, len(first.text) + 1), (1, 1)]:
        with pytest.raises(ChunkingError, match="invalid_quote_range"):
            first.quotes(parsed, start, end)
    for profile in [ChunkProfile(max_chunks=1), ChunkProfile(max_output_chars=10)]:
        with pytest.raises(ChunkingError, match="chunk_output_limit"):
            StructuralChunker(tokenizer, profile).chunk(parsed, generation_id=GENERATION)


def test_trusted_domain_profile_hook_and_unknown_domain(tokenizer):
    profiles = ChunkProfiles()
    assert {profiles.for_domain(d).max_tokens for d in ["default", "document", "multilingual"]} == {
        512
    }
    custom = ChunkProfiles({"custom": ChunkProfile(name="custom", revision="2", max_tokens=256)})
    result = StructuralChunker(tokenizer, custom.for_domain("custom")).chunk(
        document("Revenue " * 800), generation_id=GENERATION
    )
    assert all(c.token_count <= 256 for c in result)
    with pytest.raises(ChunkingError, match="unknown_chunk_profile"):
        profiles.for_domain("arbitrary")


def test_tokenizer_artifact_corruption_is_refused(tmp_path: Path):
    path = tmp_path / "tokenizer.json"
    path.write_bytes(b'{"different": true}')
    with pytest.raises(ValueError, match="tokenizer_checksum_mismatch"):
        BgeM3Tokenizer(path)


def test_tokenizer_identity_participates_in_fingerprint(tokenizer):
    class RevisionedTokenizer(BgeM3Tokenizer):
        @property
        def fingerprint(self):
            return super().fingerprint + "/new-adapter-revision"

    parsed = document("Doanh thu 120 triệu đồng.")
    old = StructuralChunker(tokenizer).chunk(parsed, generation_id=GENERATION)[0]
    new = StructuralChunker(RevisionedTokenizer()).chunk(parsed, generation_id=GENERATION)[0]
    assert old.text == new.text and old.token_count == new.token_count
    assert old.id != new.id and old.pipeline_fingerprint != new.pipeline_fingerprint


def test_partial_pdf_refuses_chunk_publication(tokenizer):
    from rag_core.contracts.v1 import PdfLocator

    partial = ParsedDocument(
        source=SOURCE,
        format="pdf",
        parser_revision="fixture-v1",
        page_count=2,
        quality="partial",
        needs_ocr_pages=(2,),
        blocks=(Block(kind="paragraph", text="Page one", locator=PdfLocator(kind="pdf", page=1)),),
    )
    with pytest.raises(ChunkingError, match="partial_extraction"):
        StructuralChunker(tokenizer).chunk(partial, generation_id=GENERATION)


def test_real_tokenizer_does_not_truncate_long_input(tokenizer):
    text = "word " * 10_000
    assert tokenizer.count(text) > 8192
    parsed = document(text)
    chunks = StructuralChunker(tokenizer).chunk(parsed, generation_id=GENERATION)
    assert all(c.token_count <= 512 for c in chunks)
    assert chunks[-1].segments[-1].source_end == len(text)
