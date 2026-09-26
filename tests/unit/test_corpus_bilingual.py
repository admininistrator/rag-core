from __future__ import annotations

import hashlib
import json
import shutil
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "corpus-documents" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import common  # noqa: E402
import corpus_root as roots  # noqa: E402
import prepare_bilingual as bilingual  # noqa: E402
import setup_corpus  # noqa: E402
import validate_corpus  # noqa: E402

pytestmark = pytest.mark.unit


def source(language: str, *, reverse: bool = False) -> dict[str, Any]:
    def qa(identifier: str, question: str, answer: str, context: str) -> dict[str, Any]:
        return {
            "id": identifier,
            "question": question,
            "answers": [{"text": answer, "answer_start": context.index(answer)}],
        }

    records = [
        {
            "title": "Article A",
            "paragraphs": [
                {
                    "context": f"Answer in {language}. Second answer in {language}.",
                    "qas": [
                        qa(
                            "qa-1",
                            f"Question in {language}?",
                            f"Answer in {language}",
                            f"Answer in {language}. Second answer in {language}.",
                        ),
                        qa(
                            "qa-2",
                            f"Second question in {language}?",
                            f"Second answer in {language}",
                            f"Answer in {language}. Second answer in {language}.",
                        ),
                    ],
                },
                {
                    "context": f"Third answer in {language}.",
                    "qas": [
                        qa(
                            "qa-3",
                            f"Third question in {language}?",
                            f"Third answer in {language}",
                            f"Third answer in {language}.",
                        ),
                    ],
                },
            ],
        },
        {
            "title": "Article B",
            "paragraphs": [
                {
                    "context": f"Fourth answer in {language}.",
                    "qas": [
                        qa(
                            "qa-4",
                            f"Fourth question in {language}?",
                            f"Fourth answer in {language}",
                            f"Fourth answer in {language}.",
                        ),
                    ],
                }
            ],
        },
    ]
    if reverse:
        records.reverse()
        for item in records:
            item["paragraphs"].reverse()
    return {"version": "1.1", "data": records}


def test_alignment_uses_title_and_qa_ids_not_array_position() -> None:
    english = bilingual.source_records(source("en"), "en")
    vietnamese = bilingual.source_records(source("vi", reverse=True), "vi")
    groups = bilingual.align_paragraphs(english, vietnamese)
    assert len(groups) == 3
    assert {group["parallel_group_id"] for group in groups} == {
        bilingual.parallel_group_id("Article A", ["qa-1", "qa-2"]),
        bilingual.parallel_group_id("Article A", ["qa-3"]),
        bilingual.parallel_group_id("Article B", ["qa-4"]),
    }


def test_alignment_rejects_missing_qa_counterpart_and_title_mismatch() -> None:
    english = bilingual.source_records(source("en"), "en")
    missing = source("vi")
    missing["data"][0]["paragraphs"][0]["qas"].pop()
    with pytest.raises(common.CorpusError, match="QA ID"):
        bilingual.align_paragraphs(english, bilingual.source_records(missing, "vi"))
    changed_title = source("vi")
    changed_title["data"][0]["title"] = "Different article"
    with pytest.raises(common.CorpusError, match="title"):
        bilingual.align_paragraphs(english, bilingual.source_records(changed_title, "vi"))


