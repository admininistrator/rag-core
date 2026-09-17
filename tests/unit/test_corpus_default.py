"""Synthetic pipeline/fault tests; never substitutes for live HotpotQA acceptance."""

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
import prepare_default as default  # noqa: E402
import validate_corpus  # noqa: E402

pytestmark = pytest.mark.unit


def source_example(number: int, category: str = "bridge", level: str = "hard") -> dict[str, Any]:
    return {
        "_id": f"synthetic_{number:04}",
        "question": f"Synthetic question {number}?",
        "answer": f"Synthetic gold answer {number}",
        "type": category,
        "level": level,
        "context": [
            ["Shared title", [f"Paragraph {number} is evidence.", " Another sentence."]],
            ["Distractor", ["Common distractor paragraph."]],
            ["Other", ["Other distractor paragraph."]],
        ],
        "supporting_facts": [["Shared title", 0], ["Shared title", 1]],
    }


def synthetic_source(count: int = 160) -> list[dict[str, Any]]:
    return [
        source_example(i, "bridge" if i % 2 else "comparison", "medium" if i % 4 < 2 else "hard")
        for i in range(count)
    ]


def parquet_bytes(examples: list[dict[str, Any]] | None = None) -> bytes:
    import pyarrow as pa
    import pyarrow.parquet as pq

    rows = []
    for record in examples if examples is not None else synthetic_source():
        row = {key: record[key] for key in ("question", "answer", "type", "level")}
        row["id"] = record["_id"]
        row["context"] = {
            "title": [p[0] for p in record["context"]],
            "sentences": [p[1] for p in record["context"]],
        }
        row["supporting_facts"] = {
            "title": [fact[0] for fact in record["supporting_facts"]],
            "sent_id": [fact[1] for fact in record["supporting_facts"]],
        }
        rows.append(row)
    sink = pa.BufferOutputStream()
    pq.write_table(pa.Table.from_pylist(rows), sink)
    return bytes(sink.getvalue())


def artifact_records(contents: dict[str, bytes]) -> list[dict[str, Any]]:
    return [json.loads(line) for line in contents[default.QA_PATH].decode().splitlines()]


def test_supporting_only_gold_with_distractors_and_original_answer() -> None:
    examples = [source_example(1), source_example(2)]
    contents, report = default.build_artifacts(examples, "0" * 64, size=2)
    qa = artifact_records(contents)
    for record, original in zip(qa, examples, strict=True):
        support = default.paragraph_id(*original["context"][0])
        distractor = default.paragraph_id(*original["context"][1])
        assert record["expected_documents"] == [support]
        assert distractor in record["context_documents"]
        assert f"documents/{distractor}.md" in contents
        assert record["expected_answers"] == [original["answer"]]
        assert record["supporting_facts"] == original["supporting_facts"]
        assert (record["category"], record["difficulty"]) == (original["type"], original["level"])
    assert report["document_count"] == 4 and report["context_paragraph_instances"] == 6
    assert report["deduplicated_instances"] == 2


def test_title_collisions_across_questions_preserve_distinct_paragraphs() -> None:
    examples = [source_example(1), source_example(2)]
    contents, _ = default.build_artifacts(examples, "0" * 64, size=2)
    qa = artifact_records(contents)
    assert qa[0]["expected_documents"] != qa[1]["expected_documents"]
    index = json.loads(contents[default.INDEX_PATH])
    assert len([item for item in index if item["title"] == "Shared title"]) == 2
    common_distractor = [item for item in index if item["title"] == "Distractor"]
    assert len(common_distractor) == 1
    assert common_distractor[0]["source_question_ids"] == ["synthetic_0001", "synthetic_0002"]


def test_multiple_supporting_titles_all_map_without_including_distractors() -> None:
    example = source_example(1)
    example["supporting_facts"].append(["Other", 0])
    contents, _ = default.build_artifacts([example], "0" * 64, size=1)
    record = artifact_records(contents)[0]
    assert record["expected_documents"] == [
        default.paragraph_id(*example["context"][0]), default.paragraph_id(*example["context"][2]),
    ]
    assert default.paragraph_id(*example["context"][1]) not in record["expected_documents"]


def test_document_text_has_no_injected_gold_or_question_provenance() -> None:
    contents, _ = default.build_artifacts([source_example(1)], "0" * 64, size=1)
    for path, content in contents.items():
        if path.startswith("documents/"):
            text = content.decode()
            assert "synthetic_0001" not in text and "Synthetic gold answer" not in text
            assert "supporting" not in text and "question" not in text and "expected" not in text
            assert "source_dataset: hotpotqa" in text


