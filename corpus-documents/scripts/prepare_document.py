"""Prepare the pinned open FinanceBench sample without altering its gold data."""

from __future__ import annotations

import json
import os
import re
import shutil
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from common import (
    CORPUS_ROOT,
    CorpusError,
    atomic_write,
    download,
    git_blob_file,
    read_json,
    read_jsonl,
    safe_path,
    sha256_file,
    validate_qa_records,
    write_json,
)
from pypdf import PdfReader
from pypdf.errors import DependencyError, PdfReadError

REVISION = "cc39aeb4afdf33909ee1412188bf89035950c2eb"
EXPECTED_QA_COUNT = 150
RAW_QA_PATH = "raw/financebench_open_source.jsonl"
RAW_METADATA_PATH = "raw/financebench_document_information.jsonl"
QA_PATH = "qa/eval.jsonl"
INDEX_PATH = "qa/documents.json"
REPORT_PATH = "qa/preparation.json"
PDF_URL_PREFIX = f"https://raw.githubusercontent.com/patronus-ai/financebench/{REVISION}/pdfs/"

_QA_KEYS = {
    "financebench_id",
    "company",
    "doc_name",
    "question_type",
    "question_reasoning",
    "domain_question_num",
    "question",
    "answer",
    "justification",
    "dataset_subset_label",
    "evidence",
}
_EVIDENCE_KEYS = {"evidence_text", "doc_name", "evidence_page_num", "evidence_text_full_page"}
_METADATA_KEYS = {"doc_name", "company", "gics_sector", "doc_type", "doc_period", "doc_link"}
_DOC_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def json_bytes(value: Any) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode(
            "utf-8"
        )
    except (TypeError, ValueError):
        raise CorpusError("FinanceBench value cannot be encoded as finite JSON") from None


def source_records(path: Path) -> list[dict[str, Any]]:
    records = list(read_jsonl(path))
    if len(records) != EXPECTED_QA_COUNT:
        raise CorpusError(f"Pinned FinanceBench source must contain {EXPECTED_QA_COUNT} open QA")
    identifiers: set[str] = set()
    for record in records:
        if set(record) != _QA_KEYS:
            raise CorpusError("FinanceBench QA fields differ from the pinned source contract")
        identifier = record["financebench_id"]
        doc_name = record["doc_name"]
        if (
            not _nonempty(identifier)
            or identifier in identifiers
            or not re.fullmatch(r"financebench_id_\d+", identifier)
        ):
            raise CorpusError("FinanceBench source ID must be unique and well formed")
        identifiers.add(identifier)
        if not _nonempty(doc_name) or not _DOC_NAME.fullmatch(doc_name):
            raise CorpusError("FinanceBench document name is unsafe or empty")
        for key in ("company", "question_type", "question", "answer"):
            if not _nonempty(record[key]):
                raise CorpusError(f"FinanceBench {key} must be a nonempty string")
        for key in ("question_reasoning", "justification"):
            if record[key] is not None and not _nonempty(record[key]):
                raise CorpusError(f"FinanceBench {key} must be null or a nonempty string")
        if record["dataset_subset_label"] != "OPEN_SOURCE":
            raise CorpusError("Closed FinanceBench records are not permitted")
        domain_number = record["domain_question_num"]
        if domain_number is not None and not _nonempty(domain_number):
            raise CorpusError("FinanceBench domain question number must be null or nonempty")
        evidence = record["evidence"]
        if not isinstance(evidence, list) or not evidence:
            raise CorpusError("FinanceBench evidence must be a nonempty list")
        for item in evidence:
            if not isinstance(item, dict) or set(item) != _EVIDENCE_KEYS:
                raise CorpusError("FinanceBench evidence fields differ from the pinned contract")
            if item["doc_name"] != doc_name:
                raise CorpusError("FinanceBench evidence maps ambiguously to another document")
            page = item["evidence_page_num"]
            if isinstance(page, bool) or not isinstance(page, int) or page < 0:
                raise CorpusError("FinanceBench evidence page must be a zero-based integer")
            if not _nonempty(item["evidence_text"]) or not _nonempty(
                item["evidence_text_full_page"]
            ):
                raise CorpusError("FinanceBench evidence text cannot be empty")
    return records