def test_four_slices_use_full_parallel_qa_and_counterpart_gold() -> None:
    english = bilingual.source_records(source("en"), "en")
    vietnamese = bilingual.source_records(source("vi"), "vi")
    groups = bilingual.align_paragraphs(english, vietnamese)
    contents, report = bilingual.build_artifacts(
        english, vietnamese, groups, source_hashes={"en": "a" * 64, "vi": "b" * 64}
    )
    rows = {
        name: [json.loads(line) for line in contents[f"qa/{name}.jsonl"].splitlines()]
        for name in bilingual.SLICES
    }
    assert {name: len(items) for name, items in rows.items()} == {
        "en_en": 4,
        "vi_vi": 4,
        "vi_en": 4,
        "en_vi": 4,
    }
    for key in ("en_en", "vi_vi", "vi_en", "en_vi"):
        assert [record["source_qa_id"] for record in rows[key]] == ["qa-1", "qa-2", "qa-3", "qa-4"]
        assert {record["evaluation_slice"] for record in rows[key]} == {key}
    assert rows["vi_en"][0]["question"].startswith("Question in vi")
    assert rows["vi_en"][0]["expected_answers"] == ["Answer in en"]
    assert rows["vi_en"][0]["question_language"] == "vi"
    assert rows["vi_en"][0]["corpus_language"] == rows["vi_en"][0]["answer_language"] == "en"
    assert rows["vi_en"][0]["expected_documents"][0].startswith("xquad_en_")
    assert rows["en_vi"][0]["question"].startswith("Question in en")
    assert rows["en_vi"][0]["expected_answers"] == ["Answer in vi"]
    assert rows["en_vi"][0]["expected_documents"][0].startswith("xquad_vi_")
    assert report["paragraph_count_by_language"] == {"en": 3, "vi": 3}
    assert report["qa_count_by_slice"] == {name: 4 for name in bilingual.SLICES}
    for language in ("en", "vi"):
        docs = [
            json.loads(line) for line in contents[f"qa/documents_{language}.jsonl"].splitlines()
        ]
        assert len(docs) == 3
        assert all("source_question_ids" not in record for record in docs)
        for record in docs:
            text = contents[f"documents/{language}/{record['path']}"].decode("utf-8")
            assert record["language"] == language
            assert record["parallel_group_id"] in text
            assert "expected_answer" not in text and "question" not in text


def test_paragraph_gold_answer_must_be_span_in_its_source_context() -> None:
    invalid = source("en")
    invalid["data"][0]["paragraphs"][0]["qas"][0]["answers"][0]["answer_start"] = 50
    with pytest.raises(common.CorpusError, match="answer span"):
        bilingual.source_records(invalid, "en")


@pytest.fixture
def download_calls() -> list[bool]:
    return []


@pytest.fixture
def corpus_root(
    tmp_path_factory: pytest.TempPathFactory,
    monkeypatch: pytest.MonkeyPatch,
    download_calls: list[bool],
) -> Path:
    # Compact fixture path avoids Windows MAX_PATH with full SHA256 document names.
    root = tmp_path_factory.mktemp("b")
    source_bodies = {
        "xquad_en": bilingual.json_bytes(source("en")),
        "xquad_vi": bilingual.json_bytes(source("vi")),
    }
    for name in (
        "manifest.json",
        "source-license-inventory.json",
        "default/manifest.json",
        "document/manifest.json",
        "bilingual/manifest.json",
    ):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(common.CORPUS_ROOT / name, path)
    domain_manifest = common.read_json(root / "bilingual/manifest.json")
    domain_manifest.update(
        status="not_downloaded",
        downloaded_at=None,
        document_count=None,
        qa_count=None,
        checksum={},
        artifacts=[],
    )
    for entry in domain_manifest["sources"]:
        body = source_bodies[entry["id"]]
        entry["expected_sha256"] = hashlib.sha256(body).hexdigest()
        git_sha = hashlib.sha1(usedforsecurity=False)
        git_sha.update(f"blob {len(body)}".encode("ascii") + bytes([0]))
        git_sha.update(body)
        entry["git_blob_sha1"] = git_sha.hexdigest()
    # Keep the synthetic pins consistent in inventory as metadata validation requires.
    common.write_json(root / "bilingual/manifest.json", domain_manifest)
    inventory = common.read_json(root / "source-license-inventory.json")
    inventory_entry = next(item for item in inventory["datasets"] if item["domain"] == "bilingual")
    inventory_entry["sources"] = deepcopy(domain_manifest["sources"])
    common.write_json(root / "source-license-inventory.json", inventory)
    aggregate = common.read_json(root / "manifest.json")
    aggregate["domains"]["bilingual"].update(
        status="not_downloaded", document_count=None, qa_count=None
    )
    common.write_json(root / "manifest.json", aggregate)

    def fake_download(url: str, destination: Path, **options: Any) -> common.DownloadReceipt:
        item = next(
            source_item for source_item in domain_manifest["sources"] if url == source_item["url"]
        )
        body = source_bodies[item["id"]]
        reused = destination.is_file() and destination.read_bytes() == body
        if not reused:
            common.atomic_write(destination, [body])
        if options.get("validate"):
            options["validate"](destination)
        download_calls.append(reused)
        return common.DownloadReceipt(
            url,
            hashlib.sha256(body).hexdigest(),
            len(body),
            None if reused else "2026-09-26T00:00:00+00:00",
            reused,
        )

    monkeypatch.setattr(bilingual, "download", fake_download)
    return root