def test_reproducible_stratified_sampling_is_independent_of_input_order() -> None:
    examples = synthetic_source()
    first, report = default.build_artifacts(examples, "0" * 64)
    second, same_report = default.build_artifacts(list(reversed(examples)), "0" * 64)
    assert first == second and report == same_report
    assert report["qa_count"] == 100
    assert report["selected_distribution"]["strata"] == {
        "bridge/hard": 25, "bridge/medium": 25,
        "comparison/hard": 25, "comparison/medium": 25,
    }
    assert len(set(report["selected_source_ids"])) == 100
    assert default.sample_records(examples, seed=43) != default.sample_records(examples)


def test_actual_hard_only_source_is_not_relabelled_to_medium() -> None:
    examples = [source_example(i, "bridge" if i % 2 else "comparison") for i in range(140)]
    _, report = default.build_artifacts(examples, "0" * 64)
    assert report["selected_distribution"]["by_level"] == {"hard": 100}
    assert report["selected_distribution"]["by_type"] == {"bridge": 50, "comparison": 50}


def test_exhausted_strata_redistribute_without_duplicates() -> None:
    examples = [source_example(0, "comparison", "medium")]
    examples += [source_example(i, "bridge", "hard") for i in range(1, 120)]
    selected = default.sample_records(examples)
    assert len(selected) == len({item["_id"] for item in selected}) == 100
    assert default.distribution(selected)["strata"] == {"bridge/hard": 99, "comparison/medium": 1}


@pytest.mark.parametrize("mutation", ["answer", "duplicate_id", "missing_title", "index", "bool_index", "ambiguous_title", "empty_context", "type", "level"])
def test_invalid_source_is_refused_before_materialization(tmp_path: Path, mutation: str) -> None:
    examples = [source_example(1)]
    if mutation == "answer":
        examples[0]["answer"] = " "
    elif mutation == "duplicate_id":
        examples.append(deepcopy(examples[0]))
    elif mutation == "missing_title":
        examples[0]["supporting_facts"] = [["Absent", 0]]
    elif mutation in {"index", "bool_index"}:
        examples[0]["supporting_facts"] = [["Shared title", 10 if mutation == "index" else True]]
    elif mutation == "ambiguous_title":
        examples[0]["context"].append(["Shared title", ["Different paragraph."]])
    elif mutation == "empty_context":
        examples[0]["context"] = []
    else:
        examples[0][mutation] = "unknown"
    path = tmp_path / "source.json"
    path.write_bytes(default.json_bytes(examples))
    with pytest.raises(common.CorpusError):
        parsed = default.source_records(path)
        default.build_artifacts(parsed, "0" * 64, size=len(parsed))


def test_source_annotation_outside_sample_is_reported_without_altering_gold(tmp_path: Path) -> None:
    examples = synthetic_source()
    before, before_report = default.build_artifacts(examples, "0" * 64)
    selected = set(before_report["selected_source_ids"])
    original = next(record for record in examples if record["_id"] not in selected)
    original["supporting_facts"][0][1] = 902
    path = tmp_path / "source.json"
    path.write_bytes(default.json_bytes(examples))
    parsed = default.source_records(path)
    after, report = default.build_artifacts(parsed, "0" * 64)
    assert parsed == examples
    assert report["selected_source_ids"] == before_report["selected_source_ids"]
    assert after[default.QA_PATH] == before[default.QA_PATH]
    assert report["source_annotation_anomalies"] == [{
        "source_id": original["_id"], "title": "Shared title", "sent_id": 902, "sentence_count": 2,
    }]
    assert report["selected_annotation_anomalies"] == []


def test_source_annotation_inside_sample_fails_without_resampling(tmp_path: Path) -> None:
    examples = synthetic_source()
    selected_ids = [record["_id"] for record in default.sample_records(examples)]
    chosen = next(record for record in examples if record["_id"] == selected_ids[0])
    chosen["supporting_facts"][0][1] = 902
    path = tmp_path / "source.json"
    path.write_bytes(default.json_bytes(examples))
    parsed = default.source_records(path)
    assert [record["_id"] for record in default.sample_records(parsed)] == selected_ids
    with pytest.raises(common.CorpusError, match="do not resample"):
        default.build_artifacts(parsed, "0" * 64)


def test_source_below_target_is_a_failure(tmp_path: Path) -> None:
    path = tmp_path / "source.json"
    path.write_bytes(default.json_bytes([source_example(1)]))
    with pytest.raises(common.CorpusError, match="100-QA"):
        default.validate_download(path)