def metadata_records(path: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for record in read_jsonl(path):
        if set(record) != _METADATA_KEYS:
            raise CorpusError("FinanceBench metadata fields differ from the pinned contract")
        name = record["doc_name"]
        if not _nonempty(name) or not _DOC_NAME.fullmatch(name):
            raise CorpusError("FinanceBench metadata document names must be safe")
        for key in ("company", "gics_sector", "doc_type", "doc_link"):
            if not _nonempty(record[key]):
                raise CorpusError(f"FinanceBench metadata {key} must be nonempty")
        period = record["doc_period"]
        if isinstance(period, bool) or not isinstance(period, int) or period < 1900:
            raise CorpusError("FinanceBench metadata period is invalid")
        link = urlsplit(record["doc_link"])
        if link.scheme != "https" or not link.hostname or link.username or link.password:
            raise CorpusError("FinanceBench company document link must be public HTTPS metadata")
        if name in records:
            prior = records[name]
            duplicates = prior.setdefault("_duplicate_source_records", [dict(prior)])
            if not isinstance(duplicates, list):
                raise CorpusError("FinanceBench duplicate metadata tracking is invalid")
            duplicates.append(record)
        else:
            records[name] = record
    if not records:
        raise CorpusError("FinanceBench document metadata is empty")
    return records


def validate_qa_source(path: Path) -> None:
    source_records(path)


def validate_metadata_source(path: Path) -> None:
    metadata_records(path)


def referenced_documents(
    records: list[dict[str, Any]], metadata: dict[str, dict[str, Any]]
) -> list[str]:
    referenced = sorted({record["doc_name"] for record in records})
    missing = [name for name in referenced if name not in metadata]
    if missing:
        raise CorpusError("FinanceBench QA references document metadata that is missing")
    if any("_duplicate_source_records" in metadata[name] for name in referenced):
        raise CorpusError("FinanceBench QA maps to ambiguous duplicate document metadata")
    return referenced


def repository_pdf_url(doc_name: str) -> str:
    if not _DOC_NAME.fullmatch(doc_name):
        raise CorpusError("FinanceBench PDF name is unsafe")
    return PDF_URL_PREFIX + doc_name + ".pdf"


def pdf_page_count(path: Path) -> int:
    try:
        with path.open("rb") as stream:
            header = stream.read(5)
        if header != b"%PDF-":
            raise CorpusError("FinanceBench source document is not a PDF")
        reader = PdfReader(path, strict=False)
        count = len(reader.pages)
    except CorpusError:
        raise
    except (DependencyError, OSError, PdfReadError, ValueError):
        raise CorpusError("FinanceBench source document cannot be parsed as a PDF") from None
    if count <= 0:
        raise CorpusError("FinanceBench source PDF has no pages")
    return count


def validate_pdf(path: Path) -> None:
    pdf_page_count(path)


def build_artifacts(
    records: list[dict[str, Any]],
    metadata: dict[str, dict[str, Any]],
    pdfs: dict[str, dict[str, Any]],
    *,
    source_sha256: str,
    metadata_sha256: str,
) -> tuple[dict[str, bytes], dict[str, Any]]:
    names = referenced_documents(records, metadata)
    if set(pdfs) != set(names):
        raise CorpusError("Materialized FinanceBench PDFs differ from QA references")
    normalized: list[dict[str, Any]] = []
    for record in records:
        doc_name = record["doc_name"]
        page_count = pdfs[doc_name]["page_count"]
        evidence = []
        for item in record["evidence"]:
            page = item["evidence_page_num"]
            if page >= page_count:
                raise CorpusError(
                    f"FinanceBench evidence page is outside the real PDF: {doc_name} page {page}"
                )
            evidence.append(
                {
                    "document": item["doc_name"],
                    "page": page,
                    "text": item["evidence_text"],
                    "text_full_page": item["evidence_text_full_page"],
                }
            )
        normalized.append(
            {
                "id": "document_" + record["financebench_id"],
                "domain": "document",
                "source_id": record["financebench_id"],
                "question": record["question"],
                "expected_answers": [record["answer"]],
                "expected_documents": [doc_name],
                "evidence": evidence,
                "justification": record["justification"],
                "question_type": record["question_type"],
                "reasoning_type": record["question_reasoning"],
                "domain_question_num": record["domain_question_num"],
                "company": record["company"],
                "dataset_subset_label": record["dataset_subset_label"],
                "language": "en",
                "answerable": True,
                "source_dataset": "financebench",
            }
        )
    documents = []
    for name in names:
        item = metadata[name]
        pdf = pdfs[name]
        documents.append(
            {
                "document_id": name,
                "original_filename": name + ".pdf",
                "path": name + ".pdf",
                "company": item["company"],
                "gics_sector": item["gics_sector"],
                "doc_type": item["doc_type"],
                "doc_period": item["doc_period"],
                "source_company_link": item["doc_link"],
                "repository_pdf_url": repository_pdf_url(name),
                "sha256": pdf["sha256"],
                "bytes": pdf["bytes"],
                "page_count": pdf["page_count"],
            }
        )
    evidence_count = sum(len(record["evidence"]) for record in records)
    report = {
        "schema_version": 1,
        "source_revision": REVISION,
        "source_sha256": source_sha256,
        "metadata_sha256": metadata_sha256,
        "qa_count": len(normalized),
        "document_count": len(documents),
        "evidence_count": evidence_count,
        "page_indexing": "zero_based",
        "question_type_counts": _counts(record["question_type"] for record in records),
        "reasoning_type_counts": _counts(record["question_reasoning"] for record in records),
        "missing_justification_count": sum(
            record["justification"] is None for record in records
        ),
        "unreferenced_duplicate_metadata_names": sorted(
            name for name, item in metadata.items() if "_duplicate_source_records" in item
        ),
        "pdfs": [
            {
                "document_id": item["document_id"],
                "filename": item["original_filename"],
                "sha256": item["sha256"],
                "bytes": item["bytes"],
                "page_count": item["page_count"],
            }
            for item in documents
        ],
        "normalization_changes": (
            "Field names normalized only; every open-source QA, answer, evidence text, "
            "full-page evidence, zero-based page, justification, reasoning label, question "
            "type, company, document name, subset label, and domain question number is retained."
        ),
        "license_status": (
            "Local evaluation authorized by the project plan; GitHub QA/PDF redistribution "
            "applicability unresolved. Publisher card separately declares CC-BY-NC-4.0; "
            "company PDF rights remain separate."
        ),
        "attribution": "Islam et al. (2023), FinanceBench; source company metadata retained.",
    }
    contents = {
        QA_PATH: b"".join(
            (json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
            for record in normalized
        ),
        INDEX_PATH: json_bytes(documents),
        REPORT_PATH: json_bytes(report),
    }
    return contents, report


def _counts(values: Any) -> dict[str, int]:
    result: dict[str, int] = {}
    for value in values:
        label = "<null>" if value is None else str(value)
        result[label] = result.get(label, 0) + 1
    return dict(sorted(result.items()))


def _tree_files(root: Path) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for parent, directories, files in os.walk(root, followlinks=False):
        for name in directories + files:
            path = Path(parent) / name
            if path.is_symlink() or path.is_junction():
                raise CorpusError("Document corpus tree cannot contain links or junctions")
        for name in files:
            relative = (Path(parent) / name).relative_to(root).as_posix()
            result[relative] = safe_path(root, relative, must_exist=True)
    return result


def _pdf_details(domain_root: Path, names: list[str]) -> dict[str, dict[str, Any]]:
    result = {}
    for name in names:
        path = safe_path(domain_root, f"documents/{name}.pdf", must_exist=True)
        result[name] = {
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
            "page_count": pdf_page_count(path),
        }
    return result


def validate_document(domain_root: Path) -> dict[str, Any]:
    from validate_corpus import validate_manifest

    manifest = read_json(safe_path(domain_root, "manifest.json", must_exist=True))
    validate_manifest(manifest)
    if (
        manifest["domain"] != "document"
        or manifest["status"] != "ready"
        or manifest["page_indexing"] != "zero_based"
    ):
        raise CorpusError("document: corpus is not ready with zero-based pages")
    raw_qa = safe_path(domain_root, RAW_QA_PATH, must_exist=True)
    raw_metadata = safe_path(domain_root, RAW_METADATA_PATH, must_exist=True)
    for source, path in zip(manifest["sources"], (raw_qa, raw_metadata), strict=True):
        if (
            sha256_file(path) != source["expected_sha256"]
            or git_blob_file(path) != source["git_blob_sha1"]
        ):
            raise CorpusError("FinanceBench source bytes differ from the pinned source")
    records = source_records(raw_qa)
    metadata = metadata_records(raw_metadata)
    names = referenced_documents(records, metadata)
    pdfs = _pdf_details(domain_root, names)
    contents, report = build_artifacts(
        records,
        metadata,
        pdfs,
        source_sha256=sha256_file(raw_qa),
        metadata_sha256=sha256_file(raw_metadata),
    )
    if (
        manifest["qa_count"] != report["qa_count"]
        or manifest["document_count"] != report["document_count"]
    ):
        raise CorpusError("Document manifest counts differ from actual artifacts")
    expected_paths = {
        "manifest.json",
        RAW_QA_PATH,
        RAW_METADATA_PATH,
        *[f"documents/{name}.pdf" for name in names],
        *contents,
    }
    if set(_tree_files(domain_root)) != expected_paths:
        raise CorpusError("Document corpus has missing, duplicate, or unmanaged artifacts")
    for reference, expected_bytes in contents.items():
        if safe_path(domain_root, reference, must_exist=True).read_bytes() != expected_bytes:
            raise CorpusError(f"Document artifact differs from original source: {reference}")
    artifacts = manifest["artifacts"]
    if {item["path"] for item in artifacts} != expected_paths - {"manifest.json"}:
        raise CorpusError("Document receipts differ from the complete materialized corpus")
    actual_checksums = {}
    for artifact in artifacts:
        path = safe_path(domain_root, artifact["path"], must_exist=True)
        checksum = sha256_file(path)
        if (
            checksum != artifact["sha256"]
            or path.stat().st_size != artifact["bytes"]
            or not artifact["path"].startswith(artifact["role"] + "/")
        ):
            raise CorpusError("Document receipt hash, bytes, or role differs from actual file")
        actual_checksums[artifact["path"]] = checksum
    if manifest["checksum"] != actual_checksums:
        raise CorpusError("Document checksum map differs from actual artifacts")
    index = read_json(domain_root / INDEX_PATH)
    mapping = {item["document_id"]: item["path"] for item in index}
    validate_qa_records(read_jsonl(domain_root / QA_PATH), domain_root / "documents", mapping)
    return report


def _same_files(first: Path, second: Path) -> bool:
    old, new = _tree_files(first), _tree_files(second)
    return set(old) == set(new) and all(
        sha256_file(old[name]) == sha256_file(new[name]) for name in old
    )


def _publish(stage: Path, root: Path) -> None:
    proposed = stage / "document"
    current = safe_path(root, "document")
    aggregate = safe_path(root, "manifest.json", must_exist=True)
    if _same_files(current, proposed) and aggregate.read_bytes() == (stage / "manifest.json").read_bytes():
        return
    backup = stage / "previous-document"
    aggregate_backup = stage / "previous-aggregate.json"
    shutil.copy2(aggregate, aggregate_backup)
    moved_old = False
    moved_new = False
    try:
        os.replace(current, backup)
        moved_old = True
        os.replace(proposed, current)
        moved_new = True
        atomic_write(aggregate, [(stage / "manifest.json").read_bytes()])
    except BaseException:
        try:
            if moved_new:
                os.replace(current, proposed)
            if moved_old:
                os.replace(backup, current)
            os.replace(aggregate_backup, aggregate)
        except BaseException as rollback_error:
            raise CorpusError(
                f"Publication rollback failed; inspect retained recovery stage {stage}"
            ) from rollback_error
        raise


def _load_cache_receipt(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"revision": REVISION, "downloaded_at": None, "sources": {}, "pdfs": {}}
    value = read_json(path)
    if (
        not isinstance(value, dict)
        or value.get("revision") != REVISION
        or not isinstance(value.get("sources"), dict)
        or not isinstance(value.get("pdfs"), dict)
        or (value.get("downloaded_at") is not None and not _nonempty(value["downloaded_at"]))
    ):
        raise CorpusError("FinanceBench cache receipt is invalid")
    return value


def _cache_pin(entry: Any, url: str) -> str | None:
    if entry is None:
        return None
    if (
        not isinstance(entry, dict)
        or entry.get("url") != url
        or not re.fullmatch(r"[0-9a-f]{64}", entry.get("sha256", ""))
        or not isinstance(entry.get("bytes"), int)
        or entry["bytes"] <= 0
    ):
        raise CorpusError("FinanceBench cached source metadata is invalid")
    pin = entry["sha256"]
    if not isinstance(pin, str):
        raise CorpusError("FinanceBench cached source hash is invalid")
    return pin


def prepare_document(root: Path = CORPUS_ROOT) -> dict[str, Any]:
    from corpus_root import AGGREGATE_NOTES, preparation_manifest
    from validate_corpus import validate_metadata

    root = root.resolve(strict=True)
    cache = safe_path(root, ".downloads")
    cache.mkdir(exist_ok=True)
    lock = safe_path(root, ".downloads/document-setup.lock")
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise CorpusError("Document setup lock exists; inspect the active/stopped setup first") from None
    stage: Path | None = None
    succeeded = False
    try:
        validate_metadata(root)
        prior_root = safe_path(root, "document")
        prior, metadata_checkout = preparation_manifest(prior_root)
        prior_ready = prior["status"] == "ready"
        if prior_ready:
            validate_document(prior_root)
        elif not metadata_checkout and set(_tree_files(prior_root)) != {"manifest.json"}:
            raise CorpusError("Refuse to replace unrecognized existing document corpus files")
        stage = cache / ("document-stage-" + uuid.uuid4().hex)
        stage.mkdir()
        destination = stage / "document"
        destination.mkdir()
        (destination / "raw").mkdir()
        (destination / "documents").mkdir()
        (destination / "qa").mkdir()
        cache_receipt_path = safe_path(root, ".downloads/financebench-download.json")
        cache_receipt = _load_cache_receipt(cache_receipt_path)
        source_specs: list[tuple[dict[str, Any], str, str, Callable[[Path], None]]] = [
            (
                prior["sources"][0],
                RAW_QA_PATH,
                "financebench_open_source.jsonl",
                validate_qa_source,
            ),
            (
                prior["sources"][1],
                RAW_METADATA_PATH,
                "financebench_document_information.jsonl",
                validate_metadata_source,
            ),
        ]
        for source, relative, cache_name, validator in source_specs:
            cached = safe_path(root, ".downloads/" + cache_name)
            if prior_ready and not cached.is_file():
                shutil.copy2(safe_path(prior_root, relative, must_exist=True), cached)
            receipt = download(
                source["url"],
                cached,
                expected_sha256=source["expected_sha256"],
                expected_git_blob=source["git_blob_sha1"],
                validate=validator,
                timeout=30,
                attempts=2,
                max_bytes=4 * 1024 * 1024,
            )
            cache_receipt["sources"][source["id"]] = {
                "url": source["url"],
                "sha256": receipt.sha256,
                "bytes": receipt.byte_count,
            }
            shutil.copy2(cached, safe_path(destination, relative))
        records = source_records(destination / RAW_QA_PATH)
        metadata = metadata_records(destination / RAW_METADATA_PATH)
        names = referenced_documents(records, metadata)
        pdf_cache = safe_path(root, ".downloads/financebench-pdfs")
        pdf_cache.mkdir(exist_ok=True)
        pdfs: dict[str, dict[str, Any]] = {}
        for name in names:
            relative = f"documents/{name}.pdf"
            url = repository_pdf_url(name)
            cached = safe_path(pdf_cache, name + ".pdf")
            prior_pin = prior["checksum"].get(relative) if prior_ready else None
            cached_entry = cache_receipt["pdfs"].get(name)
            cached_pin = _cache_pin(cached_entry, url)
            if prior_ready and not cached.is_file():
                shutil.copy2(safe_path(prior_root, relative, must_exist=True), cached)
            receipt = download(
                url,
                cached,
                expected_sha256=prior_pin or cached_pin,
                validate=validate_pdf,
                timeout=60,
                attempts=2,
                max_bytes=32 * 1024 * 1024,
            )
            page_count = pdf_page_count(cached)
            downloaded_at = receipt.downloaded_at or (
                cached_entry.get("downloaded_at") if isinstance(cached_entry, dict) else None
            )
            if receipt.downloaded_at and cache_receipt["downloaded_at"] is None:
                cache_receipt["downloaded_at"] = receipt.downloaded_at
            cache_receipt["pdfs"][name] = {
                "url": url,
                "sha256": receipt.sha256,
                "bytes": receipt.byte_count,
                "page_count": page_count,
                "downloaded_at": downloaded_at,
            }
            write_json(cache_receipt_path, cache_receipt)
            shutil.copy2(cached, safe_path(destination, relative))
            pdfs[name] = {
                "sha256": receipt.sha256,
                "bytes": receipt.byte_count,
                "page_count": page_count,
            }
        contents, report = build_artifacts(
            records,
            metadata,
            pdfs,
            source_sha256=sha256_file(destination / RAW_QA_PATH),
            metadata_sha256=sha256_file(destination / RAW_METADATA_PATH),
        )
        for reference, content in contents.items():
            atomic_write(safe_path(destination, reference), [content])
        artifact_paths = sorted([RAW_QA_PATH, RAW_METADATA_PATH, *contents])
        artifact_paths += [f"documents/{name}.pdf" for name in names]
        artifacts = [
            {
                "path": reference,
                "role": reference.split("/", 1)[0],
                "sha256": sha256_file(safe_path(destination, reference, must_exist=True)),
                "bytes": safe_path(destination, reference, must_exist=True).stat().st_size,
            }
            for reference in sorted(artifact_paths)
        ]
        downloaded_at = (
            prior["downloaded_at"]
            or cache_receipt["downloaded_at"]
            or datetime.now(UTC).isoformat()
        )
        manifest = {
            **prior,
            "status": "ready",
            "downloaded_at": downloaded_at,
            "document_count": report["document_count"],
            "qa_count": report["qa_count"],
            "checksum": {item["path"]: item["sha256"] for item in artifacts},
            "artifacts": artifacts,
            "notes": (
                "Pinned official open-source FinanceBench QA/metadata and exactly the PDFs "
                "referenced by those QA. Gold answer/evidence/full-page text/justification and "
                "zero-based pages are unchanged; citation adapters convert to physical one-based. "
                "Raw/PDF/normalized QA bytes remain local and ignored because redistribution "
                "applicability is unresolved. See qa/preparation.json for measured hashes/counts."
            ),
        }
        write_json(destination / "manifest.json", manifest)
        aggregate = read_json(root / "manifest.json")
        aggregate["domains"]["document"] = {
            "manifest": "document/manifest.json",
            "status": "ready",
            "document_count": report["document_count"],
            "qa_count": report["qa_count"],
        }
        aggregate["notes"] = AGGREGATE_NOTES
        write_json(stage / "manifest.json", aggregate)
        shutil.copy2(root / "source-license-inventory.json", stage / "source-license-inventory.json")
        for domain in ("default", "bilingual"):
            (stage / domain).mkdir()
            shutil.copy2(root / domain / "manifest.json", stage / domain / "manifest.json")
        validate_metadata(stage)
        validate_document(destination)
        _publish(stage, root)
        succeeded = True
        return report
    finally:
        os.close(descriptor)
        lock.unlink()
        if succeeded and stage is not None:
            resolved = stage.resolve(strict=True)
            if not resolved.is_relative_to(cache.resolve(strict=True)) or not resolved.name.startswith(
                "document-stage-"
            ):
                raise CorpusError("Refuse to clean a staging path outside the corpus cache")
            shutil.rmtree(resolved)
