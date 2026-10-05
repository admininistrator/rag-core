"""Conflict-policy risk cases: exact claims, qualifiers, units, locale and source roles."""

from dataclasses import replace
from uuid import uuid4

import pytest

from rag_core.domain.documents import TableCell
from rag_core.domain.evidence_conflicts import numeric_conflicts
from tests.unit.test_evidence_policy import setup

pytestmark = pytest.mark.unit


def statements(*texts):
    _, _, _, collaborators = setup()
    base = collaborators.chunks
    return tuple(
        replace(
            base[i % 2],
            text=text,
            segments=(
                replace(base[i % 2].segments[0], start=0, end=len(text), source_end=len(text)),
            ),
        )
        for i, text in enumerate(texts)
    )


@pytest.mark.parametrize(
    "left,right,conflict",
    [
        (
            "Acme revenue in 2025: 12.5 million USD.",
            "Acme revenue in 2025: 14.5 million USD.",
            True,
        ),
        (
            "Acme revenue in 2025: 12.5 million USD.",
            "Acme revenue in 2024: 14.5 million USD.",
            False,
        ),
        (
            "Acme revenue in 2025: 12.5 million USD.",
            "Beta revenue in 2025: 14.5 million USD.",
            False,
        ),
        (
            "Acme revenue in 2025: 12.5 million USD.",
            "Acme profit in 2025: 14.5 million USD.",
            False,
        ),
        (
            "Acme revenue in 2025: 12.5 million USD.",
            "Acme revenue in 2025: 12.50 million USD.",
            False,
        ),
        (
            "Acme revenue in 2025: 12.5 million USD.",
            "Acme revenue in 2025: 12,5 million USD.",
            False,
        ),
        (
            "Acme revenue in 2025: 12.5 million USD.",
            "Acme revenue in 2025: 14.5 million VND.",
            False,
        ),
        ("Acme revenue: 1,234 USD.", "Acme revenue: 1,235 USD.", False),
        ("Acme revenue: 1.234 USD.", "Acme revenue: 1.235 USD.", False),
        ("Acme revenue: 12 500 USD.", "Acme revenue: 12 600 USD.", False),
        ("12.5 USD.", "14.5 USD.", False),
        ("Acme revenue: 12.5.", "Acme revenue: 14.5.", False),
        (
            "Doanh thu Acme năm 2025: 12,5 triệu USD.",
            "Doanh thu Acme năm 2025: 14,5 triệu USD.",
            True,
        ),
        ("Acme margin: -12.5 percent.", "Acme margin: 12.5 percent.", True),
        ("Acme revenue: 12.5 USD (estimated).", "Acme revenue: 14.5 USD (audited).", False),
        ("Acme revenue: 12.5 million USD.", "Acme revenue: 12500000 USD.", False),
    ],
)
def test_same_claim_only_and_no_ambiguous_locale_guess(left, right, conflict):
    assert bool(numeric_conflicts(statements(left, right))) is conflict


def test_conflict_within_one_chunk_and_source_metadata_is_excluded():
    chunk = statements("Acme revenue: 12.5 USD. Acme revenue: 14.5 USD.")[0]
    assert numeric_conflicts((chunk,))[0].first == numeric_conflicts((chunk,))[0].second == chunk.id
    left, right = statements("Acme revenue: 12.5 USD.", "Acme revenue: 14.5 USD.")
    unmapped = replace(right, segments=())
    metadata = replace(right, segments=(replace(right.segments[0], role="metadata"),))
    assert not numeric_conflicts((left, unmapped)) and not numeric_conflicts((left, metadata))


def test_different_headings_do_not_conflate_subject_context():
    left, right = statements("Revenue: 12.5 USD.", "Revenue: 14.5 USD.")
    assert not numeric_conflicts(
        (replace(left, heading_path=("Acme",)), replace(right, heading_path=("Beta",)))
    )


def table(amount, *, subject="Acme", year="2025", header="Revenue (million USD)"):
    chunk = statements("placeholder")[0]
    headers = ("Company", "Year", header)
    rows = (headers, (subject, year, amount))
    segments = []
    cursor = 0
    for row, values in enumerate(rows):
        for column, value in enumerate(values):
            if value:
                segments.append(
                    replace(
                        chunk.segments[0],
                        start=cursor,
                        end=cursor + len(value),
                        source_start=0,
                        source_end=len(value),
                        block_index=row,
                        row=0,
                        column=column,
                        role="context" if row == 0 else "content",
                    )
                )
            cursor += len(value) + 1
    return replace(chunk, text="\n".join("\t".join(row) for row in rows), segments=tuple(segments))


def test_table_dimensions_units_subject_and_unverified_caches():
    first = table("12.5")
    second = replace(table("14.5"), id=uuid4())
    assert numeric_conflicts((first, second))
    for other in (
        table("14.5", year="2024"),
        table("14.5", subject="Beta"),
        table("14.5", header="Revenue (million VND)"),
        table("14.5", subject=""),
        table("14.5", header="Revenue"),
    ):
        assert not numeric_conflicts((first, other))
    cached = replace(
        second,
        cells=(
            TableCell(reference="C2", value="14.5", formula="=X1", value_origin="formula_cache"),
        ),
    )
    assert not numeric_conflicts((first, cached))
