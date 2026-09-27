"""Operator-owned app registry. Never load URLs or identity from request bodies."""

from pathlib import Path
from typing import Annotated, Self
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from rag_core.auth import AuthUnavailable

Name = Annotated[str, Field(min_length=1, max_length=256, pattern=r"^\S+$")]


class AppIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)

    app_id: Name
    service_key_sha256: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$", repr=False)]
    issuer: Name
    audience: Name
    jwks_url: Annotated[str, Field(min_length=1, max_length=2048, repr=False)]


class AuthConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)

    apps: Annotated[tuple[AppIdentity, ...], Field(min_length=1, max_length=100)]
    cache_ttl_seconds: Annotated[int, Field(ge=1, le=3600)] = 300
    refresh_interval_seconds: Annotated[int, Field(ge=1, le=60)] = 5
    jwks_timeout_seconds: Annotated[float, Field(gt=0, le=10)] = 3
    allow_loopback_http: bool = False

    @model_validator(mode="after")
    def validate_registry(self) -> Self:
        if self.refresh_interval_seconds > self.cache_ttl_seconds:
            raise ValueError("refresh interval must not exceed cache TTL")
        for field in ("app_id", "service_key_sha256"):
            if len({getattr(app, field) for app in self.apps}) != len(self.apps):
                raise ValueError("app IDs and service key hashes must be unique")
        for app in self.apps:
            url = urlsplit(app.jwks_url)
            # HTTP is an explicit development exception for literal loopback only.
            local = self.allow_loopback_http and url.hostname in {"127.0.0.1", "::1"}
            if (
                not url.hostname
                or url.username is not None
                or url.password is not None
                or url.fragment
                or url.query
                or (url.scheme != "https" and not (url.scheme == "http" and local))
            ):
                raise ValueError("JWKS requires HTTPS or explicitly enabled literal loopback HTTP")
            _ = url.port  # Validate malformed ports before any request.
        return self


def load_auth_config(path: Path, *, production: bool = False) -> AuthConfig:
    try:
        if path.stat().st_size > 262144:
            raise ValueError("oversized configuration")
        config = AuthConfig.model_validate_json(path.read_bytes())
        if production and config.allow_loopback_http:
            raise ValueError("development transport in production")
        return config
    except (OSError, ValueError, ValidationError):
        raise AuthUnavailable("Invalid AUTH_CONFIG_FILE") from None
