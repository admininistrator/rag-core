"""Unit tests for safe, typed settings loading."""

from __future__ import annotations

import traceback
from pathlib import Path

import pytest

from rag_core.config import SettingsError, load_settings

REQUIRED_ENV = {
    "DATABASE_URL": "postgresql://rag_core:local-only@127.0.0.1:5432/rag_core",
    "REDIS_URL": "redis://127.0.0.1:6379/0",
    "QDRANT_URL": "http://127.0.0.1:6333",
}


def _clear_required_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in REQUIRED_ENV:
        monkeypatch.delenv(name, raising=False)


@pytest.mark.unit
def test_load_settings_reads_typed_environment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    _clear_required_environment(monkeypatch)
    for name, value in REQUIRED_ENV.items():
        monkeypatch.setenv(name, value)
    monkeypatch.setenv("API_PORT", "8123")
    monkeypatch.setenv("REQUEST_TIMEOUT_SECONDS", "12.5")

    settings = load_settings()

    assert settings.api_port == 8123
    assert settings.request_timeout_seconds == 12.5
    assert str(settings.api_bind) == "127.0.0.1"
    assert settings.database_url.scheme == "postgresql"
    assert settings.redis_url.scheme == "redis"
    assert "local-only" not in repr(settings)


@pytest.mark.unit
def test_load_settings_ignores_blank_optional_secret_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    _clear_required_environment(monkeypatch)
    for name, value in REQUIRED_ENV.items():
        monkeypatch.setenv(name, value)
    monkeypatch.setenv("DATABASE_PASSWORD_FILE", "")

    settings = load_settings()

    assert settings.database_password_file is None


@pytest.mark.unit
def test_load_settings_reports_missing_required_configuration(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    _clear_required_environment(monkeypatch)

    with pytest.raises(SettingsError) as caught:
        load_settings()

    message = str(caught.value)
    assert message == (
        "Missing required RAG Core configuration: DATABASE_URL, QDRANT_URL, REDIS_URL"
    )
    assert caught.value.__cause__ is None


@pytest.mark.unit
def test_load_settings_reports_invalid_field_without_echoing_other_values(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    _clear_required_environment(monkeypatch)
    for name, value in REQUIRED_ENV.items():
        monkeypatch.setenv(name, value)
    monkeypatch.setenv("DATABASE_URL", "not-a-url-with-do-not-echo")

    with pytest.raises(SettingsError) as caught:
        load_settings()

    rendered = "".join(traceback.format_exception(caught.value))
    assert "Invalid RAG Core configuration: DATABASE_URL:" in rendered
    assert "do-not-echo" not in rendered
