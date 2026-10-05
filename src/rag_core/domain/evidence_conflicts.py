"""Conservative numeric claims; no semantic entailment, translation or unit conversion.

Only mapped source text participates. Exact normalized statement skeletons retain
subjects, metrics, dates and qualifiers. Tables retain headers and row dimensions.
This bounded baseline is deliberately narrower than general contradiction detection.
"""

import re
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from rag_core.domain.chunking import Chunk

_NUMBER = r"[+-]?\d+(?:[.,]\d+)?"
_UNIT = r"(?:(?:million|billion|triệu|tỷ)\s+)?(?:USD|VND|EUR|GBP)|kg|km|percent|%"
_QUANTITY = re.compile(rf"(?<![\w.,])(?P<value>{_NUMBER})\s*(?P<unit>{_UNIT})(?!\w)", re.I)
_UNIT_ONLY = re.compile(rf"(?<!\w)(?:{_UNIT})(?!\w)", re.I)
_SENTENCES = re.compile(r"[!?;\n]|\.(?=\s|$)")


def _normalize(value: str) -> str:
    return " ".join(value.casefold().split())


def _decimal(value: str) -> Decimal | None:
    if not re.fullmatch(_NUMBER, value):
        return None
    # 1,234 / 1.234 can denote a decimal or grouped thousands. Do not guess locale.
    if re.search(r"[.,]\d{3}$", value):
        return None
    return Decimal(value.replace(",", "."))


@dataclass(frozen=True)
class NumericConflict:
    first: UUID
    second: UUID


def _claims(chunk: Chunk) -> list[tuple[tuple[object, ...], Decimal]]:
    claims: list[tuple[tuple[object, ...], Decimal]] = []
    paragraphs: dict[int, list[tuple[int, str]]] = defaultdict(list)
    headers: dict[int, str] = {}
    rows: dict[tuple[int, int], dict[int, str]] = defaultdict(dict)
    ambiguous_headers = False
    for segment in chunk.segments:
        if segment.role == "metadata":
            continue
        value = chunk.text[segment.start : segment.end]
        if segment.row is None:
            paragraphs[segment.block_index].append((segment.start, value))
        elif segment.column is not None:
            if segment.role == "context":
                previous = headers.get(segment.column)
                if previous is not None and previous != value:
                    ambiguous_headers = True  # multi-level headers require richer interpretation
                headers[segment.column] = value
            else:
                rows[(segment.block_index, segment.row)][segment.column] = value
    for pieces in paragraphs.values():
        for statement in _SENTENCES.split("".join(v for _, v in sorted(pieces))):
            for match in _QUANTITY.finditer(statement):
                amount = _decimal(match["value"])
                # A bare quantity has no subject/metric; never compare it across sources.
                label = statement[: match.start()].strip()
                if (
                    amount is None
                    or not re.search(r"[^\W\d_]", label)
                    or re.search(r"\d\s+$", statement[: match.start()])
                ):
                    continue
                skeleton = _normalize(
                    statement[: match.start("value")] + "<value>" + statement[match.end("value") :]
                )
                claims.append((("statement", chunk.heading_path, skeleton), amount))
    # Stored formula caches are unverified; do not infer arithmetic or semantic validity.
    if ambiguous_headers or any(c.value_origin != "stored" for c in chunk.cells):
        return claims
    for row in rows.values():
        for column, header in headers.items():
            unit = _UNIT_ONLY.search(header)
            amount = _decimal(row.get(column, "").strip())
            dimensions = tuple(
                (i, _normalize(row.get(i, ""))) for i in sorted(headers) if i != column
            )
            subject = any(re.search(r"[^\W\d_]", value) for _, value in dimensions)
            if unit is not None and amount is not None and subject:
                claims.append(
                    (
                        (
                            "table",
                            chunk.heading_path,
                            tuple((i, _normalize(v)) for i, v in sorted(headers.items())),
                            column,
                            _normalize(unit[0]),
                            dimensions,
                        ),
                        amount,
                    )
                )
    return claims


def numeric_conflicts(chunks: tuple[Chunk, ...]) -> tuple[NumericConflict, ...]:
    """Return one private opposing pair per exact claim key; never log labels/text/IDs."""
    first: dict[tuple[object, ...], tuple[Decimal, UUID]] = {}
    conflicting: dict[tuple[object, ...], NumericConflict] = {}
    for chunk in chunks:
        for key, amount in _claims(chunk):
            previous = first.setdefault(key, (amount, chunk.id))
            if previous[0] != amount and key not in conflicting:
                conflicting[key] = NumericConflict(previous[1], chunk.id)
    return tuple(conflicting.values())
