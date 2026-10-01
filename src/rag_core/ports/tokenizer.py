"""Embedding tokenization port; no model, framework or network dependency."""

from typing import Protocol


class EmbeddingTokenizer(Protocol):
    @property
    def fingerprint(self) -> str: ...

    def count(self, text: str, *, special_tokens: bool = True) -> int: ...

    def boundaries(self, text: str) -> tuple[int, ...]:
        """Original Unicode character boundaries supplied by the real tokenizer."""
        ...
