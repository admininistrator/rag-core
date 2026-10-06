"""Bounded provisional answer decoding; citation-shaped text is never emitted unchecked."""

import json
import re
from typing import Annotated

from pydantic import Field

from rag_core.domain.answers import AnswerError
from rag_core.domain.query import FrozenModel


class StreamPolicy(FrozenModel):
    concurrency: Annotated[int, Field(strict=True, ge=1, le=20)] = 4
    queue_size: Annotated[int, Field(strict=True, ge=0, le=20)] = 8
    queue_timeout: Annotated[float, Field(strict=True, gt=0, le=30)] = 5.0
    buffer_events: Annotated[int, Field(strict=True, ge=1, le=8)] = 2
    heartbeat_seconds: Annotated[float, Field(strict=True, gt=0, le=30)] = 10.0
    send_timeout: Annotated[float, Field(strict=True, gt=0, le=30)] = 5.0
    total_timeout: Annotated[float, Field(strict=True, gt=0, le=300)] = 120.0
    sentence_chars: Annotated[int, Field(strict=True, ge=64, le=8192)] = 4096


class ProvisionalAnswer:
    """Decode the first JSON answer string incrementally, including escaped Unicode.

    Streaming policy asks for answer first. Other legal JSON field orders defer
    deltas until final validation; they do not grant a second generation attempt.
    Full wire text stays bounded to the same 64KiB T24 JSON limit.
    """

    def __init__(self, allowed_ids: set[str], sentence_chars: int = 4096) -> None:
        self.allowed_ids = allowed_ids
        self.limit = sentence_chars
        self.raw = ""
        self.size = 0
        self.position: int | None = None
        self.closed = False
        self.deferred = False
        self.pending = ""
        self.text = ""
        self.high_surrogate: int | None = None

    def feed(self, fragment: str) -> list[str]:
        self.size += len(fragment.encode("utf-8"))
        if self.size > 65536:
            raise AnswerError("invalid_citation")
        self.raw += fragment
        if self.closed or self.deferred:
            return []
        if self.position is None:
            match = re.match(r'^\s*\{\s*"answer"\s*:\s*"', self.raw)
            if match is None:
                if len(self.raw) > 128:
                    self.deferred = True
                return []
            self.position = match.end()
        output = []
        while self.position < len(self.raw):
            index = self.position
            char = self.raw[index]
            if char == '"':
                if self.high_surrogate is not None:
                    raise AnswerError("invalid_citation")
                self.closed = True
                self.position += 1
                break
            if char == "\\":
                if index + 1 == len(self.raw):
                    break
                escape = self.raw[index + 1]
                width = 6 if escape == "u" else 2
                if index + width > len(self.raw):
                    break
                try:
                    char = json.loads('"' + self.raw[index : index + width] + '"')
                except ValueError:
                    raise AnswerError("invalid_citation") from None
                self.position += width
            else:
                if ord(char) < 32:
                    raise AnswerError("invalid_citation")
                self.position += 1
            code = ord(char)
            if 0xD800 <= code <= 0xDBFF:
                if self.high_surrogate is not None:
                    raise AnswerError("invalid_citation")
                self.high_surrogate = code
                continue
            if self.high_surrogate is not None:
                if not 0xDC00 <= code <= 0xDFFF:
                    raise AnswerError("invalid_citation")
                char = chr(0x10000 + ((self.high_surrogate - 0xD800) << 10) + code - 0xDC00)
                self.high_surrogate = None
            elif 0xDC00 <= code <= 0xDFFF:
                raise AnswerError("invalid_citation")
            self.pending += char
            self.text += char
            if len(self.pending) > self.limit:
                raise AnswerError("invalid_citation")
            # Boundaries inside an unfinished bracket cannot split a citation ID.
            if char in "\n\r" or (
                char.isspace() and len(self.pending) > 1 and self.pending[-2] in ".!?"
            ):
                if self.pending.rfind("[") > self.pending.rfind("]"):
                    continue
                output.append(self._flush())
        return output

    def _flush(self) -> str:
        markers = re.findall(r"\[([ce][^\]]*)\]", self.pending, flags=re.IGNORECASE)
        if not set(markers) <= self.allowed_ids or re.search(
            r"\[[ce][^\]]*$", self.pending, flags=re.IGNORECASE
        ):
            raise AnswerError("invalid_citation")
        result, self.pending = self.pending, ""
        return result

    def finish(self) -> list[str]:
        if not self.closed and not self.deferred:
            # A differently ordered short JSON answer is legal at the final gate.
            self.deferred = True
        return [self._flush()] if self.pending else []
