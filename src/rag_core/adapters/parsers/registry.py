"""Copy a verified local source, execute one bounded parser, clean up on every exit."""

import hashlib
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from tempfile import TemporaryDirectory

from rag_core.domain.documents import ParsedDocument, ParseError, ParserLimits, SourceIdentity

FORMATS = {
    ".pdf": ("pdf", "application/pdf"),
    ".docx": ("docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    ".txt": ("txt", "text/plain"),
    ".md": ("md", "text/markdown"),
    ".html": ("html", "text/html"),
    ".htm": ("html", "text/html"),
}


class ParserRegistry:
    def __init__(self, temp_root: Path, limits: ParserLimits | None = None) -> None:
        self.limits = limits or ParserLimits()
        self.temp_root = temp_root
        # A registry is shared by the worker; never create an unbounded CPU queue.
        self._slot = threading.BoundedSemaphore(1)

    def parse(
        self, path: Path, *, filename: str, content_type: str, source: SourceIdentity
    ) -> ParsedDocument:
        extension = Path(filename).suffix.lower()
        selected = FORMATS.get(extension)
        if selected is None:
            raise ParseError("unsupported_format")
        if content_type.split(";", 1)[0].strip().lower() != selected[1]:
            raise ParseError("mime_mismatch")
        if not self._slot.acquire(blocking=False):
            raise ParseError("parser_busy")
        started = time.monotonic()
        try:
            self.temp_root.mkdir(parents=True, exist_ok=True)
            with TemporaryDirectory(prefix="parse-", dir=self.temp_root) as directory:
                sandbox = Path(directory)
                local = sandbox / ("source" + extension)
                digest = hashlib.sha256()
                size = 0
                with path.open("rb") as original, local.open("xb") as target:
                    while data := original.read(1024 * 1024):
                        size += len(data)
                        if size > self.limits.max_bytes:
                            raise ParseError("source_too_large")
                        self._remaining(started)
                        digest.update(data)
                        target.write(data)
                if digest.hexdigest() != source.sha256:
                    raise ParseError("source_changed")
                request = sandbox / "request.json"
                request.write_text(
                    json.dumps(
                        {
                            "format": selected[0],
                            "source": source.model_dump(mode="json"),
                            "limits": self.limits.model_dump(),
                            "input": local.name,
                        }
                    ),
                    encoding="utf-8",
                )
                # No backend stdout/stderr is allowed to leak untrusted source data.
                environment = os.environ.copy()
                environment.update(
                    {name: str(sandbox.resolve()) for name in ("TMP", "TEMP", "TMPDIR")}
                )
                with subprocess.Popen(
                    [
                        sys.executable,
                        "-m",
                        "rag_core.adapters.parsers.worker",
                        str(request.resolve()),
                    ],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    env=environment,
                ) as process:
                    try:
                        process.wait(timeout=self._remaining(started))
                    except (subprocess.TimeoutExpired, ParseError):
                        process.kill()
                        process.wait()
                        raise ParseError("parser_timeout") from None
                    except BaseException:
                        process.kill()
                        process.wait()
                        raise
                result = sandbox / "result.json"
                if process.returncode != 0 or not result.is_file():
                    raise ParseError("parser_failed")
                if result.stat().st_size > self.limits.max_result_bytes:
                    raise ParseError("extraction_limit")
                payload = json.loads(result.read_text(encoding="utf-8"))
                if "error" in payload:
                    raise ParseError(payload["error"])
                parsed = ParsedDocument.model_validate(payload)
                if parsed.source != source:
                    raise ParseError("source_changed")
                self._remaining(started)
                return parsed
        except ParseError:
            raise
        except (OSError, ValueError):
            raise ParseError("parser_failed") from None
        finally:
            self._slot.release()

    def _remaining(self, started: float) -> float:
        remaining = self.limits.timeout_seconds - (time.monotonic() - started)
        if remaining <= 0:
            raise ParseError("parser_timeout")
        return remaining
