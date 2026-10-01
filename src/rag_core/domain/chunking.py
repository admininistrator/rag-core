"""Structural embedding chunks with explicit, lossless source segment mappings.

This synchronous CPU port must be offloaded by future asynchronous orchestration.
Source IDs and generation IDs are provenance, never authorization.
"""

import hashlib
import json
import re
from bisect import bisect_right
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, replace
from types import MappingProxyType
from typing import Literal
from uuid import UUID, uuid5

from rag_core.contracts.v1 import OffsetRange, SourceLocator, XlsxLocator
from rag_core.domain.documents import Block, ParsedDocument, SourceIdentity, TableCell
from rag_core.ports.tokenizer import EmbeddingTokenizer

CHUNKER_REVISION = "structure-v1"
CHUNK_NAMESPACE = UUID("8cbe39b6-9466-47d8-af22-708aa1ec70af")
Role = Literal["content", "context", "overlap", "metadata"]


class ChunkingError(Exception):
    """Safe code only, never document text."""


@dataclass(frozen=True)
class ChunkProfile:
    name: str = "baseline"
    revision: str = "1"
    max_tokens: int = 512
    overlap_tokens: int = 64
    max_chunks: int = 100_000
    max_output_chars: int = 32 * 1024 * 1024

    def __post_init__(self) -> None:
        if (
            not self.name
            or not self.revision
            or not 4 <= self.max_tokens <= 8192
            or not 0 <= self.overlap_tokens < self.max_tokens - 2
            or self.max_chunks < 1
            or self.max_output_chars < 1
        ):
            raise ValueError("invalid_chunk_profile")


class ChunkProfiles:
    """Trusted code/config hook; request/source data cannot register executable hooks."""

    def __init__(self, profiles: Mapping[str, ChunkProfile] | None = None) -> None:
        self._profiles = MappingProxyType(
            dict(
                profiles
                if profiles is not None
                else {
                    "default": ChunkProfile(),
                    "document": ChunkProfile(),
                    "multilingual": ChunkProfile(),
                }
            )
        )

    def for_domain(self, domain: str) -> ChunkProfile:
        try:
            return self._profiles[domain]
        except KeyError:
            raise ChunkingError("unknown_chunk_profile") from None


def _hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def parsed_fingerprint(document: ParsedDocument) -> str:
    # Include text, cell context, provenance and parser revision, excluding timings/RSS.
    data = document.model_dump(mode="json", exclude={"ocr"})
    if document.ocr is not None:
        data["ocr"] = {
            "engine": document.ocr.engine,
            "engine_version": document.ocr.engine_version,
            "languages": document.ocr.languages,
            "completed_pages": document.ocr.completed_pages,
        }
    return _hash(data)


@dataclass(frozen=True)
class SourceSegment:
    start: int
    end: int
    block_index: int
    source_start: int
    source_end: int
    locator: SourceLocator
    role: Role = "content"
    # row/column refer to Block.rows, not page or byte offsets.
    row: int | None = None
    column: int | None = None
    source_part: str | None = None
    source_path: str | None = None
    bbox: tuple[float, float, float, float] | None = None


@dataclass(frozen=True)
class MappedQuote:
    text: str
    segment: SourceSegment


@dataclass(frozen=True)
class Chunk:
    id: UUID
    source: SourceIdentity
    generation_id: UUID
    ordinal: int
    text: str
    token_count: int
    checksum: str
    pipeline_fingerprint: str
    parsed_fingerprint: str
    heading_path: tuple[str, ...]
    segments: tuple[SourceSegment, ...]
    cells: tuple[TableCell, ...] = ()

    def quotes(self, document: ParsedDocument, start: int, end: int) -> tuple[MappedQuote, ...]:
        """Resolve only mapped source substrings; synthetic separators/metadata have no quote.

        Future T24 must authorize owner/session/version/generation before calling this.
        Coarse original locator + exact normalized block/cell offsets are always retained.
        """
        if (
            document.source != self.source
            or parsed_fingerprint(document) != self.parsed_fingerprint
        ):
            raise ChunkingError("source_mapping_mismatch")
        if not 0 <= start < end <= len(self.text):
            raise ChunkingError("invalid_quote_range")
        result = []
        for segment in self.segments:
            a, b = max(start, segment.start), min(end, segment.end)
            if a >= b or segment.role == "metadata":
                continue
            block = document.blocks[segment.block_index]
            source_text = (
                block.text
                if segment.row is None
                else block.rows[segment.row][segment.column if segment.column is not None else 0]
            )
            source_a = segment.source_start + a - segment.start
            source_b = segment.source_start + b - segment.start
            quote = self.text[a:b]
            if source_text[source_a:source_b] != quote:
                raise ChunkingError("source_mapping_mismatch")
            locator = segment.locator
            # Only narrow source offsets where parser offsets describe verbatim block text.
            offsets = getattr(locator, "offsets", None)
            if (
                segment.row is None
                and offsets is not None
                and locator.kind != "html"
                and offsets.end - offsets.start == len(block.text)
            ):
                locator = locator.model_copy(
                    update={
                        "offsets": OffsetRange(
                            start=offsets.start + source_a, end=offsets.start + source_b
                        )
                    }
                )
            result.append(
                MappedQuote(
                    quote,
                    replace(
                        segment,
                        start=a,
                        end=b,
                        source_start=source_a,
                        source_end=source_b,
                        locator=locator,
                    ),
                )
            )
        if not result:
            raise ChunkingError("quote_has_no_source")
        return tuple(result)


