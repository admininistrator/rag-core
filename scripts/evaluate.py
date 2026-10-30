#!/usr/bin/env python3
"""RAG Core reproducible evaluation CLI harness.

Supports ingestion validation, retrieval evaluation, generation benchmark,
and gate reporting under anti-leakage invariants.
"""

import argparse
import sys
from pathlib import Path
from typing import Any

# Add src to sys.path so rag_core is importable directly
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from rag_core.evaluation.runner import EvaluationRunner  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="RAG Core Reproducible Evaluation Harness and Anti-Leakage Protocol",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=REPO_ROOT / "configs" / "evaluation.yaml",
        help="Path to evaluation configuration file",
    )
    parser.add_argument(
        "--domain",
        choices=["default", "document", "bilingual", "multilingual", "all"],
        default="all",
        help="Target domain to evaluate",
    )
    parser.add_argument(
        "--stage",
        choices=["ingest", "retrieval", "generation", "report", "all"],
        default="all",
        help="Evaluation pipeline stage to execute",
    )
    parser.add_argument(
        "--split",
        choices=["tuning", "held_out", "all"],
        default="all",
        help="Dataset split to evaluate (tuning, held_out, or all)",
    )
    parser.add_argument(
        "--mode",
        choices=["fixture", "service"],
        default="service",
        help="Evaluation mode: fixture (fast synthetic/mock) or service (live local stack)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "artifacts" / "eval",
        help="Directory where evaluation manifest and markdown report will be saved",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=None,
        help="Cap sample count per slice for quick testing",
    )
    return parser.parse_args()


def print_cli_summary(manifest: Any) -> None:
    print("=" * 80)
    print(f"RAG Core Evaluation Report (Mode: {manifest.mode})")
    print("=" * 80)
    print(f"Run ID:             {manifest.run_id}")
    print(f"Timestamp:          {manifest.timestamp}")
    print(f"Git Commit:         {manifest.git_commit}")
    print(f"Config Fingerprint: {manifest.config_fingerprint}")
    print("-" * 80)
    print("Gates Verification:")
    for g in manifest.gates:
        status_text = "PASS" if g.passed else "FAIL"
        print(f"  [{status_text}] {g.gate_name}: {g.actual} (Expected: {g.expected})")
    print("-" * 80)
    print("Domain Slices Summary:")
    for domain, slices in manifest.domains.items():
        print(f"  Domain: [{domain}]")
        for s in slices:
            gen_info = ""
            if s.generation:
                gen_info = f" | EM: {s.generation.exact_match:.2f} | F1: {s.generation.f1:.2f} | CitValid: {s.generation.citation_validity:.2f}"
            page_info = (
                f" | PageR@10: {s.retrieval_tuned.page_recall_at_10:.2f}"
                if s.retrieval_tuned.page_recall_at_10 is not None
                else ""
            )
            print(
                f"    - {s.slice_name} ({s.split}): "
                f"Tuned R@10: {s.retrieval_tuned.recall_at_10:.2f}{page_info} | "
                f"MRR: {s.retrieval_tuned.mrr:.2f}{gen_info}"
            )
    print("=" * 80)


def main() -> int:
    args = parse_args()

    try:
        runner = EvaluationRunner(config_path=args.config, mode=args.mode)
    except Exception as exc:
        print(f"Error initializing EvaluationRunner: {exc}", file=sys.stderr)
        return 1

    # Optional ingestion safety validation
    corpus_root = REPO_ROOT / "corpus-documents"
    if corpus_root.is_dir() and args.stage in ("ingest", "all"):
        try:
            runner.validate_ingestion_safety(corpus_root)
            print("Corpus ingestion safety check: PASS (No QA or ground truth leakage)")
        except Exception as exc:
            print(f"Ingestion safety validation failed: {exc}", file=sys.stderr)
            return 2

    # Execute benchmark
    try:
        manifest = runner.run_benchmark(
            domain_filter=args.domain,
            stage_filter=args.stage,
            split_filter=args.split,
            sample_size=args.sample_size,
        )
    except Exception as exc:
        print(f"Error during benchmark execution: {exc}", file=sys.stderr)
        return 3

    # Save reports
    manifest_path, report_path = runner.write_reports(manifest, output_dir=args.output_dir)

    print_cli_summary(manifest)
    print(f"Manifest written to: {manifest_path}")
    print(f"Report written to:   {report_path}")

    if manifest.passed_all_gates:
        print("Final Evaluation Status: ALL GATES PASSED")
        return 0
    else:
        print("Final Evaluation Status: ONE OR MORE GATES FAILED", file=sys.stderr)
        return 4


if __name__ == "__main__":
    sys.exit(main())
