"""Shared corpus I/O. No model, application storage, or production index access."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import tempfile
import time
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from http.client import IncompleteRead
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

DOMAINS = ("default", "document", "bilingual")
CORPUS_ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_HOSTS = frozenset(
    {"raw.githubusercontent.com", "github.com", "api.github.com", "curtis.ml.cmu.edu"}
)
_WINDOWS_RESERVED = re.compile(r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)", re.I)


class CorpusError(ValueError):
    """Invalid corpus metadata/content or unsafe operation."""


class DownloadError(CorpusError):
    """A bounded download failed; the previously published file is preserved."""


def safe_path(root: Path, reference: str, *, must_exist: bool = False) -> Path:
    """Resolve a portable relative reference, rejecting traversal and links/junctions."""
    if not isinstance(reference, str) or not reference or reference != reference.strip():
        raise CorpusError("Reference must be a nonempty relative path")
    parts = reference.split("/")
    if (
        PurePosixPath(reference).is_absolute()
        or "\\" in reference
        or any(ord(c) < 32 for c in reference)
        or any(c in reference for c in ':?*<>|"%')
        or any(
            part in {"", ".", ".."} or part.endswith((".", " ")) or _WINDOWS_RESERVED.match(part)
            for part in parts
        )
    ):
        raise CorpusError("Unsafe corpus reference")
    resolved_root = root.resolve(strict=True)
    candidate = resolved_root.joinpath(*parts)
    cursor = resolved_root
    for part in parts:
        cursor /= part
        if cursor.is_symlink() or cursor.is_junction():
            raise CorpusError("Corpus references cannot traverse links or junctions")
    if not candidate.resolve().is_relative_to(resolved_root):
        raise CorpusError("Corpus reference escapes its root")
    if must_exist and (not candidate.is_file() or candidate.stat().st_size == 0):
        raise CorpusError("Referenced corpus file is missing or empty")
    return candidate


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_blob_file(path: Path) -> str:
    """Git blob identity is SHA1('blob ' + byte size + NUL + exact bytes)."""
    digest = hashlib.sha1(usedforsecurity=False)
    digest.update(f"blob {path.stat().st_size}\0".encode("ascii"))
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CorpusError("Duplicate JSON object key")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise CorpusError(f"Nonfinite JSON constant: {value}")


def _finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise CorpusError("JSON number exceeds the finite float range")
    return number


def parse_json(text: str) -> Any:
    try:
        return json.loads(
            text,
            object_pairs_hook=_no_duplicate_keys,
            parse_constant=_reject_constant,
            parse_float=_finite_float,
        )
    except json.JSONDecodeError as exc:
        raise CorpusError(f"Invalid JSON at line {exc.lineno}, column {exc.colno}") from None


def read_json(path: Path) -> Any:
    try:
        return parse_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError):
        raise CorpusError("JSON file is missing, unreadable, or not UTF-8") from None


def read_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    try:
        with path.open(encoding="utf-8") as stream:
            for number, line in enumerate(stream, 1):
                if not line.strip():
                    raise CorpusError(f"Empty JSONL record at line {number}")
                record = parse_json(line)
                if not isinstance(record, dict):
                    raise CorpusError(f"JSONL record must be an object at line {number}")
                yield record
    except (OSError, UnicodeError):
        raise CorpusError("JSONL file is missing, unreadable, or not UTF-8") from None


def atomic_write(
    destination: Path,
    chunks: Iterable[bytes],
    *,
    validate: Callable[[Path], None] | None = None,
) -> bool:
    """Stage, fsync, validate, then replace once. Equal bytes leave the old mtime intact.

    Returns whether publication changed bytes. Exceptions (including interruption)
    remove only this call's temporary file and leave the old destination untouched.
    Atomicity is per file; domain generation publication belongs to domain tasks.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".part", dir=destination.parent
    )
    staged = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            for chunk in chunks:
                if not isinstance(chunk, bytes):
                    raise CorpusError("Atomic writer requires byte chunks")
                stream.write(chunk)
            stream.flush()
            os.fsync(stream.fileno())
        if validate:
            validate(staged)
        if destination.is_file() and sha256_file(destination) == sha256_file(staged):
            return False
        os.replace(staged, destination)
        return True
    finally:
        staged.unlink(missing_ok=True)


def write_json(
    destination: Path, value: Any, *, validate: Callable[[Path], None] | None = None
) -> bool:
    try:
        content = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode(
            "utf-8"
        )
    except (TypeError, ValueError):
        raise CorpusError("Value cannot be encoded as finite JSON") from None
    return atomic_write(destination, [content], validate=validate)


def check_url(url: str, allowed_hosts: frozenset[str] = OFFICIAL_HOSTS) -> None:
    """Allow only official hosts. The legacy CMU dataset endpoint alone permits HTTP."""
    parsed = urlsplit(url)
    if (
        parsed.hostname not in allowed_hosts
        or parsed.username
        or parsed.password
        or parsed.port is not None
        or parsed.query
        or parsed.fragment
        or parsed.scheme not in {"https", "http"}
        or (parsed.scheme == "http" and parsed.hostname != "curtis.ml.cmu.edu")
    ):
        raise CorpusError("Source URL is outside the official corpus allowlist")


class _OfficialRedirects(HTTPRedirectHandler):
    def redirect_request(
        self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str
    ) -> Any:
        check_url(newurl)
        if urlsplit(req.full_url).scheme == "https" and urlsplit(newurl).scheme != "https":
            raise CorpusError("Source redirect cannot downgrade HTTPS")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _open_source(url: str, timeout: float) -> Any:
    opener = build_opener(_OfficialRedirects())
    return opener.open(Request(url, headers={"User-Agent": "rag-core-corpus/1"}), timeout=timeout)


