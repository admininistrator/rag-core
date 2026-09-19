"""Corpus setup entry point. Domain implementations are added sequentially in T05-T07."""

from __future__ import annotations

import argparse
import sys

from common import DOMAINS, CorpusError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Reproduce official RAG evaluation corpus (default/document implemented)."
    )
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument(
        "--all", action="store_true", help="Prepare all domains (complete in T08)."
    )
    selection.add_argument("--domain", choices=DOMAINS, help="Prepare one corpus domain.")
    args = parser.parse_args(argv)
    selected = DOMAINS if args.all else (args.domain,)
    unavailable = [domain for domain in selected if domain == "bilingual"]
    # Preflight every requested domain before any download or mutation. No success stubs.
    if unavailable:
        print(
            "CORPUS SETUP: UNAVAILABLE - domain preparation not implemented: "
            + ", ".join(unavailable)
            + ". Required task: T07 (bilingual); full acceptance T08.",
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
        else:
            from prepare_document import prepare_document

            report = prepare_document()
            detail = (
                f"document/FinanceBench; PDFs={report['document_count']} "
                f"QA={report['qa_count']} evidence={report['evidence_count']} "
                f"page_indexing={report['page_indexing']} source_sha256={report['source_sha256']}"
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
