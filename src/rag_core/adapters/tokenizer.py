"""Offline, checksum-verified BGE-M3 tokenizer. Never downloads during ingestion."""

import hashlib
from importlib.metadata import version
from pathlib import Path

from tokenizers import Tokenizer  # type: ignore[import-untyped]

BGE_MODEL = "BAAI/bge-m3"
BGE_REVISION = "5617a9f61b028005a4858fdac845db406aefb181"
BGE_SHA256 = "21106b6d7dab2952c1d496fb21d5dc9db75c28ed361a05f5020bbba27810dd08"
TOKENIZERS_VERSION = "0.22.2"
DEFAULT_TOKENIZER_PATH = Path(".local/tokenizers/bge-m3/tokenizer.json")


class BgeM3Tokenizer:
    def __init__(self, path: Path = DEFAULT_TOKENIZER_PATH) -> None:
        if version("tokenizers") != TOKENIZERS_VERSION:
            raise ValueError("tokenizer_runtime_mismatch")
        if path.stat().st_size > 32 * 1024 * 1024:
            raise ValueError("tokenizer_artifact_too_large")
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != BGE_SHA256:
            raise ValueError("tokenizer_checksum_mismatch")
        self._tokenizer = Tokenizer.from_str(data.decode("utf-8"))
        self._tokenizer.no_truncation()
        self._tokenizer.no_padding()

    @property
    def fingerprint(self) -> str:
        return f"{BGE_MODEL}@{BGE_REVISION}/{BGE_SHA256}/tokenizers-{TOKENIZERS_VERSION}"

    def count(self, text: str, *, special_tokens: bool = True) -> int:
        return len(self._tokenizer.encode(text, add_special_tokens=special_tokens).ids)

    def boundaries(self, text: str) -> tuple[int, ...]:
        encoding = self._tokenizer.encode(text, add_special_tokens=False)
        # Normalization can give multiple tokens the same source character span.
        # Slice the original string, never decode IDs or slice UTF-8 bytes.
        return tuple(sorted({0, len(text), *(end for _, end in encoding.offsets)}))