@dataclass(frozen=True)
class DownloadReceipt:
    url: str
    sha256: str
    byte_count: int
    downloaded_at: str | None
    reused: bool


def download(
    url: str,
    destination: Path,
    *,
    expected_sha256: str | None = None,
    expected_git_blob: str | None = None,
    validate: Callable[[Path], None] | None = None,
    timeout: float = 30,
    attempts: int = 3,
    max_bytes: int = 128 * 1024 * 1024,
    opener: Callable[[str, float], Any] = _open_source,
    sleep: Callable[[float], None] = time.sleep,
) -> DownloadReceipt:
    """Bounded streamed download with pin/content checks BEFORE publication.

    A source without an upstream hash needs a semantic validator; its first receipt
    supplies a measured SHA256 for future pins. An unpinned existing file is fetched
    again (its unchanged bytes still preserve mtime), never silently trusted.
    """
    check_url(url)
    for pin, length in ((expected_sha256, 64), (expected_git_blob, 40)):
        if pin is not None and not re.fullmatch(rf"[0-9a-f]{{{length}}}", pin):
            raise CorpusError("Invalid checksum pin")
    if not (expected_sha256 or expected_git_blob or validate):
        raise CorpusError("An upstream pin or semantic content validator is required")
    if not 1 <= attempts <= 5 or not 0 < timeout <= 120 or max_bytes <= 0:
        raise CorpusError("Invalid bounded download configuration")

    def verify(path: Path) -> None:
        if not 0 < path.stat().st_size <= max_bytes:
            raise CorpusError("Source byte count is empty or exceeds its limit")
        if expected_sha256 and sha256_file(path) != expected_sha256:
            raise CorpusError("Source SHA256 does not match its pin")
        if expected_git_blob and git_blob_file(path) != expected_git_blob:
            raise CorpusError("Source Git blob does not match its pin")
        if validate:
            validate(path)

    if destination.is_file() and (expected_sha256 or expected_git_blob):
        try:
            verify(destination)
        except CorpusError:
            pass
        else:
            return DownloadReceipt(
                url, sha256_file(destination), destination.stat().st_size, None, True
            )

    for attempt in range(1, attempts + 1):
        try:
            with opener(url, timeout) as response:
                check_url(response.geturl())
                if (
                    urlsplit(url).scheme == "https"
                    and urlsplit(response.geturl()).scheme != "https"
                ):
                    raise CorpusError("Source response downgraded HTTPS")
                if response.status != 200:
                    raise CorpusError("Source response status is not 200")
                length_header = response.headers.get("Content-Length")
                advertised = int(length_header) if length_header is not None else None
                if advertised is not None and not 0 < advertised <= max_bytes:
                    raise CorpusError("Invalid source Content-Length")

                def chunks(advertised_length: int | None = advertised) -> Iterable[bytes]:
                    received = 0
                    while block := response.read(1024 * 1024):
                        received += len(block)
                        if received > max_bytes:
                            raise CorpusError("Source exceeds its byte limit")
                        yield block
                    if advertised_length is not None and received != advertised_length:
                        raise CorpusError("Source stream is truncated or has excess bytes")

                atomic_write(destination, chunks(), validate=verify)
            return DownloadReceipt(
                url,
                sha256_file(destination),
                destination.stat().st_size,
                datetime.now(UTC).isoformat(),
                False,
            )
        except HTTPError as exc:
            retryable = exc.code in {408, 429, 500, 502, 503, 504}
            reason = f"HTTP {exc.code}"
            exc.close()
        except (URLError, TimeoutError, ConnectionError, IncompleteRead):
            retryable, reason = True, "source transport failure"
        except (CorpusError, OSError, ValueError):
            retryable, reason = False, "source verification or local publication failure"
        if not retryable or attempt == attempts:
            raise DownloadError(f"Download failed after {attempt} attempt(s): {reason}") from None
        sleep(min(2 ** (attempt - 1), 4))
    raise AssertionError("Unreachable bounded download state")


def validate_qa_records(
    records: Iterable[Mapping[str, Any]], documents_root: Path, document_paths: Mapping[str, str]
) -> int:
    """Common checks only; original gold/domain/page/alignment checks belong to T05-T07.

    Document IDs map to paths relative to documents/, never to raw/ or qa/.
    All mapped documents and every expected document must exist and be nonempty.
    """
    for document_id, reference in document_paths.items():
        if not isinstance(document_id, str) or not document_id.strip():
            raise CorpusError("Document ID must be nonempty")
        safe_path(documents_root, reference, must_exist=True)
    identifiers: set[str] = set()
    count = 0
    for record in records:
        identifier = record.get("id")
        if not isinstance(identifier, str) or not identifier.strip() or identifier in identifiers:
            raise CorpusError("QA ID must be nonempty and unique")
        identifiers.add(identifier)
        if record.get("domain") not in DOMAINS:
            raise CorpusError("Unknown corpus domain")
        question = record.get("question")
        answers = record.get("expected_answers")
        expected = record.get("expected_documents")
        if not isinstance(question, str) or not question.strip():
            raise CorpusError("QA question must be nonempty")
        if (
            not isinstance(answers, list)
            or not answers
            or any(not isinstance(answer, str) or not answer.strip() for answer in answers)
        ):
            raise CorpusError("QA expected answers must be nonempty strings")
        if (
            not isinstance(expected, list)
            or not expected
            or any(not isinstance(doc, str) or doc not in document_paths for doc in expected)
        ):
            raise CorpusError("QA references an unknown document")
        if len(expected) != len(set(expected)):
            raise CorpusError("QA expected documents must be unique")
        count += 1
    if count == 0:
        raise CorpusError("QA corpus contains no records")
    return count
