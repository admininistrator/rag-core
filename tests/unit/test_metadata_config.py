"""Credential-safe metadata configuration failures."""

from pathlib import Path

import pytest

from rag_core.adapters.persistence.database import database_url, database_url_from_env

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "value", ["not-a-dsn-secret", "sqlite:///secret", "postgresql://user@host"]
)
def test_invalid_database_url_does_not_echo_input(value: str) -> None:
    with pytest.raises(ValueError) as caught:
        database_url(value)
    assert str(caught.value) == "Invalid DATABASE_URL or DATABASE_PASSWORD_FILE"


def test_password_file_and_missing_configuration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValueError, match="DATABASE_URL is required"):
        database_url_from_env()
    secret = tmp_path / "password"
    secret.write_text("synthetic-password\n", encoding="utf-8")
    url = database_url("postgresql://user@127.0.0.1/test", secret)
    assert url.drivername == "postgresql+psycopg"
    assert url.password == "synthetic-password"
    assert "synthetic-password" not in repr(url)
    secret.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid DATABASE_URL or DATABASE_PASSWORD_FILE"):
        database_url("postgresql://user@127.0.0.1/test", secret)
