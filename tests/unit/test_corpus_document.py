from __future__ import annotations

import hashlib
import io
import json
import shutil
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
from pypdf import PdfWriter

SCRIPTS = Path(__file__).resolve().parents[2] / "corpus-documents" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import common  # noqa: E402
import prepare_document as document  # noqa: E402
import validate_corpus  # noqa: E402

DOCS = ("ACME_2022_10K", "BETA_2023Q2_10Q")


def pdf_bytes(pages: int) -> bytes:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=612, height=792)
    stream = io.BytesIO()
    writer.write(stream)
    return stream.getvalue()


def qa_record(index: int) -> dict[str, Any]:
    name = DOCS[index % len(DOCS)]
    page = 2 if name == DOCS[0] else 3
    return {
        "financebench_id": f"financebench_id_{index:05d}",
        "company": "Acme Holdings" if name == DOCS[0] else "Beta Industries",
        "doc_name": name,
        "question_type": "metrics-generated" if index % 2 else "domain-relevant",
        "question_reasoning": None if index % 4 == 0 else "Information extraction",
        "domain_question_num": None if index % 2 else f"dg{index:03d}",
        "question": f"What is synthetic metric {index}?",
        "answer": f"Synthetic answer {index}",
        "justification": None if index % 3 == 0 else f"Synthetic justification {index}",
        "dataset_subset_label": "OPEN_SOURCE",
        "evidence": [
            {
                "evidence_text": f"Synthetic evidence {index}",
                "doc_name": name,
                "evidence_page_num": page,
                "evidence_text_full_page": f"Synthetic full page {index}",
            }
        ],
    }


def source_records() -> list[dict[str, Any]]:
    return [qa_record(index) for index in range(document.EXPECTED_QA_COUNT)]


def metadata() -> list[dict[str, Any]]:
    return [
        {
            "doc_name": name,
            "company": "Acme Holdings" if name == DOCS[0] else "Beta Industries",
            "gics_sector": "Industrials",
            "doc_type": "10k" if name == DOCS[0] else "10q",
            "doc_period": 2022 if name == DOCS[0] else 2023,
            "doc_link": f"https://example.com/{name}.pdf",
        }
        for name in DOCS
    ]