@pytest.fixture
def corpus_root(tmp_path: Path) -> Path:
    names = ["manifest.json", "source-license-inventory.json"]
    names += [f"{domain}/manifest.json" for domain in common.DOMAINS]
    for name in names:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(common.CORPUS_ROOT / name, path)
    # A unit test's starting state is always synthetic and not downloaded.
    manifest = common.read_json(tmp_path / "default/manifest.json")
    manifest["sources"][0]["expected_sha256"] = hashlib.sha256(parquet_bytes()).hexdigest()
    manifest.update(status="not_downloaded", downloaded_at=None, document_count=None,
                    qa_count=None, artifacts=[], checksum={})
    common.write_json(tmp_path / "default/manifest.json", manifest)
    inventory = common.read_json(tmp_path / "source-license-inventory.json")
    inventory["datasets"][0]["sources"] = deepcopy(manifest["sources"])
    common.write_json(tmp_path / "source-license-inventory.json", inventory)
    aggregate = common.read_json(tmp_path / "manifest.json")
    aggregate["domains"]["default"].update(status="not_downloaded", document_count=None, qa_count=None)
    common.write_json(tmp_path / "manifest.json", aggregate)
    return tmp_path


@pytest.fixture
def fake_download(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    examples = synthetic_source()
    body = parquet_bytes(examples)
    checksum = hashlib.sha256(body).hexdigest()
    calls: list[dict[str, Any]] = []

    def injected(url: str, destination: Path, **options: Any) -> common.DownloadReceipt:
        calls.append(options)
        reused = destination.is_file()
        if reused:
            assert options["expected_sha256"] == checksum
            assert destination.read_bytes() == body
        else:
            common.atomic_write(destination, [body])
        return common.DownloadReceipt(url, checksum, len(body), None if reused else "2026-09-17T16:00:00Z", reused)

    monkeypatch.setattr(default, "download", injected)
    return calls


def published_hashes(root: Path) -> dict[str, str]:
    paths = [root / "manifest.json", *[p for p in (root / "default").rglob("*") if p.is_file()]]
    return {path.relative_to(root).as_posix(): common.sha256_file(path) for path in paths}


def test_prepare_and_rerun_preserve_ids_content_timestamp_and_mtimes(
    corpus_root: Path, fake_download: list[dict[str, Any]]
) -> None:
    report = default.prepare_default(corpus_root)
    before = published_hashes(corpus_root)
    times = {name: (corpus_root / name).stat().st_mtime_ns for name in before}
    timestamp = common.read_json(corpus_root / "default/manifest.json")["downloaded_at"]
    assert default.prepare_default(corpus_root) == report
    assert published_hashes(corpus_root) == before
    assert times == {name: (corpus_root / name).stat().st_mtime_ns for name in before}
    assert common.read_json(corpus_root / "default/manifest.json")["downloaded_at"] == timestamp
    assert len(fake_download) == 2 and fake_download[1]["expected_sha256"] == report["source_sha256"]
    assert default.validate_default(corpus_root / "default") == report
    validate_corpus.validate_metadata(corpus_root)
    assert {path.name for path in (corpus_root / ".downloads").iterdir()} == {
        "hf-hotpotqa-distractor-validation.parquet", "hf-hotpotqa-download.json",
    }


def test_parquet_conversion_preserves_original_semantic_fields(tmp_path: Path) -> None:
    examples = synthetic_source()
    path = tmp_path / "synthetic.parquet"
    path.write_bytes(parquet_bytes(examples))
    assert default.parquet_records(path) == examples
    default.validate_parquet(path)
    assert list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize("corruption", ["converted_json", "parquet_pin"])
def test_validator_refuses_conversion_or_primary_source_drift(
    corpus_root: Path, fake_download: list[dict[str, Any]], corruption: str
) -> None:
    default.prepare_default(corpus_root)
    domain = corpus_root / "default"
    path = domain / (default.RAW_PATH if corruption == "converted_json" else default.PARQUET_PATH)
    path.write_bytes(b"corrupted synthetic source")
    with pytest.raises(common.CorpusError):
        default.validate_default(domain)


def test_download_failure_preserves_last_good_metadata(
    corpus_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    before = published_hashes(corpus_root)

    def offline(*_args: Any, **_kwargs: Any) -> Any:
        raise common.DownloadError("Synthetic source transport failure")

    monkeypatch.setattr(default, "download", offline)
    with pytest.raises(common.DownloadError):
        default.prepare_default(corpus_root)
    assert published_hashes(corpus_root) == before
    assert not (corpus_root / ".downloads/default-setup.lock").exists()
    assert len(list((corpus_root / ".downloads").glob("default-stage-*"))) == 1


@pytest.mark.parametrize("failure", ["staged_validation", "new_directory", "aggregate", "interrupt"])
def test_publication_fault_preserves_last_good_tree_and_aggregate(
    corpus_root: Path, fake_download: list[dict[str, Any]], monkeypatch: pytest.MonkeyPatch,
    failure: str,
) -> None:
    before = published_hashes(corpus_root)
    if failure == "staged_validation":
        original_validate = default.validate_default

        def broken_validate(path: Path) -> Any:
            if "default-stage-" in str(path):
                raise common.CorpusError("Synthetic staged validation failure")
            return original_validate(path)

        monkeypatch.setattr(default, "validate_default", broken_validate)
    elif failure == "new_directory":
        original_replace = default.os.replace
        failed = False

        def broken_replace(source: Any, destination: Any) -> None:
            nonlocal failed
            if not failed and Path(destination) == corpus_root / "default":
                failed = True
                raise OSError("Synthetic directory publication failure")
            original_replace(source, destination)

        monkeypatch.setattr(default.os, "replace", broken_replace)
    else:
        original_write = default.atomic_write

        def broken_write(destination: Path, chunks: Any, **options: Any) -> bool:
            if destination == corpus_root / "manifest.json":
                if failure == "interrupt":
                    raise KeyboardInterrupt("Synthetic publication interruption")
                raise OSError("Synthetic aggregate publication failure")
            return original_write(destination, chunks, **options)

        monkeypatch.setattr(default, "atomic_write", broken_write)
    with pytest.raises((common.CorpusError, OSError, KeyboardInterrupt)):
        default.prepare_default(corpus_root)
    assert published_hashes(corpus_root) == before
    assert not (corpus_root / ".downloads/default-setup.lock").exists()


def test_refresh_publication_failure_preserves_existing_ready_data(
    corpus_root: Path, fake_download: list[dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    default.prepare_default(corpus_root)
    manifest_path = corpus_root / "default/manifest.json"
    manifest = common.read_json(manifest_path)
    manifest["notes"] = "Last good ready checkpoint before metadata refresh"
    common.write_json(manifest_path, manifest)
    default.validate_default(corpus_root / "default")
    before = published_hashes(corpus_root)
    original_write = default.atomic_write

    def aggregate_failure(destination: Path, chunks: Any, **options: Any) -> bool:
        if destination == corpus_root / "manifest.json":
            raise OSError("Synthetic refresh publication failure")
        return original_write(destination, chunks, **options)

    monkeypatch.setattr(default, "atomic_write", aggregate_failure)
    with pytest.raises(OSError, match="refresh"):
        default.prepare_default(corpus_root)
    assert published_hashes(corpus_root) == before
    assert default.validate_default(corpus_root / "default")["qa_count"] == 100


@pytest.mark.parametrize("corruption", ["gold", "support", "document", "duplicate", "missing", "receipt"])
def test_validator_refuses_gold_content_mapping_or_artifact_drift(
    corpus_root: Path, fake_download: list[dict[str, Any]], corruption: str
) -> None:
    default.prepare_default(corpus_root)
    domain = corpus_root / "default"
    if corruption in {"gold", "support"}:
        records = list(common.read_jsonl(domain / default.QA_PATH))
        if corruption == "gold":
            records[0]["expected_answers"] = ["Altered synthetic answer"]
        else:
            records[0]["expected_documents"] = records[0]["context_documents"]
        (domain / default.QA_PATH).write_bytes(b"".join((json.dumps(r) + "\n").encode() for r in records))
    elif corruption == "receipt":
        manifest = common.read_json(domain / "manifest.json")
        manifest["artifacts"][0]["bytes"] += 1
        common.write_json(domain / "manifest.json", manifest)
    else:
        path = next((domain / "documents").glob("*.md"))
        if corruption == "document":
            path.write_text("Corrupt text", encoding="utf-8")
        elif corruption == "missing":
            path.unlink()
        else:
            shutil.copy2(path, domain / "documents/duplicate.md")
    with pytest.raises(common.CorpusError):
        default.validate_default(domain)


def test_unrecognized_existing_files_are_preserved_and_refused(
    corpus_root: Path, fake_download: list[dict[str, Any]]
) -> None:
    personal = corpus_root / "default/user-file.md"
    personal.write_text("User owned", encoding="utf-8")
    with pytest.raises(common.CorpusError, match="unrecognized"):
        default.prepare_default(corpus_root)
    assert personal.read_text(encoding="utf-8") == "User owned" and fake_download == []


def test_existing_setup_lock_prevents_mutation_or_download(
    corpus_root: Path, fake_download: list[dict[str, Any]]
) -> None:
    cache = corpus_root / ".downloads"
    cache.mkdir()
    lock = cache / "default-setup.lock"
    lock.write_text("Another writer", encoding="utf-8")
    before = published_hashes(corpus_root)
    with pytest.raises(common.CorpusError, match="lock"):
        default.prepare_default(corpus_root)
    assert published_hashes(corpus_root) == before and fake_download == []
    assert lock.read_text(encoding="utf-8") == "Another writer"
