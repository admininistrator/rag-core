"""Synthetic corpus faults only. These fixtures never replace official dataset gold."""

from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import sys
from copy import deepcopy
from http.client import IncompleteRead
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "corpus-documents" / "scripts"
# The corpus directory is deliberately independent of the application package.
sys.path.insert(0, str(SCRIPTS))
import common  # noqa: E402
import prepare_default  # noqa: E402
import setup_corpus  # noqa: E402
import validate_corpus  # noqa: E402

pytestmark = pytest.mark.unit
URL = "https://raw.githubusercontent.com/google-deepmind/xquad/" + "a" * 40 + "/sample.json"
VALID = b'{"fixture":"synthetic","text":"valid"}\n'
HASH = hashlib.sha256(VALID).hexdigest()


class Response(io.BytesIO):
    status = 200

    def __init__(self, body: bytes, *, length: int | None = None, url: str = URL) -> None:
        super().__init__(body)
        self.headers = {"Content-Length": str(len(body) if length is None else length)}
        self.url = url

    def geturl(self) -> str:
        return self.url


def response_opener(body: bytes = VALID, **kwargs: Any) -> Any:
    return lambda _url, _timeout: Response(body, **kwargs)


def assert_preserved(path: Path, expected: bytes) -> None:
    assert path.read_bytes() == expected
    assert list(path.parent.glob("*.part")) == []


def test_corrupt_download_never_publishes_over_valid_prior(tmp_path: Path) -> None:
    destination = tmp_path / "source.json"
    destination.write_bytes(VALID)
    # A different requested pin forces download; incoming corruption must preserve old bytes.
    requested = hashlib.sha256(b"new-valid-version").hexdigest()
    with pytest.raises(common.DownloadError, match="verification"):
        common.download(URL, destination, expected_sha256=requested, opener=response_opener(b"bad"))
    assert_preserved(destination, VALID)


def test_corrupt_download_does_not_create_destination(tmp_path: Path) -> None:
    destination = tmp_path / "source.json"
    with pytest.raises(common.DownloadError):
        common.download(URL, destination, expected_sha256=HASH, opener=response_opener(b"corrupt"))
    assert not destination.exists()
    assert list(tmp_path.glob("*.part")) == []


def test_interrupted_stream_and_retry_preserve_prior(tmp_path: Path) -> None:
    destination = tmp_path / "source.json"
    destination.write_bytes(b"old-valid")
    calls = 0

    class Interrupted(Response):
        def read(self, size: int = -1) -> bytes:
            if self.tell():
                raise ConnectionResetError("synthetic transport interruption")
            return super().read(5)

    def opener(_url: str, _timeout: float) -> Response:
        nonlocal calls
        calls += 1
        return Interrupted(VALID)

    sleeps: list[float] = []
    with pytest.raises(common.DownloadError, match="3 attempt"):
        common.download(URL, destination, expected_sha256=HASH, opener=opener, sleep=sleeps.append)
    assert calls == 3
    assert sleeps == [1, 2]
    assert_preserved(destination, b"old-valid")


def test_incomplete_http_read_retries_without_publishing_partial(tmp_path: Path) -> None:
    destination = tmp_path / "source.json"
    destination.write_bytes(b"old-valid")
    calls = 0

    class Incomplete(Response):
        def read(self, size: int = -1) -> bytes:
            raise IncompleteRead(b"partial", len(VALID))

    def opener(_url: str, _timeout: float) -> Response:
        nonlocal calls
        calls += 1
        return Incomplete(VALID) if calls == 1 else Response(VALID)

    receipt = common.download(
        URL, destination, expected_sha256=HASH, opener=opener, sleep=lambda _delay: None
    )
    assert calls == 2 and receipt.sha256 == HASH
    assert_preserved(destination, VALID)


@pytest.mark.parametrize("interruption", [OSError, KeyboardInterrupt])
def test_interrupted_atomic_writer_preserves_valid_prior(
    tmp_path: Path, interruption: type[BaseException]
) -> None:
    destination = tmp_path / "manifest.json"
    destination.write_bytes(VALID)

    def chunks() -> Any:
        yield b"partial"
        raise interruption("synthetic interruption")

    with pytest.raises(interruption):
        common.atomic_write(destination, chunks())
    assert_preserved(destination, VALID)


