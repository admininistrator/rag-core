"""Synchronous CPU boundary: future async callers must offload this port."""

from pathlib import Path
from threading import Event
from typing import Protocol

from rag_core.domain.documents import ParsedDocument, SourceIdentity


class DocumentParser(Protocol):
    def parse(
        self,
        path: Path,
        *,
        filename: str,
        content_type: str,
        source: SourceIdentity,
        cancel: Event | None = None,
    ) -> ParsedDocument: ...
