"""Reproduce and validate the pinned evaluation corpus without model dependencies."""
from __future__ import annotations

import argparse
import sys

from common import DOMAINS, CorpusError
from corpus_root import initialize_root, output_root, print_summary, setup_lock


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reproduce the pinned RAG evaluation corpus.")
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--all", action="store_true", help="Prepare and validate all domains.")
    selection.add_argument("--domain", choices=DOMAINS, help="Prepare one corpus domain.")
    parser.add_argument("--output-root", help="Isolated output: corpus-documents/.repro/<name> (cwd-relative or absolute).")
    args = parser.parse_args(argv)
    try:
        from prepare_bilingual import prepare_bilingual
        from prepare_default import prepare_default
        from prepare_document import prepare_document
        from validate_corpus import validate_data

        root = output_root(args.output_root)
        initialize_root(root)
        selected = DOMAINS if args.all else (args.domain,)
        prepare = {"default": prepare_default, "document": prepare_document, "bilingual": prepare_bilingual}
        with setup_lock(root):
            for domain in selected:
                print(f"Preparing {domain}...", flush=True)
                prepare[domain](root)
            reports = validate_data(root, selected)
        print_summary(reports)
        print("CORPUS SETUP: PASS")
        return 0
    except (CorpusError, OSError) as exc:
        print(f"CORPUS SETUP: FAIL - {exc}; no data acceptance", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