@pytest.mark.parametrize("stage", ["fsync", "replace", "validate"])
def test_publication_failure_preserves_prior(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stage: str
) -> None:
    destination = tmp_path / "manifest.json"
    destination.write_bytes(VALID)

    def fail(*_args: Any) -> None:
        raise OSError("synthetic publication failure")

    validator = None
    if stage == "validate":
        validator = fail
    else:
        monkeypatch.setattr(common.os, stage, fail)
    with pytest.raises(OSError):
        common.atomic_write(destination, [b"new-content"], validate=validator)
    assert_preserved(destination, VALID)


def test_retry_eventually_succeeds_and_bounds_timeout(tmp_path: Path) -> None:
    calls: list[float] = []
    sleeps: list[float] = []

    def opener(_url: str, timeout: float) -> Response:
        calls.append(timeout)
        if len(calls) < 3:
            raise URLError("synthetic offline")
        return Response(VALID)

    receipt = common.download(
        URL,
        tmp_path / "source.json",
        expected_sha256=HASH,
        timeout=7,
        opener=opener,
        sleep=sleeps.append,
    )
    assert calls == [7, 7, 7]
    assert sleeps == [1, 2]
    assert receipt.sha256 == HASH and receipt.byte_count == len(VALID)
    assert receipt.downloaded_at is not None and not receipt.reused


@pytest.mark.parametrize("code,attempts", [(404, 1), (429, 3), (503, 3)])
def test_http_retry_is_bounded_without_logging_url_secrets(
    tmp_path: Path, code: int, attempts: int
) -> None:
    calls = 0

    def opener(_url: str, _timeout: float) -> Response:
        nonlocal calls
        calls += 1
        raise HTTPError(URL, code, "synthetic-sensitive-marker", {}, None)

    with pytest.raises(common.DownloadError, match=f"{attempts} attempt") as failure:
        common.download(
            URL,
            tmp_path / "source.json",
            expected_sha256=HASH,
            opener=opener,
            sleep=lambda _delay: None,
        )
    assert calls == attempts
    assert "synthetic-sensitive-marker" not in str(failure.value)


@pytest.mark.parametrize(
    "body,length,limit",
    [(b"short", 100, 200), (b"", 0, 100), (VALID, 1, 100), (VALID, len(VALID), 5)],
)
def test_invalid_length_or_size_never_publishes(
    tmp_path: Path, body: bytes, length: int, limit: int
) -> None:
    with pytest.raises(common.DownloadError):
        common.download(
            URL,
            tmp_path / "source.json",
            expected_sha256=HASH,
            opener=response_opener(body, length=length),
            max_bytes=limit,
        )
    assert not (tmp_path / "source.json").exists()


def test_git_blob_pin_checks_exact_bytes_and_cache_is_idempotent(tmp_path: Path) -> None:
    destination = tmp_path / "source.json"
    expected_blob = hashlib.sha1(
        f"blob {len(VALID)}\0".encode() + VALID, usedforsecurity=False
    ).hexdigest()
    first = common.download(
        URL, destination, expected_git_blob=expected_blob, opener=response_opener()
    )
    initial_mtime = destination.stat().st_mtime_ns

    def forbidden(_url: str, _timeout: float) -> Any:
        pytest.fail("Verified cached file must not use the network")

    second = common.download(URL, destination, expected_git_blob=expected_blob, opener=forbidden)
    assert common.git_blob_file(destination) == expected_blob
    assert first.sha256 == second.sha256 == HASH
    assert second.reused and second.downloaded_at is None
    assert destination.stat().st_mtime_ns == initial_mtime
    destination.write_bytes(b"cache-corruption")
    third = common.download(
        URL, destination, expected_git_blob=expected_blob, opener=response_opener()
    )
    assert not third.reused and destination.read_bytes() == VALID


def test_sha_pin_mismatch_even_when_git_pin_matches(tmp_path: Path) -> None:
    pin = hashlib.sha1(f"blob {len(VALID)}\0".encode() + VALID, usedforsecurity=False).hexdigest()
    with pytest.raises(common.DownloadError):
        common.download(
            URL,
            tmp_path / "source.json",
            expected_git_blob=pin,
            expected_sha256="0" * 64,
            opener=response_opener(),
        )


