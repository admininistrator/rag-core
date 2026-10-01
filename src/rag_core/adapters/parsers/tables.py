"""Lossless cell text normalization shared across format adapters."""

from collections.abc import Iterable


def table_rows(rows: Iterable[Iterable[str]]) -> tuple[tuple[str, ...], ...]:
    # Keep empty cells, embedded newlines, Unicode, headers and units verbatim.
    return tuple(tuple(row) for row in rows)


def table_text(rows: Iterable[Iterable[str]]) -> str:
    return "\n".join("\t".join(row) for row in rows)
