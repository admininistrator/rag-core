"""Typed settings shared by RAG Core processes."""

from ipaddress import IPv4Address
from pathlib import Path
from typing import Literal

from pydantic import AnyHttpUrl, Field, IPvAnyAddress, PostgresDsn, RedisDsn, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class SettingsError(ValueError):
    """Raised with a safe, operator-facing summary of invalid configuration."""


class Settings(BaseSettings):
    """Configuration implemented by the T01 project scaffold.

    Database and Redis URLs are required because the target service cannot start
    meaningfully without its durable metadata store and broker configuration.
    Later tasks add settings only when the owning component is implemented.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        case_sensitive=False,
        extra="ignore",
        hide_input_in_errors=True,
    )

    app_env: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    api_bind: IPvAnyAddress = IPv4Address("127.0.0.1")
    api_port: int = Field(default=8000, ge=1, le=65535)
    request_timeout_seconds: float = Field(default=30.0, gt=0, le=300)
    health_timeout_seconds: float = Field(default=2.0, gt=0, le=30)
    database_url: PostgresDsn = Field(repr=False)
    database_password_file: Path | None = Field(default=None, repr=False)
    redis_url: RedisDsn = Field(repr=False)
    qdrant_url: AnyHttpUrl = Field(repr=False)
    auth_config_file: Path | None = Field(default=None, repr=False)


def _safe_validation_message(exc: ValidationError) -> str:
    errors = exc.errors(include_url=False, include_context=False, include_input=False)
    missing = sorted(
        ".".join(str(part) for part in error["loc"]).upper()
        for error in errors
        if error["type"] == "missing"
    )
    if missing:
        return f"Missing required RAG Core configuration: {', '.join(missing)}"

    details = [
        f"{'.'.join(str(part) for part in error['loc']).upper()}: {error['msg']}"
        for error in errors
    ]
    return f"Invalid RAG Core configuration: {'; '.join(details)}"


def load_settings() -> Settings:
    """Load environment/.env settings and replace raw validation output safely."""

    try:
        return Settings()
    except ValidationError as exc:
        raise SettingsError(_safe_validation_message(exc)) from None