def test_metadata_only_checkout_can_rebuild_without_changing_qa(
    corpus_root: Path, download_calls: list[bool],
) -> None:
    expected = bilingual.prepare_bilingual(corpus_root)
    clone = corpus_root.parent / (corpus_root.name + "c")
    clone.mkdir()
    for name in ["manifest.json", "source-license-inventory.json", *[f"{d}/manifest.json" for d in common.DOMAINS]]:
        target = clone / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(corpus_root / name, target)
    shutil.copytree(corpus_root / "bilingual/qa", clone / "bilingual/qa")
    assert not (clone / ".downloads").exists()
    assert bilingual.prepare_bilingual(clone) == expected
    assert bilingual.validate_bilingual(clone / "bilingual") == expected
    assert download_calls == [False, False, False, False]


def test_prepare_validate_and_rerun_preserves_hashes_mtimes_ids_and_timestamp(
    corpus_root: Path,
    download_calls: list[bool],
) -> None:
    root = corpus_root
    first = bilingual.prepare_bilingual(root)
    before = bilingual._published_hashes(root)
    mtimes = {name: (root / name).stat().st_mtime_ns for name in before}
    manifest = common.read_json(root / "bilingual/manifest.json")
    identifiers = {
        name: [record["id"] for record in common.read_jsonl(root / f"bilingual/qa/{name}.jsonl")]
        for name in bilingual.SLICES
    }
    assert first == bilingual.validate_bilingual(root / "bilingual")
    assert bilingual.prepare_bilingual(root) == first
    assert bilingual._published_hashes(root) == before
    assert {name: (root / name).stat().st_mtime_ns for name in before} == mtimes
    assert (
        common.read_json(root / "bilingual/manifest.json")["downloaded_at"]
        == manifest["downloaded_at"]
    )
    assert {
        name: [record["id"] for record in common.read_jsonl(root / f"bilingual/qa/{name}.jsonl")]
        for name in bilingual.SLICES
    } == identifiers
    assert download_calls == [False, False, True, True]
    assert len(set(first["paragraph_group_ids"])) == first["parallel_group_count"]
    validate_corpus.validate_metadata(root)


def test_alignment_rejects_regrouped_paragraphs_with_same_ids_and_titles() -> None:
    changed = source("vi")
    paragraphs = changed["data"][0]["paragraphs"]
    paragraphs[1]["context"] += " " + paragraphs[0]["context"]
    moved = paragraphs[0]["qas"].pop()
    moved["answers"][0]["answer_start"] = paragraphs[1]["context"].index(
        moved["answers"][0]["text"]
    )
    paragraphs[1]["qas"].append(moved)
    with pytest.raises(common.CorpusError, match="structures do not align"):
        bilingual.align_paragraphs(
            bilingual.source_records(source("en"), "en"),
            bilingual.source_records(changed, "vi"),
        )


@pytest.mark.parametrize("mutation", ["duplicate_id", "boolean_offset", "empty_answer", "version"])
def test_invalid_source_is_refused(mutation: str) -> None:
    value = source("en")
    qas = value["data"][0]["paragraphs"][0]["qas"]
    if mutation == "duplicate_id":
        qas[1]["id"] = qas[0]["id"]
    elif mutation == "boolean_offset":
        qas[0]["answers"][0]["answer_start"] = True
    elif mutation == "empty_answer":
        qas[0]["answers"][0]["text"] = ""
    else:
        value["version"] = "2.0"
    with pytest.raises(common.CorpusError):
        bilingual.source_records(value, "en")


