"""S3 reader with operator-owned routing and immutable, bounded downloads."""

import hashlib
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Self
from urllib.parse import urlsplit

import boto3  # type: ignore[import-untyped]
from botocore.config import Config  # type: ignore[import-untyped]
from botocore.exceptions import BotoCoreError, ClientError  # type: ignore[import-untyped]
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from rag_core.ports.storage import DownloadedSource, SourceObject, StorageError


class StorageLocation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)

    app_id: str = Field(min_length=1, max_length=256)
    alias: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
    endpoint: str = Field(min_length=1, max_length=2048, repr=False)
    region: str = Field(min_length=1, max_length=128)
    bucket: str = Field(min_length=3, max_length=63)
    prefix: str = Field(min_length=1, max_length=1024)
    access_key_file: Path = Field(repr=False)
    secret_key_file: Path = Field(repr=False)
    allow_loopback_http: bool = False
    # Exact local Compose service name only; never an arbitrary internal hostname.
    allow_compose_http: bool = False
    max_bytes: int = Field(default=100 * 1024 * 1024, gt=0, le=1024 * 1024 * 1024)
    timeout_seconds: int = Field(default=10, ge=1, le=60)

    @model_validator(mode="after")
    def validate_location(self) -> Self:
        url = urlsplit(self.endpoint)
        local = self.allow_loopback_http and url.hostname in {"127.0.0.1", "::1"}
        local = local or (self.allow_compose_http and url.hostname == "minio" and url.port == 9000)
        if (
            not url.hostname
            or (url.scheme != "https" and not (url.scheme == "http" and local))
            or url.username is not None
            or url.password is not None
            or url.query
            or url.fragment
            or url.path not in {"", "/"}
        ):
            raise ValueError("storage endpoint must be HTTPS or explicit loopback HTTP origin")
        _ = url.port
        if not _safe_key(self.prefix, prefix=True):
            raise ValueError("invalid storage prefix")
        if not self.prefix.endswith("/"):
            raise ValueError("storage prefix must end with /")
        return self


class StorageRegistry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)
    locations: tuple[StorageLocation, ...] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def unique_locations(self) -> Self:
        keys = [(location.app_id, location.alias) for location in self.locations]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate app storage alias")
        return self


def _safe_key(key: str, *, prefix: bool = False) -> bool:
    if (
        not key
        or key.startswith("/")
        or "\\" in key
        or "://" in key
        or "%" in key
        or any(ord(char) < 32 or ord(char) == 127 for char in key)
    ):
        return False
    segments = key.rstrip("/").split("/") if prefix else key.split("/")
    return bool(segments) and all(segment not in {"", ".", ".."} for segment in segments)


def load_storage_registry(path: Path, *, production: bool = False) -> StorageRegistry:
    try:
        if path.stat().st_size > 262144:
            raise ValueError("oversized registry")
        registry = StorageRegistry.model_validate_json(path.read_bytes())
        if production and any(location.allow_loopback_http or location.allow_compose_http
                              for location in registry.locations):
            raise ValueError("development transport in production")
        return registry
    except (OSError, ValueError, ValidationError):
        raise StorageError("invalid_storage_config") from None


