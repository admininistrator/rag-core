"""Corpus setup entry point for supported individual domains; --all is reserved for T08."""

from __future__ import annotations

import argparse
import sys

from common import DOMAINS, CorpusError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Reproduce official RAG evaluation corpus (individual domains; --all belongs to T08)."
    )
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument(
        "--all", action="store_true", help="Prepare all domains (complete in T08)."
    )
    selection.add_argument("--domain", choices=DOMAINS, help="Prepare one corpus domain.")
    args = parser.parse_args(argv)
    if args.all:
        print(
            "CORPUS SETUP: UNAVAILABLE - --all setup and acceptance are reserved for T08.",
            file=sys.stderr,
        )
        return 2
    try:
        if args.domain == "default":
            from prepare_default import prepare_default

            report = prepare_default()
            detail = (
                f"default/HotpotQA; documents={report['document_count']} "
                f"QA={report['qa_count']} seed={report['seed']} "
                f"source_sha256={report['source_sha256']}"
            )
        elif args.domain == "document":
            from prepare_document import prepare_document

            report = prepare_document()
            detail = (
                f"document/FinanceBench; PDFs={report['document_count']} "
                f"QA={report['qa_count']} evidence={report['evidence_count']} "
                f"page_indexing={report['page_indexing']} source_sha256={report['source_sha256']}"
            )
        else:
            from prepare_bilingual import prepare_bilingual

            report = prepare_bilingual()
            detail = (
                f"bilingual/XQuAD; documents={report['paragraph_count_by_language']} "
                f"QA_slices={report['qa_count_by_slice']} "
                f"parallel_groups={report['parallel_group_count']}"
            )
    except (CorpusError, OSError) as exc:
        print(f"CORPUS SETUP: FAIL - {args.domain}: {exc}; no data acceptance", file=sys.stderr)
        return 1
    print("CORPUS SETUP: PASS - " + detail)
    if args.domain == "default":
        print("Selected distribution: " + str(report["selected_distribution"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