@dataclass(frozen=True)
class _Piece:
    text: str
    segments: tuple[SourceSegment, ...]
    cells: tuple[TableCell, ...] = ()


def _join(pieces: Iterable[_Piece], separator: str = "\n") -> _Piece:
    parts: list[str] = []
    segments: list[SourceSegment] = []
    cells: list[TableCell] = []
    cursor = 0
    for piece in pieces:
        if parts:
            parts.append(separator)
            cursor += len(separator)
        parts.append(piece.text)
        segments.extend(
            replace(s, start=s.start + cursor, end=s.end + cursor) for s in piece.segments
        )
        cells.extend(piece.cells)
        cursor += len(piece.text)
    return _Piece("".join(parts), tuple(segments), tuple(cells))


def _slice(piece: _Piece, start: int, end: int, overlap_end: int = 0) -> _Piece:
    segments = []
    for s in piece.segments:
        a, b = max(start, s.start), min(end, s.end)
        if a >= b:
            continue
        ranges: tuple[tuple[int, int, Role], ...] = (
            (a, min(b, overlap_end), "overlap"),
            (max(a, overlap_end), b, s.role),
        )
        for x, y, role in ranges:
            if x < y:
                segments.append(
                    replace(
                        s,
                        start=x - start,
                        end=y - start,
                        source_start=s.source_start + x - s.start,
                        source_end=s.source_start + y - s.start,
                        role=role,
                    )
                )
    return _Piece(piece.text[start:end], tuple(segments), piece.cells)


def _segment(
    block: Block,
    index: int,
    text: str,
    *,
    row: int | None = None,
    column: int | None = None,
    role: Role = "content",
) -> SourceSegment:
    locator = block.locator
    if locator.kind == "xlsx" and column is not None and block.cells:
        reference = block.cells[column].reference
        locator = XlsxLocator(
            sheet=locator.sheet,
            kind="xlsx",
            cell_range=reference,
            headers=locator.headers,
            unit=locator.unit,
        )
    return SourceSegment(
        0,
        len(text),
        index,
        0,
        len(text),
        locator,
        role,
        row,
        column,
        block.source_part,
        block.source_path,
        block.bbox,
    )


def _row(block: Block, index: int, row: int, role: Role = "content") -> _Piece:
    # Empty cells must keep their TAB positions; no mapping needed for separators.
    segments = []
    cursor = 0
    for col, value in enumerate(block.rows[row]):
        if value:
            segments.append(
                replace(
                    _segment(block, index, value, row=row, column=col, role=role),
                    start=cursor,
                    end=cursor + len(value),
                )
            )
        cursor += len(value) + 1
    text = "\t".join(block.rows[row])
    return _Piece(text, tuple(segments), block.cells if row == 0 else ())


def _with_cell_policy(piece: _Piece) -> _Piece:
    notes = [
        f"{cell.reference}: number format {cell.number_format}"
        for cell in piece.cells
        if cell.value and cell.number_format not in {None, "General"}
    ]
    if any(cell.formula for cell in piece.cells):
        notes.append("Formula values are unverified stored caches; not recalculated.")
    return _join([piece, _Piece("\n".join(notes), ())]) if notes else piece


def _unit(block: Block) -> tuple[object, ...]:
    locator = block.locator
    position: object = None
    if locator.kind == "pdf":
        position = locator.page
    elif locator.kind == "pptx":
        position = (locator.slide, locator.shape)
    elif locator.kind == "xlsx":
        position = locator.sheet
    elif locator.kind == "image":
        position = locator.image_id
    return (
        locator.kind,
        position,
        block.heading_path,
        block.source_part,
        block.extraction_method,
        block.kind,
    )


