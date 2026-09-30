"""Storage read contract. Authorization of an upload belongs to the app and T12."""

from contextlib import AbstractContextManager
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class SourceObject:
    storage_alias: str
    bucket: str
    key: str
    version_id: str | None = None
    sha256: str | None = None


@dataclass(frozen=True)
class DownloadedSource:
    path: Path
    size: int
    sha256: str
    version_id: str | None


class StorageError(Exception):
    """Safe error code; provider details and credentials are never exposed."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class StorageReader(Protocol):
    def read(self, app_id: str, source: SourceObject) -> AbstractContextManager[DownloadedSource]: ...
