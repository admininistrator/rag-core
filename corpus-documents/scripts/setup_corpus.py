"""Corpus setup entry point. Domain implementations are added sequentially in T05-T07."""

from __future__ import annotations

import argparse
import sys

from common import DOMAINS


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Reproduce official RAG evaluation corpus (domain preparation pending T05-T07)."
    )
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument(
        "--all", action="store_true", help="Prepare all domains (complete in T08)."
    )
    selection.add_argument("--domain", choices=DOMAINS, help="Prepare one corpus domain.")
    args = parser.parse_args(argv)
    selected = DOMAINS if args.all else (args.domain,)
    # Preflight every requested domain before any download or mutation. No success stubs.
    print(
        "CORPUS SETUP: UNAVAILABLE - domain preparation not implemented: "
        + ", ".join(selected)
        + ". Required tasks: T05 (default), T06 (document), T07 (bilingual); full acceptance T08.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