class S3StorageReader:
    """Only exposes HEAD and GET; clients and aliases are fixed by operator config."""

    def __init__(self, registry: StorageRegistry, *, temp_dir: Path | None = None) -> None:
        self._locations = {(item.app_id, item.alias): item for item in registry.locations}
        self._clients: dict[tuple[str, str], Any] = {}
        self._temp_dir = temp_dir

    def _client(self, location: StorageLocation) -> Any:
        identifier = (location.app_id, location.alias)
        if identifier not in self._clients:
            try:
                access_key = location.access_key_file.read_text(encoding="ascii").strip()
                secret_key = location.secret_key_file.read_text(encoding="ascii").strip()
                if not access_key or not secret_key:
                    raise ValueError("empty credential")
                client = boto3.client(
                    "s3",
                    endpoint_url=location.endpoint,
                    region_name=location.region,
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    config=Config(
                        signature_version="s3v4",
                        s3={"addressing_style": "path"},
                        connect_timeout=location.timeout_seconds,
                        read_timeout=location.timeout_seconds,
                        retries={"max_attempts": 1},
                    ),
                )
                expected = urlsplit(location.endpoint)

                def enforce_endpoint(request: Any, **_kwargs: Any) -> None:
                    actual = urlsplit(request.url)
                    if (actual.scheme, actual.hostname, actual.port) != (
                        expected.scheme,
                        expected.hostname,
                        expected.port,
                    ):
                        raise StorageError("storage_forbidden")

                client.meta.events.register("before-send.s3", enforce_endpoint)
                def reject_redirect(response: Any = None, **_kwargs: Any) -> None:
                    if response is not None and 300 <= response[0].status_code < 400:
                        raise StorageError("storage_forbidden")

                client.meta.events.register_first("needs-retry.s3", reject_redirect)
                self._clients[identifier] = client
            except (OSError, ValueError):
                raise StorageError("storage_unavailable") from None
        return self._clients[identifier]

    @contextmanager
    def read(self, app_id: str, source: SourceObject) -> Iterator[DownloadedSource]:
        location = self._locations.get((app_id, source.storage_alias))
        if location is None or source.bucket != location.bucket:
            raise StorageError("storage_forbidden")
        if not _safe_key(source.key) or not source.key.startswith(location.prefix):
            raise StorageError("storage_forbidden")
        if source.version_id is None and source.sha256 is None:
            raise StorageError("source_unpinned")
        if source.sha256 is not None and (
            len(source.sha256) != 64 or any(c not in "0123456789abcdefABCDEF" for c in source.sha256)
        ):
            raise StorageError("invalid_source")

        client = self._client(location)
        version = {"VersionId": source.version_id} if source.version_id else {}
        path: Path | None = None
        response: Any = None
        try:
            head = client.head_object(Bucket=location.bucket, Key=source.key, **version)
            if source.version_id and head.get("VersionId") != source.version_id:
                raise StorageError("source_changed")
            if head["ContentLength"] > location.max_bytes:
                raise StorageError("source_too_large")
            get_args = {**version, "IfMatch": head["ETag"]}
            response = client.get_object(Bucket=location.bucket, Key=source.key, **get_args)
            if source.version_id and response.get("VersionId") != source.version_id:
                raise StorageError("source_changed")
            digest = hashlib.sha256()
            size = 0
            with tempfile.NamedTemporaryFile(dir=self._temp_dir, delete=False) as temp:
                path = Path(temp.name)
                while True:
                    chunk = response["Body"].read(1024 * 1024)
                    if not chunk:
                        break
                    size += len(chunk)
                    if size > location.max_bytes:
                        raise StorageError("source_too_large")
                    digest.update(chunk)
                    temp.write(chunk)
            if size != head["ContentLength"] or size != response["ContentLength"]:
                raise StorageError("source_changed")
            sha256 = digest.hexdigest()
            if source.sha256 and sha256 != source.sha256.lower():
                raise StorageError("source_changed")
            if not source.version_id:
                after = client.head_object(Bucket=location.bucket, Key=source.key)
                if after["ETag"] != head["ETag"] or after["ContentLength"] != size:
                    raise StorageError("source_changed")
            yield DownloadedSource(path, size, sha256, source.version_id)
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "")
            if code in {"PreconditionFailed", "412", "NoSuchVersion"}:
                raise StorageError("source_changed") from None
            raise StorageError("storage_unavailable") from None
        except (BotoCoreError, OSError):
            raise StorageError("storage_unavailable") from None
        finally:
            if response is not None:
                response["Body"].close()
            if path is not None:
                path.unlink(missing_ok=True)
