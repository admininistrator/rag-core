"""T11 acceptance against the isolated real MinIO fixture and two IAM users."""

import hashlib
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from uuid import uuid4

import boto3
import pytest
from botocore.exceptions import ClientError
from pydantic import ValidationError

from rag_core.adapters.storage.s3 import S3StorageReader, StorageLocation, StorageRegistry
from rag_core.ports.storage import SourceObject, StorageError

BUCKET = "rag-core-storage-test"
SECRET_DIR = Path(".local/secrets")


def _secret(name: str) -> str:
    path = SECRET_DIR / name
    if not path.is_file():
        pytest.fail(f"Missing ignored {path}; run scripts/bootstrap_storage_test.ps1")
    return path.read_text(encoding="ascii").strip()


def _client(role: str):
    return boto3.client(
        "s3",
        endpoint_url="http://127.0.0.1:9000",
        region_name="us-east-1",
        aws_access_key_id=_secret(f"minio_{role}_user"),
        aws_secret_access_key=_secret(f"minio_{role}_password"),
    )


@pytest.fixture
def storage(tmp_path: Path):
    location = StorageLocation(
        app_id="test-app",
        alias="test-store",
        endpoint="http://127.0.0.1:9000",
        region="us-east-1",
        bucket=BUCKET,
        prefix="allowed/",
        access_key_file=SECRET_DIR / "minio_reader_user",
        secret_key_file=SECRET_DIR / "minio_reader_password",
        allow_loopback_http=True,
        max_bytes=64,
    )
    reader = S3StorageReader(StorageRegistry(locations=(location,)), temp_dir=tmp_path)
    uploader = _client("uploader")
    key = f"allowed/t11-{uuid4().hex}.txt"
    try:
        yield reader, uploader, key, tmp_path
    finally:
        versions = uploader.list_object_versions(Bucket=BUCKET, Prefix=key)
        for entry in (*versions.get("Versions", []), *versions.get("DeleteMarkers", [])):
            if entry["Key"] == key:
                uploader.delete_object(Bucket=BUCKET, Key=key, VersionId=entry["VersionId"])


@pytest.mark.integration
def test_real_read_and_reader_iam(storage) -> None:
    reader, uploader, key, temp = storage
    payload = b"T11 immutable source\n"
    uploader.put_object(Bucket=BUCKET, Key=key, Body=payload)
    original = hashlib.sha256(uploader.get_object(Bucket=BUCKET, Key=key)["Body"].read()).hexdigest()
    source = SourceObject("test-store", BUCKET, key, sha256=original)
    with reader.read("test-app", source) as item:
        assert item.path.read_bytes() == payload
        assert item.size == len(payload)
        assert item.sha256 == original
    assert list(temp.iterdir()) == []

    core = _client("reader")
    for operation in (
        lambda: core.put_object(Bucket=BUCKET, Key=key, Body=b"overwrite"),
        lambda: core.delete_object(Bucket=BUCKET, Key=key),
    ):
        with pytest.raises(ClientError) as denied:
            operation()
        assert denied.value.response["Error"]["Code"] == "AccessDenied"
    actual = hashlib.sha256(uploader.get_object(Bucket=BUCKET, Key=key)["Body"].read()).hexdigest()
    assert actual == original
    with pytest.raises(ClientError) as denied_prefix:
        core.get_object(Bucket=BUCKET, Key="outside/fixture")
    assert denied_prefix.value.response["Error"]["Code"] == "AccessDenied"


@pytest.mark.integration
def test_real_version_id_pins_old_bytes(storage) -> None:
    reader, uploader, key, _ = storage
    old = b"version one"
    version_id = uploader.put_object(Bucket=BUCKET, Key=key, Body=old)["VersionId"]
    uploader.put_object(Bucket=BUCKET, Key=key, Body=b"version two")
    with reader.read("test-app", SourceObject("test-store", BUCKET, key, version_id)) as item:
        assert item.path.read_bytes() == old
        assert item.sha256 == hashlib.sha256(old).hexdigest()