class StructuralChunker:
    def __init__(self, tokenizer: EmbeddingTokenizer, profile: ChunkProfile | None = None) -> None:
        self.tokenizer = tokenizer
        self.profile = profile or ChunkProfile()

    def chunk(
        self,
        document: ParsedDocument,
        *,
        generation_id: UUID,
        extraction_fingerprint: str = "native-v1",
    ) -> tuple[Chunk, ...]:
        if document.quality == "partial":
            raise ChunkingError("partial_extraction")
        if not extraction_fingerprint or (
            document.ocr is not None and extraction_fingerprint == "native-v1"
        ):
            # Caller must include traineddata SHA/engine/DPI/order/Docling configuration.
            raise ChunkingError("missing_extraction_fingerprint")
        parsed = parsed_fingerprint(document)
        fingerprint = _hash(
            {
                "chunker": CHUNKER_REVISION,
                "profile": asdict(self.profile),
                "tokenizer": self.tokenizer.fingerprint,
                "parser": document.parser_revision,
                "extraction": extraction_fingerprint,
            }
        )
        chunks: list[Chunk] = []
        total_chars = 0
        for heading, piece in self._pieces(document):
            count = self.tokenizer.count(piece.text)
            if count > self.profile.max_tokens:
                raise ChunkingError("chunk_token_limit")
            total_chars += len(piece.text)
            if (
                len(chunks) >= self.profile.max_chunks
                or total_chars > self.profile.max_output_chars
            ):
                raise ChunkingError("chunk_output_limit")
            checksum = hashlib.sha256(piece.text.encode("utf-8")).hexdigest()
            ordinal = len(chunks)
            identity = _hash(
                {
                    "source": document.source.model_dump(mode="json"),
                    "generation": str(generation_id),
                    "pipeline": fingerprint,
                    "parsed": parsed,
                    "ordinal": ordinal,
                    "checksum": checksum,
                }
            )
            chunks.append(
                Chunk(
                    uuid5(CHUNK_NAMESPACE, identity),
                    document.source,
                    generation_id,
                    ordinal,
                    piece.text,
                    count,
                    checksum,
                    fingerprint,
                    parsed,
                    heading,
                    piece.segments,
                    piece.cells,
                )
            )
        if not chunks:
            raise ChunkingError("empty_chunks")
        return tuple(chunks)

    def _pieces(self, document: ParsedDocument) -> Iterable[tuple[tuple[str, ...], _Piece]]:
        blocks = document.blocks
        i = 0
        while i < len(blocks):
            block = blocks[i]
            if block.rows:
                indices = [i]
                # XLSX parser emits individual rows; group only adjacent rows in the same region.
                if block.locator.kind in {"xlsx", "csv"}:
                    while i + 1 < len(blocks) and self._adjacent_rows(blocks[i], blocks[i + 1]):
                        i += 1
                        indices.append(i)
                yield from ((block.heading_path, p) for p in self._tables(document, indices))
            else:
                group = [_Piece(block.text, (_segment(block, i, block.text),))]
                if block.kind == "paragraph":
                    while (
                        i + 1 < len(blocks)
                        and not blocks[i + 1].rows
                        and _unit(blocks[i + 1]) == _unit(block)
                    ):
                        i += 1
                        value = blocks[i]
                        group.append(_Piece(value.text, (_segment(value, i, value.text),)))
                separator = " " if block.extraction_method == "ocr" else "\n"
                combined = _join(group, separator)
                yield from ((block.heading_path, p) for p in self._windows(combined))
            i += 1

    @staticmethod
    def _adjacent_rows(left: Block, right: Block) -> bool:
        if left.locator.kind == "csv" and right.locator.kind == "csv":
            return bool(
                right.rows
                and _unit(left) == _unit(right)
                and left.table_headers == right.table_headers
                and left.locator.row_end + 1 == right.locator.row_start
            )
        if (
            not right.rows
            or right.locator.kind != "xlsx"
            or left.locator.kind != "xlsx"
            or _unit(left) != _unit(right)
            or left.table_headers != right.table_headers
        ):
            return False
        left_rows = re.findall(r"\d+", left.locator.cell_range)
        right_rows = re.findall(r"\d+", right.locator.cell_range)
        return int(right_rows[0]) == int(left_rows[-1]) + 1

    def _windows(self, piece: _Piece) -> Iterable[_Piece]:
        bounds = self.tokenizer.boundaries(piece.text)
        start = 0
        previous_end = 0
        while start < len(piece.text):
            first = bisect_right(bounds, start)
            candidates = bounds[first : first + self.profile.max_tokens]
            lo, hi = 0, len(candidates)
            while lo < hi:
                mid = (lo + hi) // 2
                if (
                    self.tokenizer.count(piece.text[start : candidates[mid]])
                    <= self.profile.max_tokens
                ):
                    lo = mid + 1
                else:
                    hi = mid
            if lo == 0:
                raise ChunkingError("token_span_too_large")
            end = candidates[lo - 1]
            # Prefer original paragraph/word boundaries whenever that advances the source.
            if end < len(piece.text):
                ends = [s.end for s in piece.segments if previous_end < s.end <= end]
                if ends:
                    end = max(ends)
            if end <= previous_end:
                raise ChunkingError("overlap_prevents_progress")
            yield _slice(piece, start, end, previous_end)
            if end == len(piece.text):
                return
            next_start = end
            # A suffix can retokenize differently: measure overlap on the exact original text.
            for candidate in reversed(bounds[first : bisect_right(bounds, end) - 1]):
                if (
                    self.tokenizer.count(piece.text[candidate:end], special_tokens=False)
                    > self.profile.overlap_tokens
                ):
                    break
                next_start = candidate
            previous_end, start = end, next_start

    def _headers(self, document: ParsedDocument, index: int) -> _Piece | None:
        block = document.blocks[index]
        if not block.table_headers:
            return None
        pieces = []
        if block.locator.kind == "csv":
            first = document.blocks[0]
            if (
                first.locator.kind != "csv"
                or first.locator.row_start != 1
                or first.rows != block.table_headers
            ):
                raise ChunkingError("unmapped_table_header")
            pieces.append(_row(first, 0, 0, "context"))
        elif block.locator.kind != "xlsx":
            for row, header in enumerate(block.table_headers):
                if row >= len(block.rows) or block.rows[row] != header:
                    raise ChunkingError("unmapped_table_header")
                pieces.append(_row(block, index, row, "context"))
        else:
            # Expanded merged header values refer back to actual stored anchor cells.
            region: list[tuple[int, Block]] = [(index, block)]
            for j in range(index - 1, -1, -1):
                candidate = document.blocks[j]
                if (
                    candidate.locator.kind != "xlsx"
                    or not candidate.rows
                    or candidate.locator.sheet != block.locator.sheet
                ):
                    break
                a = int(re.findall(r"\d+", candidate.locator.cell_range)[-1])
                next_locator = region[-1][1].locator
                assert next_locator.kind == "xlsx"
                b = int(re.findall(r"\d+", next_locator.cell_range)[0])
                if a + 1 != b:
                    break
                region.append((j, candidate))
            for header in block.table_headers:
                cells = []
                for column, value in enumerate(header):
                    if not value:
                        cells.append(_Piece("", ()))
                        continue
                    match: tuple[int, Block, int] | None = None
                    for j, candidate in reversed(region):
                        for col, actual in enumerate(candidate.rows[0]):
                            if actual == value and (
                                col == column
                                or (
                                    candidate.cells
                                    and candidate.cells[column].merged_origin
                                    == candidate.cells[col].reference
                                )
                            ):
                                match = (j, candidate, col)
                                break
                        if match:
                            break
                    if match is None:
                        raise ChunkingError("unmapped_table_header")
                    j, origin, col = match
                    cells.append(
                        _Piece(
                            value,
                            (_segment(origin, j, value, row=0, column=col, role="context"),),
                            (origin.cells[col],) if origin.cells else (),
                        )
                    )
                pieces.append(_join(cells, "\t"))
        return _with_cell_policy(_join(pieces))

    def _tables(self, document: ParsedDocument, indices: list[int]) -> Iterable[_Piece]:
        headers = self._headers(document, indices[0])
        if headers and self.tokenizer.count(headers.text) >= self.profile.max_tokens:
            raise ChunkingError("table_header_too_large")
        pending: list[_Piece] = []
        context = [headers] if headers else []
        for index in indices:
            block = document.blocks[index]
            header_count = 0
            for header in block.table_headers:
                if block.locator.kind == "csv" and block.locator.row_start != 1:
                    break
                if header_count < len(block.rows) and block.rows[header_count] == header:
                    header_count += 1
                else:
                    break
            for row in range(len(block.rows)):
                if row < header_count:
                    continue
                if block.locator.kind == "xlsx" and any(
                    len(header) == len(block.rows[row])
                    and all(
                        value == header[col]
                        or (not value and block.cells and block.cells[col].merged_origin)
                        for col, value in enumerate(block.rows[row])
                    )
                    for header in block.table_headers
                ):
                    continue
                piece = _row(block, index, row)
                # Preserve stored format/cache semantics as explicit nonquote metadata.
                piece = _with_cell_policy(piece)
                if self.tokenizer.count(_join([*context, piece]).text) > self.profile.max_tokens:
                    raise ChunkingError("table_row_too_large")
                candidate = _join([*context, *pending, piece])
                if pending and self.tokenizer.count(candidate.text) > self.profile.max_tokens:
                    yield _join([*context, *pending])
                    pending = []
                pending.append(piece)
        if pending:
            yield _join([*context, *pending])
        elif headers:
            yield headers