def test_unpinned_requires_validation_and_measures_receipt(tmp_path: Path) -> None:
    destination = tmp_path / "source.json"
    with pytest.raises(common.CorpusError, match="validator"):
        common.download(URL, destination, opener=response_opener())
    receipt = common.download(URL, destination, validate=common.read_json, opener=response_opener())
    assert receipt.sha256 == HASH and receipt.downloaded_at is not None
    with pytest.raises(common.DownloadError):
        common.download(
            URL, destination, validate=common.read_json, opener=response_opener(b"<html>bad</html>")
        )
    assert_preserved(destination, VALID)


def test_equal_atomic_json_is_idempotent(tmp_path: Path) -> None:
    destination = tmp_path / "manifest.json"
    value = {"fixture": "synthetic", "text": "Tiếng Việt"}
    assert common.write_json(destination, value)
    initial_mtime = destination.stat().st_mtime_ns
    assert not common.write_json(destination, value)
    assert destination.stat().st_mtime_ns == initial_mtime
    assert common.read_json(destination) == value


@pytest.mark.parametrize(
    "reference",
    [
        "../qa/eval.jsonl",
        "/absolute",
        "C:/outside",
        "a\\b",
        "a/../b",
        "a//b",
        "./b",
        "file:stream",
        "NUL.txt",
        "COM1",
        "a.",
        "a ",
        "a/%2e%2e/b",
        " a",
        "a\x00b",
    ],
)
def test_unsafe_document_reference_is_rejected(tmp_path: Path, reference: str) -> None:
    with pytest.raises(common.CorpusError):
        common.safe_path(tmp_path, reference)


def test_actual_link_or_windows_junction_cannot_escape_documents(tmp_path: Path) -> None:
    documents = tmp_path / "documents"
    outside = tmp_path / "qa"
    documents.mkdir()
    outside.mkdir()
    (outside / "private.json").write_bytes(VALID)
    junction = documents / "link"
    if os.name == "nt":
        created = subprocess.run(
            ["cmd.exe", "/c", "mklink", "/J", str(junction), str(outside)],
            capture_output=True,
            check=False,
        )
        assert created.returncode == 0, created.stderr.decode(errors="replace")
    else:
        junction.symlink_to(outside, target_is_directory=True)
    try:
        with pytest.raises(common.CorpusError, match="links or junctions"):
            common.safe_path(documents, "link/private.json", must_exist=True)
    finally:
        # Remove the link itself only; never recurse into its target.
        if os.name == "nt":
            junction.rmdir()
        else:
            junction.unlink()
    assert (outside / "private.json").read_bytes() == VALID


@pytest.mark.parametrize(
    "url",
    [
        "https://mirror.example/data.json",
        "file:///data",
        "http://raw.githubusercontent.com/data",
        "https://user:secret@github.com/data",
        "https://github.com:443/data",
        "https://github.com/data?token=private",
        "https://github.com/data#fragment",
    ],
)
def test_unofficial_or_credential_source_url_rejected(url: str) -> None:
    with pytest.raises(common.CorpusError):
        common.check_url(url)


def test_unofficial_response_and_redirect_are_rejected(tmp_path: Path) -> None:
    with pytest.raises(common.DownloadError):
        common.download(
            URL,
            tmp_path / "source.json",
            expected_sha256=HASH,
            opener=response_opener(url="https://mirror.example/data"),
        )
    from urllib.request import Request

    with pytest.raises(common.CorpusError):
        common._OfficialRedirects().redirect_request(
            Request(URL), None, 302, "Found", {}, "https://mirror.example/data"
        )
    assert not (tmp_path / "source.json").exists()


def test_hf_exception_is_exact_url_and_mandatory_published_checksum(tmp_path: Path) -> None:
    common.check_url(common.APPROVED_HF_URL)
    with pytest.raises(common.CorpusError):
        common.check_url(common.APPROVED_HF_URL.replace("distractor", "fullwiki"))
    for pin in (None, "0" * 64):
        with pytest.raises(common.CorpusError, match="published SHA256"):
            common.download(
                common.APPROVED_HF_URL, tmp_path / "source.parquet", expected_sha256=pin,
                validate=lambda _path: None, opener=response_opener(),
            )
    assert list(tmp_path.iterdir()) == []


