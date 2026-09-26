"""Safe output roots and reconstruction of a checkout containing only metadata."""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
from typing import Any

from common import (
    CORPUS_ROOT,
    DOMAINS,
    CorpusError,
    atomic_write,
    read_json,
    safe_path,
    sha256_file,
    write_json,
)

AGGREGATE_NOTES = (
    "Per-domain status/counts describe validated local artifacts. "
    "Run setup_corpus.py --all and validate_corpus.py --all for complete corpus acceptance."
)


def output_root(value: str | None) -> Path:
    """CLI paths are cwd-relative; isolated outputs occupy a dedicated ignored namespace."""
    if value is None:
        return CORPUS_ROOT
    # Win32 abspath can erase trailing dots/spaces; reject before normalization.
    if any(part == ".." or part.endswith((".", " ")) for part in Path(value).parts):
        raise CorpusError("Output root cannot contain traversal or ambiguous Windows names")
    candidate = Path(os.path.abspath(value))
    try:
        relative = candidate.relative_to(CORPUS_ROOT)
    except ValueError:
        raise CorpusError("Output root must be below corpus-documents/.repro/<name>") from None
    if len(relative.parts) != 2 or relative.parts[0] != ".repro":
        raise CorpusError("Output root must be below corpus-documents/.repro/<name>")
    return safe_path(CORPUS_ROOT, relative.as_posix())


def empty_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        **manifest, "status": "not_downloaded", "downloaded_at": None,
        "document_count": None, "qa_count": None, "checksum": {}, "artifacts": [],
    }


def initialize_root(root: Path) -> None:
    """Copy only provenance into a new isolated root, never published payload/cache."""
    from validate_corpus import validate_metadata

    if root == CORPUS_ROOT or (root.exists() and any(root.iterdir())):
        validate_metadata(root)
        return
    validate_metadata(CORPUS_ROOT)
    aggregate = deepcopy(read_json(CORPUS_ROOT / "manifest.json"))
    manifests = {}
    for domain in DOMAINS:
        manifests[domain] = empty_manifest(read_json(CORPUS_ROOT / domain / "manifest.json"))
        aggregate["domains"][domain].update(
            status="not_downloaded", document_count=None, qa_count=None,
        )
    aggregate["notes"] = AGGREGATE_NOTES
    root.mkdir(parents=True, exist_ok=True)
    atomic_write(root / "source-license-inventory.json", [(CORPUS_ROOT / "source-license-inventory.json").read_bytes()])
    for domain, manifest in manifests.items():
        write_json(root / domain / "manifest.json", manifest)
    write_json(root / "manifest.json", aggregate)
    validate_metadata(root)


def preparation_manifest(domain_root: Path) -> tuple[dict[str, Any], bool]:
    """Permit tracked metadata-only clones; partial/corrupt local data still fails closed."""
    manifest = read_json(safe_path(domain_root, "manifest.json", must_exist=True))
    if manifest["status"] != "ready":
        return manifest, False
    if any((domain_root / name).exists() for name in ("raw", "documents")):
        return manifest, False
    for current, directories, files in os.walk(domain_root):
        for name in [*directories, *files]:
            path = Path(current) / name
            relative = path.relative_to(domain_root).as_posix()
            safe_path(domain_root, relative)
            if path.is_dir():
                if relative != "qa":
                    raise CorpusError("Unrecognized directory in metadata-only checkout")
            elif relative != "manifest.json" and (
                not relative.startswith("qa/")
                or manifest["checksum"].get(relative) != sha256_file(path)
            ):
                raise CorpusError("Unrecognized or modified file in metadata-only checkout")
    return empty_manifest(manifest), True


@contextmanager
def setup_lock(root: Path) -> Iterator[None]:
    cache = safe_path(root, ".downloads")
    cache.mkdir(exist_ok=True)
    lock = safe_path(root, ".downloads/corpus-setup.lock")
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise CorpusError("Corpus setup lock exists; inspect the active/stopped setup first") from None
    try:
        yield
    finally:
        os.close(descriptor)
        lock.unlink()


def print_summary(reports: dict[str, dict[str, Any]]) -> None:
    print("RAG Evaluation Corpus")
    for domain, report in reports.items():
        if domain == "default":
            print(f"Default / HotpotQA: documents={report['document_count']} QA={report['qa_count']}")
            print(f"  seed={report['seed']} distribution={report['selected_distribution']}")
        elif domain == "document":
            print(f"Document / FinanceBench: PDFs={report['document_count']} QA={report['qa_count']}")
            print(f"  evidence={report['evidence_count']} page_indexing={report['page_indexing']}")
        else:
            print(f"Bilingual / XQuAD: documents={report['paragraph_count_by_language']}")
            print(f"  QA_slices={report['qa_count_by_slice']} parallel_groups={report['parallel_group_count']}")
    print("Validation: PASS")
