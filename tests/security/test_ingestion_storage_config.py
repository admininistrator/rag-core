"""The worker's explicit Compose HTTP opt-in must not authorize other origins."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from rag_core.adapters.storage.s3 import StorageLocation, load_storage_registry
from rag_core.ports.storage import StorageError

pytestmark = pytest.mark.security


def location(endpoint: str, **flags: bool) -> StorageLocation:
    return StorageLocation(
        app_id="test-app", alias="app-store", endpoint=endpoint, region="us-east-1",
        bucket="test-bucket", prefix="allowed/", access_key_file=Path("reader-user"),
        secret_key_file=Path("reader-password"), **flags,
    )


@pytest.mark.parametrize("endpoint", [
    "http://minio", "http://minio:9001", "http://minio.example:9000",
    "http://127.0.0.1:9000", "http://169.254.169.254:9000",
    "http://reader@minio:9000", "http://minio:9000?target=elsewhere",
    "http://minio:9000/bucket", "http://minio:9000#target",
])
def test_compose_opt_in_rejects_other_origins_and_url_components(endpoint: str) -> None:
    with pytest.raises(ValidationError):
        location(endpoint, allow_compose_http=True)


def test_compose_http_requires_explicit_opt_in() -> None:
    with pytest.raises(ValidationError):
        location("http://minio:9000")
    assert location("http://minio:9000", allow_compose_http=True).endpoint == "http://minio:9000"


@pytest.mark.parametrize("flag", ["allow_compose_http", "allow_loopback_http"])
def test_production_rejects_development_flags_even_on_https(tmp_path: Path, flag: str) -> None:
    config = tmp_path / "storage.json"
    config.write_text(json.dumps({"locations": [
        location("https://storage.example", **{flag: True}).model_dump(mode="json"),
    ]}), encoding="utf-8")
    assert load_storage_registry(config).locations[0].endpoint == "https://storage.example"
    with pytest.raises(StorageError, match="invalid_storage_config"):
        load_storage_registry(config, production=True)