def test_hf_signed_delivery_is_scoped_and_https_only() -> None:
    signed = "https://us.aws.cdn.hf.co/xet-bridge-us/synthetic?Policy=SYNTHETIC&Signature=SYNTHETIC"
    common._check_response_url(signed, common.APPROVED_HF_URL)
    for url in (
        signed.replace("https:", "http:"), signed.replace("us.aws.cdn.hf.co", "mirror.example"),
        signed.replace("https://", "https://user:secret@"),
    ):
        with pytest.raises(common.CorpusError):
            common._check_response_url(url, common.APPROVED_HF_URL)
    with pytest.raises(common.CorpusError):
        common._check_response_url(signed, URL)


@pytest.mark.parametrize(
    "options",
    [
        {"attempts": 0},
        {"attempts": 6},
        {"timeout": 0},
        {"timeout": 121},
        {"max_bytes": 0},
        {"expected_sha256": "bad"},
        {"expected_git_blob": "bad"},
    ],
)
def test_invalid_download_limits_or_pins_fail_before_io(
    tmp_path: Path, options: dict[str, Any]
) -> None:
    params = {"expected_sha256": HASH, **options}
    with pytest.raises(common.CorpusError):
        common.download(URL, tmp_path / "source.json", **params)
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    "text",
    [
        '{"id":"a","id":"b"}',
        '{"a":NaN}',
        '{"a":Infinity}',
        '{"a":1e400}',
        '{"a":-1e400}',
        "{broken",
    ],
)
def test_ambiguous_or_malformed_json_is_rejected(text: str) -> None:
    with pytest.raises(common.CorpusError):
        common.parse_json(text)


def sample_qa() -> dict[str, Any]:
    return {
        "id": "synthetic_001",
        "domain": "default",
        "question": "Synthetic question?",
        "expected_answers": ["Synthetic answer"],
        "expected_documents": ["synthetic_doc"],
    }


@pytest.mark.parametrize(
    "mutation",
    [
        "unknown",
        "missing",
        "empty_doc",
        "traversal",
        "duplicate",
        "blank_question",
        "empty_answers",
        "blank_answer",
        "empty_qa",
        "bad_jsonl",
    ],
)
def test_invalid_qa_reference_or_common_gold_is_rejected(tmp_path: Path, mutation: str) -> None:
    documents = tmp_path / "documents"
    documents.mkdir()
    (documents / "doc.md").write_text("Synthetic evidence", encoding="utf-8")
    mapping = {"synthetic_doc": "doc.md"}
    records = [sample_qa()]
    if mutation == "unknown":
        records[0]["expected_documents"] = ["unknown"]
    elif mutation == "missing":
        mapping["synthetic_doc"] = "missing.md"
    elif mutation == "empty_doc":
        (documents / "doc.md").write_bytes(b"")
    elif mutation == "traversal":
        mapping["synthetic_doc"] = "../qa/eval.jsonl"
    elif mutation == "duplicate":
        records.append(sample_qa())
    elif mutation == "blank_question":
        records[0]["question"] = " "
    elif mutation == "empty_answers":
        records[0]["expected_answers"] = []
    elif mutation == "blank_answer":
        records[0]["expected_answers"] = [" "]
    elif mutation == "empty_qa":
        records = []
    else:
        qa = tmp_path / "eval.jsonl"
        qa.write_text(json.dumps(sample_qa()) + "\n\n", encoding="utf-8")
        with pytest.raises(common.CorpusError):
            common.validate_qa_records(common.read_jsonl(qa), documents, mapping)
        return
    with pytest.raises(common.CorpusError):
        common.validate_qa_records(records, documents, mapping)


def test_valid_synthetic_jsonl_keeps_gold_and_document_separation(tmp_path: Path) -> None:
    documents = tmp_path / "documents"
    documents.mkdir()
    (documents / "doc.md").write_text("Evidence only", encoding="utf-8")
    qa = tmp_path / "qa.jsonl"
    qa.write_text(json.dumps(sample_qa()) + "\n", encoding="utf-8")
    assert (
        common.validate_qa_records(common.read_jsonl(qa), documents, {"synthetic_doc": "doc.md"})
        == 1
    )
    assert "Synthetic answer" not in (documents / "doc.md").read_text(encoding="utf-8")