@pytest.mark.integration
def test_scope_change_size_and_interrupted_stream(storage, monkeypatch: pytest.MonkeyPatch) -> None:
    reader, uploader, key, temp = storage
    original = b"first content"
    uploader.put_object(Bucket=BUCKET, Key=key, Body=original)
    pinned = SourceObject("test-store", BUCKET, key, sha256=hashlib.sha256(original).hexdigest())
    for forbidden in (
        SourceObject("other", BUCKET, key, sha256=pinned.sha256),
        SourceObject("test-store", BUCKET, "allowed/../escape", sha256=pinned.sha256),
        SourceObject("test-store", BUCKET, "allowed/%2e%2e/escape", sha256=pinned.sha256),
        SourceObject("test-store", BUCKET, "outside/file", sha256=pinned.sha256),
        SourceObject("test-store", "other-bucket", key, sha256=pinned.sha256),
    ):
        with pytest.raises(StorageError) as error, reader.read("test-app", forbidden):
            pass
        assert error.value.code == "storage_forbidden"

    uploader.put_object(Bucket=BUCKET, Key=key, Body=b"changed content")
    with pytest.raises(StorageError) as changed, reader.read("test-app", pinned):
        pass
    assert changed.value.code == "source_changed"
    uploader.put_object(Bucket=BUCKET, Key=key, Body=b"x" * 65)
    with pytest.raises(StorageError) as large, reader.read("test-app", pinned):
        pass
    assert large.value.code == "source_too_large"

    uploader.put_object(Bucket=BUCKET, Key=key, Body=original)
    client = reader._client(reader._locations[("test-app", "test-store")])
    real_get = client.get_object

    class BrokenBody:
        def __init__(self, wrapped):
            self.wrapped = wrapped
            self.reads = 0

        def read(self, count):
            self.reads += 1
            if self.reads > 1:
                raise OSError("simulated interrupted transport")
            return self.wrapped.read(count)

        def close(self):
            self.wrapped.close()

    def interrupted_get(**kwargs):
        result = real_get(**kwargs)
        result["Body"] = BrokenBody(result["Body"])
        return result

    monkeypatch.setattr(client, "get_object", interrupted_get)
    with pytest.raises(StorageError) as interrupted, reader.read("test-app", pinned):
        pass
    assert interrupted.value.code == "storage_unavailable"
    assert list(temp.iterdir()) == []


@pytest.mark.integration
def test_operator_endpoint_and_redirect_guard(storage) -> None:
    reader, _, _, _ = storage
    location = reader._locations[("test-app", "test-store")]
    for endpoint in (
        "http://example.com",
        "http://user:password@127.0.0.1:9000",
        "http://127.0.0.1:9000/other",
        "http://127.0.0.1:9000?redirect=https://evil.example",
    ):
        with pytest.raises(ValidationError):
            StorageLocation.model_validate({**location.model_dump(), "endpoint": endpoint})
    client = reader._client(location)
    with pytest.raises(StorageError) as redirect:
        client.meta.events.emit(
            "before-send.s3.GetObject",
            request=type("Request", (), {"url": "https://redirect.example/bucket/key"})(),
        )
    assert redirect.value.code == "storage_forbidden"


@pytest.mark.integration
def test_live_http_redirect_never_reaches_target(tmp_path: Path) -> None:
    hits = {"redirect": 0, "target": 0}

    class Target(BaseHTTPRequestHandler):
        def do_HEAD(self) -> None:
            hits["target"] += 1
            self.send_response(200)
            self.end_headers()

        def log_message(self, _format: str, *args: object) -> None:
            pass

    target = ThreadingHTTPServer(("127.0.0.1", 0), Target)

    class Redirect(BaseHTTPRequestHandler):
        def do_HEAD(self) -> None:
            hits["redirect"] += 1
            self.send_response(307)
            self.send_header("Location", f"http://127.0.0.1:{target.server_port}/stolen")
            self.end_headers()

        def log_message(self, _format: str, *args: object) -> None:
            pass

    redirect = ThreadingHTTPServer(("127.0.0.1", 0), Redirect)
    threads = [threading.Thread(target=server.serve_forever, daemon=True) for server in (target, redirect)]
    for thread in threads:
        thread.start()
    try:
        location = StorageLocation(
            app_id="test-app", alias="test-store",
            endpoint=f"http://127.0.0.1:{redirect.server_port}",
            region="us-east-1", bucket=BUCKET, prefix="allowed/",
            access_key_file=SECRET_DIR / "minio_reader_user",
            secret_key_file=SECRET_DIR / "minio_reader_password",
            allow_loopback_http=True,
        )
        reader = S3StorageReader(StorageRegistry(locations=(location,)), temp_dir=tmp_path)
        source = SourceObject("test-store", BUCKET, "allowed/redirect", sha256="0" * 64)
        with pytest.raises(StorageError), reader.read("test-app", source):
            pass
        assert hits["redirect"] >= 1
        assert hits["target"] == 0
    finally:
        for server in (redirect, target):
            server.shutdown()
            server.server_close()
        for thread in threads:
            thread.join(timeout=2)
