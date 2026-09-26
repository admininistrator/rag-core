"""Record/check isolated corpus equality and rerun stability without exposing QA text."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from common import (
    CORPUS_ROOT,
    DOMAINS,
    CorpusError,
    read_json,
    read_jsonl,
    safe_path,
    sha256_file,
    write_json,
)
from corpus_root import output_root


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def snapshot(root: Path) -> dict[str, Any]:
    published = {}
    content = {}
    ids = {}
    counts = {}
    timestamps = {}
    paths = [root / "manifest.json", root / "source-license-inventory.json"]
    for domain in DOMAINS:
        directory = safe_path(root, domain)
        paths.extend(path for path in directory.rglob("*") if path.is_file())
        manifest = read_json(directory / "manifest.json")
        counts[domain] = [manifest["document_count"], manifest["qa_count"]]
        timestamps[domain] = manifest["downloaded_at"]
        for path in (directory / "qa").glob("*.jsonl"):
            if path.stem not in {"eval", "en_en", "vi_vi", "vi_en", "en_vi"}:
                continue  # Document indexes are hashed as content, not question IDs.
            identifiers = [item["id"] for item in read_jsonl(path)]
            if len(identifiers) != len(set(identifiers)):
                raise CorpusError("Duplicate QA IDs")
            ids[path.relative_to(root).as_posix()] = digest(identifiers)
    for path in sorted(paths):
        name = path.relative_to(root).as_posix()
        safe_path(root, name, must_exist=True)
        byte_hash = sha256_file(path)
        published[name] = [byte_hash, path.stat().st_mtime_ns, path.stat().st_size]
        if path.name == "manifest.json":
            value = read_json(path)
            value.pop("downloaded_at", None)
            content[name] = digest(value)
        else:
            content[name] = byte_hash
    cache = {}
    cache_root = safe_path(root, ".downloads")
    for path in sorted(cache_root.rglob("*")):
        name = path.relative_to(root).as_posix()
        safe_path(root, name)
        if path.is_file():
            cache[name] = [sha256_file(path), path.stat().st_mtime_ns, path.stat().st_size]
    return {"published": published, "content": content, "ids": ids, "counts": counts, "downloaded_at": timestamps, "cache": cache}


def compare_content(reference: dict[str, Any], candidate: dict[str, Any]) -> None:
    for key in ("content", "ids", "counts"):
        if reference[key] != candidate[key]:
            raise CorpusError(f"Reproduction differs from standard corpus: {key}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("record", "check"))
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args(argv)
    try:
        root = output_root(args.output_root)
        candidate = snapshot(root)
        compare_content(snapshot(CORPUS_ROOT), candidate)
        record = safe_path(root, ".verification.json")
        if args.mode == "record":
            if record.exists():
                raise CorpusError("Verification record already exists; do not overwrite baseline")
            write_json(record, candidate)
        elif read_json(record) != candidate:
            raise CorpusError("Rerun changed hashes, mtimes, IDs, counts or download timestamps")
        print(f"REPRODUCTION {args.mode}: PASS")
        print(f"published_files={len(candidate['published'])} cache_files={len(candidate['cache'])}")
        print(f"content_sha256={digest(candidate['content'])} IDs_sha256={digest(candidate['ids'])}")
        print(f"counts={candidate['counts']}")
        print(f"downloaded_at={candidate['downloaded_at']}")
        return 0
    except (CorpusError, OSError) as exc:
        print(f"REPRODUCTION: FAIL - {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
