"""Output isolation, metadata-only checkouts and honest all-domain failures."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "corpus-documents/scripts"
sys.path.insert(0, str(SCRIPTS))
import common  # noqa: E402
import corpus_root as roots  # noqa: E402
import prepare_bilingual  # noqa: E402
import prepare_default  # noqa: E402
import prepare_document  # noqa: E402
import setup_corpus  # noqa: E402
import validate_corpus  # noqa: E402
import verify_reproduction  # noqa: E402

pytestmark = pytest.mark.unit


@pytest.fixture
def metadata_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "c"
    root.mkdir()
    for name in ["source-license-inventory.json", "manifest.json", *[f"{d}/manifest.json" for d in common.DOMAINS]]:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(common.CORPUS_ROOT / name, target)
    monkeypatch.setattr(roots, "CORPUS_ROOT", root)
    return root


@pytest.mark.parametrize("relative", ["..", "default", "scripts", ".downloads/x", ".repro", ".repro/a/b", ".repro/CON", ".repro/a:stream", ".repro/a.", ".repro/../outside"])
def test_output_refuses_unsafe_or_protected_paths(metadata_root: Path, relative: str) -> None:
    with pytest.raises(common.CorpusError):
        roots.output_root(str(metadata_root / relative))
    assert not (metadata_root / ".repro").exists()


def test_output_rejects_links_even_inside_corpus(metadata_root: Path) -> None:
    # is_junction is covered using a real Windows junction in the shared path tests.
    # Here simulate the filesystem flag without needing symlink creation privileges.
    from unittest.mock import patch

    with (
        patch.object(Path, "is_symlink", lambda path: path.name == ".repro"),
        pytest.raises(common.CorpusError, match="links"),
    ):
        roots.output_root(str(metadata_root / ".repro/a"))


def test_initialize_copies_only_provenance_and_validator_never_bootstraps(metadata_root: Path) -> None:
    root = roots.output_root(str(metadata_root / ".repro/a"))
    assert validate_corpus.main(["--all", "--output-root", str(root)]) == 1
    assert not root.exists()
    roots.initialize_root(root)
    validate_corpus.validate_metadata(root)
    assert (root / "source-license-inventory.json").read_bytes() == (metadata_root / "source-license-inventory.json").read_bytes()
    assert len(list(root.rglob("*.*"))) == 5
    for domain in common.DOMAINS:
        manifest = common.read_json(root / domain / "manifest.json")
        assert manifest["status"] == "not_downloaded"
        assert manifest["downloaded_at"] is None
        assert not manifest["artifacts"] and not manifest["checksum"]
    assert validate_corpus.main(["--all", "--output-root", str(root)]) == 1


def test_initialize_refuses_unknown_files_without_overwrite(metadata_root: Path) -> None:
    root = metadata_root / ".repro/a"
    root.mkdir(parents=True)
    personal = root / "user.txt"
    personal.write_text("preserve", encoding="utf-8")
    with pytest.raises(common.CorpusError):
        roots.initialize_root(root)
    assert list(root.iterdir()) == [personal]
    assert personal.read_text() == "preserve"


@pytest.mark.parametrize("domain", common.DOMAINS)
def test_metadata_only_clone_retains_verified_qa_and_clears_measurements(metadata_root: Path, domain: str) -> None:
    directory = metadata_root / domain
    original = common.read_json(directory / "manifest.json")
    qa = next(item for item in original["artifacts"] if item["role"] == "qa")
    # Synthetic bytes with a consistent receipt; no live ignored files needed.
    target = directory / qa["path"]
    common.atomic_write(target, [b"synthetic QA bytes"])
    original["checksum"][qa["path"]] = common.sha256_file(target)
    common.write_json(directory / "manifest.json", original)
    manifest, checkout = roots.preparation_manifest(directory)
    assert checkout and manifest["status"] == "not_downloaded"
    assert manifest["downloaded_at"] is None and manifest["checksum"] == {}
    assert common.read_json(directory / "manifest.json") == original
    target.write_bytes(b"user changed this")
    with pytest.raises(common.CorpusError, match="modified"):
        roots.preparation_manifest(directory)


@pytest.mark.parametrize("directory", ["raw", "documents"])
def test_partial_payload_never_becomes_metadata_checkout(metadata_root: Path, directory: str) -> None:
    (metadata_root / "default" / directory).mkdir()
    manifest, checkout = roots.preparation_manifest(metadata_root / "default")
    assert not checkout and manifest["status"] == "ready"
    with pytest.raises(common.CorpusError):
        prepare_default.prepare_default(metadata_root)


def test_all_domain_failure_stops_dispatch_and_never_prints_pass(metadata_root: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    called = []

    def first(root: Path) -> dict[str, Any]:
        called.append("default")
        return {}

    def fail(root: Path) -> dict[str, Any]:
        called.append("document")
        raise common.DownloadError("synthetic transport failure")

    def forbidden(root: Path) -> dict[str, Any]:
        pytest.fail("must stop before bilingual")

    monkeypatch.setattr(prepare_default, "prepare_default", first)
    monkeypatch.setattr(prepare_document, "prepare_document", fail)
    monkeypatch.setattr(prepare_bilingual, "prepare_bilingual", forbidden)
    assert setup_corpus.main(["--all"]) == 1
    assert called == ["default", "document"]
    captured = capsys.readouterr()
    assert "PASS" not in captured.out and "synthetic transport failure" in captured.err
    assert not (metadata_root / ".downloads/corpus-setup.lock").exists()


def test_existing_setup_lock_is_preserved(metadata_root: Path) -> None:
    with roots.setup_lock(metadata_root):
        assert setup_corpus.main(["--all"]) == 1
        assert (metadata_root / ".downloads/corpus-setup.lock").exists()


def test_fingerprint_separates_timestamps_but_detects_content_and_ids(metadata_root: Path) -> None:
    for domain in common.DOMAINS:
        common.atomic_write(metadata_root / domain / "qa/eval.jsonl", [b'{"id":"qa-1"}\n'])
    common.atomic_write(metadata_root / "bilingual/qa/paragraphs.en.jsonl", [b'{"document_id":"doc-1"}\n'])
    before = verify_reproduction.snapshot(metadata_root)
    manifest_path = metadata_root / "bilingual/manifest.json"
    manifest = common.read_json(manifest_path)
    manifest["downloaded_at"] = "2026-09-26T12:00:00Z"
    common.write_json(manifest_path, manifest)
    changed_time = verify_reproduction.snapshot(metadata_root)
    verify_reproduction.compare_content(before, changed_time)
    assert before["published"] != changed_time["published"]
    assert before["downloaded_at"] != changed_time["downloaded_at"]
    assert len(before["ids"]) == 3
    common.atomic_write(metadata_root / "default/qa/eval.jsonl", [b'{"id":"qa-2"}\n'])
    changed_id = verify_reproduction.snapshot(metadata_root)
    assert before["ids"] != changed_id["ids"]
    with pytest.raises(common.CorpusError, match="content"):
        verify_reproduction.compare_content(before, changed_id)