def test_committed_metadata_has_no_fabricated_downloads() -> None:
    validate_corpus.validate_metadata()
    for domain in common.DOMAINS:
        manifest = common.read_json(common.CORPUS_ROOT / domain / "manifest.json")
        if domain in {"default", "document"} and manifest["status"] == "ready":
            expected_qa = 100 if domain == "default" else 150
            assert manifest["qa_count"] == expected_qa and manifest["document_count"] > 0
            assert manifest["downloaded_at"] and manifest["artifacts"] and manifest["checksum"]
            continue
        assert manifest["status"] == "not_downloaded"
        assert (
            manifest["document_count"] is manifest["qa_count"] is manifest["downloaded_at"] is None
        )
        assert manifest["checksum"] == {} and manifest["artifacts"] == []


@pytest.mark.parametrize(
    "field,value",
    [
        ("document_count", 0),
        ("qa_count", 100),
        ("downloaded_at", "2026-09-17T00:00:00Z"),
        ("checksum", {"fake": "0" * 64}),
    ],
)
def test_not_downloaded_schema_refuses_fabricated_measurements(field: str, value: Any) -> None:
    manifest = deepcopy(common.read_json(common.CORPUS_ROOT / "default" / "manifest.json"))
    manifest.update(
        status="not_downloaded", document_count=None, qa_count=None, downloaded_at=None,
        checksum={}, artifacts=[],
    )
    manifest[field] = value
    with pytest.raises(common.CorpusError, match="Schema violation"):
        validate_corpus.validate_manifest(manifest)


def test_ready_schema_cannot_claim_acceptance_without_measured_receipts() -> None:
    manifest = deepcopy(common.read_json(common.CORPUS_ROOT / "default" / "manifest.json"))
    manifest.update(document_count=None, qa_count=None, downloaded_at=None, checksum={}, artifacts=[])
    manifest["status"] = "ready"
    with pytest.raises(common.CorpusError, match="Schema violation"):
        validate_corpus.validate_manifest(manifest)


@pytest.mark.parametrize(
    "args",
    [["--all"], ["--domain", "bilingual"]],
)
def test_setup_and_validation_unavailable_fail_without_mutation(args: list[str]) -> None:
    before = {
        path: common.sha256_file(path) for path in common.CORPUS_ROOT.glob("**/manifest.json")
    }
    for name in ("setup_corpus.py", "validate_corpus.py"):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / name), *args], capture_output=True, check=False
        )
        assert result.returncode != 0
        assert b"PASS" not in result.stdout
        assert result.stderr
    assert before == {path: common.sha256_file(path) for path in before}


def test_default_setup_failure_is_honest_without_unit_network(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def offline() -> Any:
        raise common.DownloadError("Synthetic official source transport failure")

    monkeypatch.setattr(prepare_default, "prepare_default", offline)
    assert setup_corpus.main(["--domain", "default"]) == 1
    captured = capsys.readouterr()
    assert "PASS" not in captured.out and "FAIL" in captured.err


def test_metadata_validator_detects_aggregate_and_provenance_drift(tmp_path: Path) -> None:
    names = [
        "source-license-inventory.json",
        "manifest.json",
        *[f"{d}/manifest.json" for d in common.DOMAINS],
    ]
    for name in names:
        destination = tmp_path / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((common.CORPUS_ROOT / name).read_bytes())
    validate_corpus.validate_metadata(tmp_path)
    aggregate = common.read_json(tmp_path / "manifest.json")
    original_count = aggregate["domains"]["default"]["qa_count"]
    aggregate["domains"]["default"]["qa_count"] = 0
    common.write_json(tmp_path / "manifest.json", aggregate)
    with pytest.raises(common.CorpusError, match="Aggregate status/count"):
        validate_corpus.validate_metadata(tmp_path)
    aggregate["domains"]["default"]["qa_count"] = original_count
    common.write_json(tmp_path / "manifest.json", aggregate)
    domain = common.read_json(tmp_path / "default/manifest.json")
    domain["sources"][0]["repository_commit"] = "0" * 40
    common.write_json(tmp_path / "default/manifest.json", domain)
    with pytest.raises(common.CorpusError, match="provenance"):
        validate_corpus.validate_metadata(tmp_path)