@pytest.mark.parametrize(
    "corruption", ["gold", "evidence", "language", "raw", "extra", "missing", "role", "sha"]
)
def test_validator_refuses_corruption(corpus_root: Path, corruption: str) -> None:
    bilingual.prepare_bilingual(corpus_root)
    domain = corpus_root / "bilingual"
    if corruption in {"gold", "evidence", "language"}:
        path = domain / "qa/en_vi.jsonl"
        rows = list(common.read_jsonl(path))
        if corruption == "gold":
            rows[0]["expected_answers"] = ["Wrong gold"]
        elif corruption == "evidence":
            rows[0]["evidence"][0]["text"] = "Wrong evidence"
        else:
            rows[0]["corpus_language"] = "en"
        path.write_bytes(
            b"".join(bilingual.json_bytes(row).replace(b"\n", b"") + b"\n" for row in rows)
        )
    elif corruption == "raw":
        (domain / bilingual.RAW_EN).write_bytes(bilingual.json_bytes(source("vi")))
    elif corruption == "extra":
        (domain / "qa/unmanaged.txt").write_text("preserve me", encoding="utf-8")
    elif corruption == "missing":
        next((domain / "documents/en").iterdir()).unlink()
    else:
        manifest = common.read_json(domain / "manifest.json")
        if corruption == "role":
            manifest["artifacts"][0]["role"] = "raw"
        else:
            manifest["sources"][0]["expected_sha256"] = "0" * 64
        common.write_json(domain / "manifest.json", manifest)
    with pytest.raises(common.CorpusError):
        bilingual.validate_bilingual(domain)


def test_setup_refuses_existing_lock_and_unmanaged_files(corpus_root: Path) -> None:
    cache = corpus_root / ".downloads"
    cache.mkdir()
    lock = cache / "bilingual-setup.lock"
    lock.write_text("another writer", encoding="utf-8")
    with pytest.raises(common.CorpusError, match="lock exists"):
        bilingual.prepare_bilingual(corpus_root)
    assert lock.read_text(encoding="utf-8") == "another writer"
    lock.unlink()
    extra = corpus_root / "bilingual/user.txt"
    extra.write_text("keep", encoding="utf-8")
    with pytest.raises(common.CorpusError, match="unrecognized"):
        bilingual.prepare_bilingual(corpus_root)
    assert extra.read_text(encoding="utf-8") == "keep"


def test_failed_publication_preserves_prior_tree_and_aggregate(
    corpus_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    before = bilingual._published_hashes(corpus_root)
    real_write = bilingual.atomic_write

    def fail_aggregate(path: Path, chunks: Any, **options: Any) -> Any:
        if path == corpus_root / "manifest.json":
            raise OSError("Synthetic aggregate publication failure")
        return real_write(path, chunks, **options)

    monkeypatch.setattr(bilingual, "atomic_write", fail_aggregate)
    with pytest.raises(OSError, match="publication failure"):
        bilingual.prepare_bilingual(corpus_root)
    assert bilingual._published_hashes(corpus_root) == before
    assert not (corpus_root / ".downloads/bilingual-setup.lock").exists()
    assert list((corpus_root / ".downloads").glob("bilingual-stage-*"))


def test_domain_commands_dispatch_to_synthetic_corpus_and_report_failure(
    corpus_root: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    shutil.copytree(common.CORPUS_ROOT / "schemas", corpus_root / "schemas")
    monkeypatch.setattr(roots, "CORPUS_ROOT", corpus_root)
    assert setup_corpus.main(["--domain", "bilingual"]) == 0
    assert "CORPUS SETUP: PASS" in capsys.readouterr().out
    assert validate_corpus.main(["--domain", "bilingual"]) == 0
    assert "CORPUS VALIDATION: PASS" in capsys.readouterr().out
    (corpus_root / "bilingual/qa/en_vi.jsonl").unlink()
    assert validate_corpus.main(["--domain", "bilingual"]) == 1
    captured = capsys.readouterr()
    assert "PASS" not in captured.out and "FAIL" in captured.err