def jsonl_bytes(records: list[dict[str, Any]]) -> bytes:
    return b"".join(
        (json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
        for record in records
    )


def git_blob(body: bytes) -> str:
    digest = hashlib.sha1(usedforsecurity=False)
    digest.update(f"blob {len(body)}\0".encode())
    digest.update(body)
    return digest.hexdigest()


@pytest.fixture
def source_bodies() -> dict[str, bytes]:
    return {
        "financebench_open_source": jsonl_bytes(source_records()),
        "financebench_document_information": jsonl_bytes(metadata()),
        DOCS[0]: pdf_bytes(3),
        DOCS[1]: pdf_bytes(4),
    }


@pytest.fixture
def corpus_root(tmp_path: Path, source_bodies: dict[str, bytes]) -> Path:
    names = ["manifest.json", "source-license-inventory.json"]
    names += [f"{domain}/manifest.json" for domain in common.DOMAINS]
    for name in names:
        destination = tmp_path / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(common.CORPUS_ROOT / name, destination)
    manifest_path = tmp_path / "document/manifest.json"
    manifest = common.read_json(manifest_path)
    manifest.update(
        status="not_downloaded",
        downloaded_at=None,
        document_count=None,
        qa_count=None,
        checksum={},
        artifacts=[],
    )
    for source in manifest["sources"]:
        body = source_bodies[source["id"]]
        source["expected_sha256"] = hashlib.sha256(body).hexdigest()
        source["git_blob_sha1"] = git_blob(body)
    common.write_json(manifest_path, manifest)
    inventory_path = tmp_path / "source-license-inventory.json"
    inventory = common.read_json(inventory_path)
    entry = next(item for item in inventory["datasets"] if item["domain"] == "document")
    entry["sources"] = deepcopy(manifest["sources"])
    common.write_json(inventory_path, inventory)
    aggregate_path = tmp_path / "manifest.json"
    aggregate = common.read_json(aggregate_path)
    aggregate["domains"]["document"].update(
        status="not_downloaded", document_count=None, qa_count=None
    )
    common.write_json(aggregate_path, aggregate)
    return tmp_path


@pytest.fixture
def fake_download(
    monkeypatch: pytest.MonkeyPatch, source_bodies: dict[str, bytes]
) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []

    def injected(url: str, destination: Path, **options: Any) -> common.DownloadReceipt:
        if "financebench_open_source.jsonl" in url:
            key = "financebench_open_source"
        elif "financebench_document_information.jsonl" in url:
            key = "financebench_document_information"
        else:
            key = destination.stem
        body = source_bodies[key]
        checksum = hashlib.sha256(body).hexdigest()
        reused = destination.is_file() and destination.read_bytes() == body
        if options.get("expected_sha256") is not None:
            assert options["expected_sha256"] == checksum
        if options.get("expected_git_blob") is not None:
            assert options["expected_git_blob"] == git_blob(body)
        if not reused:
            common.atomic_write(destination, [body])
        validator = options.get("validate")
        if validator:
            validator(destination)
        calls.append({"url": url, "destination": destination, "reused": reused})
        return common.DownloadReceipt(
            url,
            checksum,
            len(body),
            None if reused else "2026-09-19T10:00:00+00:00",
            reused,
        )

    monkeypatch.setattr(document, "download", injected)
    return calls


def parsed_sources(tmp_path: Path) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    qa_path = tmp_path / "qa.jsonl"
    qa_path.write_bytes(jsonl_bytes(source_records()))
    metadata_path = tmp_path / "metadata.jsonl"
    metadata_path.write_bytes(jsonl_bytes(metadata()))
    return document.source_records(qa_path), document.metadata_records(metadata_path)


def test_normalization_preserves_gold_evidence_metadata_and_filename(tmp_path: Path) -> None:
    records, meta = parsed_sources(tmp_path)
    pdfs = {
        DOCS[0]: {"sha256": "1" * 64, "bytes": 100, "page_count": 3},
        DOCS[1]: {"sha256": "2" * 64, "bytes": 200, "page_count": 4},
    }
    contents, report = document.build_artifacts(
        records, meta, pdfs, source_sha256="3" * 64, metadata_sha256="4" * 64
    )
    normalized = [json.loads(line) for line in contents[document.QA_PATH].splitlines()]
    for original, result in zip(records, normalized, strict=True):
        assert result["source_id"] == original["financebench_id"]
        assert result["question"] == original["question"]
        assert result["expected_answers"] == [original["answer"]]
        assert result["expected_documents"] == [original["doc_name"]]
        assert result["justification"] == original["justification"]
        assert result["reasoning_type"] == original["question_reasoning"]
        assert result["domain_question_num"] == original["domain_question_num"]
        assert result["evidence"] == [
            {
                "document": item["doc_name"],
                "page": item["evidence_page_num"],
                "text": item["evidence_text"],
                "text_full_page": item["evidence_text_full_page"],
            }
            for item in original["evidence"]
        ]
    index = json.loads(contents[document.INDEX_PATH])
    assert {item["original_filename"] for item in index} == {f"{name}.pdf" for name in DOCS}
    assert all(item["path"] == item["original_filename"] for item in index)
    assert report["qa_count"] == 150 and report["document_count"] == 2
    assert report["page_indexing"] == "zero_based"


@pytest.mark.parametrize(
    "mutation",
    ["closed", "answer", "duplicate_id", "evidence_doc", "negative_page", "missing_field"],
)
def test_invalid_or_closed_source_is_refused(
    tmp_path: Path, mutation: str
) -> None:
    records = source_records()
    if mutation == "closed":
        records[0]["dataset_subset_label"] = "CLOSED_SOURCE"
    elif mutation == "answer":
        records[0]["answer"] = " "
    elif mutation == "duplicate_id":
        records[1]["financebench_id"] = records[0]["financebench_id"]
    elif mutation == "evidence_doc":
        records[0]["evidence"][0]["doc_name"] = DOCS[1]
    elif mutation == "negative_page":
        records[0]["evidence"][0]["evidence_page_num"] = -1
    else:
        del records[0]["justification"]
    path = tmp_path / "source.jsonl"
    path.write_bytes(jsonl_bytes(records))
    with pytest.raises(common.CorpusError):
        document.source_records(path)


def test_zero_based_last_page_is_valid_and_out_of_range_fails(tmp_path: Path) -> None:
    records, meta = parsed_sources(tmp_path)
    pdfs = {
        DOCS[0]: {"sha256": "1" * 64, "bytes": 100, "page_count": 3},
        DOCS[1]: {"sha256": "2" * 64, "bytes": 200, "page_count": 4},
    }
    document.build_artifacts(
        records, meta, pdfs, source_sha256="3" * 64, metadata_sha256="4" * 64
    )
    pdfs[DOCS[0]]["page_count"] = 2
    with pytest.raises(common.CorpusError, match="outside the real PDF"):
        document.build_artifacts(
            records, meta, pdfs, source_sha256="3" * 64, metadata_sha256="4" * 64
        )


def test_unreferenced_duplicate_metadata_is_reported_but_referenced_duplicate_fails(
    tmp_path: Path,
) -> None:
    records = metadata()
    unreferenced = {**records[0], "doc_name": "UNREFERENCED_2022_10K"}
    records.extend([unreferenced, {**unreferenced, "doc_period": 2021}])
    path = tmp_path / "metadata.jsonl"
    path.write_bytes(jsonl_bytes(records))
    parsed = document.metadata_records(path)
    assert "_duplicate_source_records" in parsed["UNREFERENCED_2022_10K"]
    assert document.referenced_documents(source_records(), parsed) == sorted(DOCS)
    records.append({**records[0], "doc_period": 2021})
    path.write_bytes(jsonl_bytes(records))
    with pytest.raises(common.CorpusError, match="ambiguous duplicate"):
        document.referenced_documents(source_records(), document.metadata_records(path))


def test_real_pdf_parser_counts_pages_and_refuses_non_pdf(tmp_path: Path) -> None:
    path = tmp_path / "source.pdf"
    path.write_bytes(pdf_bytes(3))
    assert document.pdf_page_count(path) == 3
    path.write_bytes(b"not a PDF")
    with pytest.raises(common.CorpusError, match="not a PDF"):
        document.pdf_page_count(path)


def published_hashes(root: Path) -> dict[str, str]:
    paths = [root / "manifest.json", *[p for p in (root / "document").rglob("*") if p.is_file()]]
    return {path.relative_to(root).as_posix(): common.sha256_file(path) for path in paths}


def test_prepare_validate_and_rerun_preserve_ids_hashes_mtimes_without_redownload(
    corpus_root: Path, fake_download: list[dict[str, Any]]
) -> None:
    report = document.prepare_document(corpus_root)
    before = published_hashes(corpus_root)
    mtimes = {name: (corpus_root / name).stat().st_mtime_ns for name in before}
    ids = [record["id"] for record in common.read_jsonl(corpus_root / "document/qa/eval.jsonl")]
    timestamp = common.read_json(corpus_root / "document/manifest.json")["downloaded_at"]
    assert report == document.validate_document(corpus_root / "document")
    validate_corpus.validate_metadata(corpus_root)
    first_calls = len(fake_download)
    assert first_calls == 4 and all(not call["reused"] for call in fake_download)
    assert document.prepare_document(corpus_root) == report
    assert published_hashes(corpus_root) == before
    assert {name: (corpus_root / name).stat().st_mtime_ns for name in before} == mtimes
    assert [
        record["id"] for record in common.read_jsonl(corpus_root / "document/qa/eval.jsonl")
    ] == ids
    assert common.read_json(corpus_root / "document/manifest.json")["downloaded_at"] == timestamp
    assert len(fake_download) == first_calls * 2
    assert all(call["reused"] for call in fake_download[first_calls:])
    assert {path.name for path in (corpus_root / ".downloads/financebench-pdfs").iterdir()} == {
        f"{name}.pdf" for name in DOCS
    }


@pytest.mark.parametrize("corruption", ["gold", "evidence", "page", "pdf", "receipt", "extra"])
def test_validator_refuses_gold_evidence_page_pdf_receipt_or_extra_file(
    corpus_root: Path, fake_download: list[dict[str, Any]], corruption: str
) -> None:
    document.prepare_document(corpus_root)
    domain = corpus_root / "document"
    if corruption in {"gold", "evidence", "page"}:
        records = list(common.read_jsonl(domain / document.QA_PATH))
        if corruption == "gold":
            records[0]["expected_answers"] = ["Altered answer"]
        elif corruption == "evidence":
            records[0]["evidence"][0]["text"] = "Altered evidence"
        else:
            records[0]["evidence"][0]["page"] = 999
        (domain / document.QA_PATH).write_bytes(jsonl_bytes(records))
    elif corruption == "pdf":
        (domain / f"documents/{DOCS[0]}.pdf").write_bytes(b"corrupted")
    elif corruption == "receipt":
        manifest = common.read_json(domain / "manifest.json")
        manifest["artifacts"][0]["bytes"] += 1
        common.write_json(domain / "manifest.json", manifest)
    else:
        (domain / "documents/extra.pdf").write_bytes(pdf_bytes(1))
    with pytest.raises(common.CorpusError):
        document.validate_document(domain)


def test_unrecognized_file_and_existing_lock_preserve_prior_tree(
    corpus_root: Path, fake_download: list[dict[str, Any]]
) -> None:
    personal = corpus_root / "document/user-file.txt"
    personal.write_text("user owned", encoding="utf-8")
    with pytest.raises(common.CorpusError, match="unrecognized"):
        document.prepare_document(corpus_root)
    assert personal.read_text(encoding="utf-8") == "user owned" and fake_download == []
    personal.unlink()
    cache = corpus_root / ".downloads"
    cache.mkdir(exist_ok=True)
    lock = cache / "document-setup.lock"
    lock.write_text("another writer", encoding="utf-8")
    before = published_hashes(corpus_root)
    with pytest.raises(common.CorpusError, match="lock"):
        document.prepare_document(corpus_root)
    assert published_hashes(corpus_root) == before and fake_download == []
    assert lock.read_text(encoding="utf-8") == "another writer"


def test_publication_failure_preserves_previous_manifest_and_tree(
    corpus_root: Path,
    fake_download: list[dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = published_hashes(corpus_root)
    original_write = document.atomic_write

    def fail_aggregate(destination: Path, chunks: Any, **options: Any) -> bool:
        if destination == corpus_root / "manifest.json":
            raise OSError("Synthetic aggregate publication failure")
        return original_write(destination, chunks, **options)

    monkeypatch.setattr(document, "atomic_write", fail_aggregate)
    with pytest.raises(OSError, match="aggregate"):
        document.prepare_document(corpus_root)
    assert published_hashes(corpus_root) == before
    assert not (corpus_root / ".downloads/document-setup.lock").exists()
