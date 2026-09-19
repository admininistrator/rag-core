"""Validate shared metadata separately from future domain corpus validation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from common import CORPUS_ROOT, DOMAINS, CorpusError, check_url, read_json, safe_path

# The existing dev-only jsonschema package has no bundled typing stubs.
from jsonschema import Draft202012Validator, FormatChecker  # type: ignore[import-untyped]
from jsonschema.exceptions import ValidationError  # type: ignore[import-untyped]


def validate_schema(value: Any, schema_name: str) -> None:
    schema = read_json(CORPUS_ROOT / "schemas" / schema_name)
    Draft202012Validator.check_schema(schema)
    try:
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(value)
    except ValidationError as exc:
        location = "/".join(str(part) for part in exc.absolute_path) or "root"
        raise CorpusError(f"Schema violation at {location} ({exc.validator})") from None


def validate_manifest(value: Any) -> None:
    validate_schema(value, "domain-manifest.schema.json")


def validate_metadata(root: Path = CORPUS_ROOT) -> None:
    inventory = read_json(root / "source-license-inventory.json")
    validate_schema(inventory, "source-inventory.schema.json")
    aggregate = read_json(root / "manifest.json")
    validate_schema(aggregate, "root-manifest.schema.json")
    inventory_domains = {item["domain"]: item for item in inventory["datasets"]}
    if len(inventory_domains) != len(DOMAINS) or set(inventory_domains) != set(DOMAINS):
        raise CorpusError("Inventory must contain each corpus domain exactly once")
    for source in inventory_domains.values():
        identifiers = [item["id"] for item in source["sources"]]
        if len(identifiers) != len(set(identifiers)):
            raise CorpusError("Source IDs must be unique within a dataset")
        for item in source["sources"]:
            check_url(item["url"])
            if item["url"].startswith("https://raw.githubusercontent.com/"):
                prefix = f"https://raw.githubusercontent.com/{source['source_repository']}/{item['repository_commit']}/"
                if not item["url"].startswith(prefix) or not item["git_blob_sha1"]:
                    raise CorpusError(
                        "Git source URL must use its pinned repository commit and blob"
                    )
    for domain in DOMAINS:
        entry = aggregate["domains"][domain]
        if entry["manifest"] != f"{domain}/manifest.json":
            raise CorpusError("Aggregate domain points to the wrong manifest")
        manifest = read_json(safe_path(root, entry["manifest"], must_exist=True))
        validate_manifest(manifest)
        source = inventory_domains[domain]
        if (
            manifest["domain"] != domain
            or manifest["dataset"] != source["dataset"]
            or manifest["source_repository"] != source["source_repository"]
            or manifest["dataset_version"] != source["dataset_version"]
            or manifest["license"] != source["data_license"]
            or manifest["sources"] != source["sources"]
        ):
            raise CorpusError("Domain manifest provenance differs from inventory")
        for key in ("status", "document_count", "qa_count"):
            if entry[key] != manifest[key]:
                raise CorpusError("Aggregate status/count differs from domain manifest")
        artifact_paths = [item["path"] for item in manifest["artifacts"]]
        if len(artifact_paths) != len(set(artifact_paths)):
            raise CorpusError("Artifact receipts must have unique paths")
        if manifest["checksum"] != {item["path"]: item["sha256"] for item in manifest["artifacts"]}:
            raise CorpusError("Manifest checksum map differs from artifact receipts")
        for artifact in manifest["artifacts"]:
            # Receipts use domain-relative paths and explicitly separate data roles.
            reference = artifact["path"]
            if not reference.startswith(artifact["role"] + "/"):
                raise CorpusError("Artifact path does not match its data role")
            safe_path(root / domain, reference)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate corpus metadata or a prepared domain.")
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument(
        "--metadata-only",
        action="store_true",
        help="Check schemas/pins/manifest consistency; no corpus acceptance.",
    )
    selection.add_argument(
        "--all", action="store_true", help="Validate all prepared domains (pending T05-T08)."
    )
    selection.add_argument("--domain", choices=DOMAINS, help="Validate a prepared domain.")
    args = parser.parse_args(argv)
    try:
        validate_metadata()
        if args.metadata_only:
            print(
                "CORPUS METADATA: PASS - 3 domain manifests + inventory; corpus data NOT validated."
            )
            return 0
        selected = DOMAINS if args.all else (args.domain,)
        for domain in selected:
            manifest = read_json(CORPUS_ROOT / domain / "manifest.json")
            if manifest["status"] != "ready":
                raise CorpusError(
                    f"{domain}: corpus is {manifest['status']}; run domain setup after its implementation"
                )
            if domain == "bilingual":
                raise CorpusError(f"{domain}: domain validation pending its implementation")
        for domain in selected:
            if domain == "default":
                from prepare_default import validate_default

                report = validate_default(CORPUS_ROOT / domain)
                detail = (
                    f"documents={report['document_count']} QA={report['qa_count']} "
                    f"seed={report['seed']} source_sha256={report['source_sha256']}"
                )
            else:
                from prepare_document import validate_document

                report = validate_document(CORPUS_ROOT / domain)
                detail = (
                    f"PDFs={report['document_count']} QA={report['qa_count']} "
                    f"evidence={report['evidence_count']} "
                    f"page_indexing={report['page_indexing']} "
                    f"source_sha256={report['source_sha256']}"
                )
            print(f"CORPUS VALIDATION: PASS - {domain}; {detail}")
        return 0
    except (CorpusError, OSError) as exc:
        print(f"CORPUS VALIDATION: FAIL - {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
