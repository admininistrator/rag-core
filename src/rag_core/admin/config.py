"""Operator-owned local admin configuration and versioned scrypt password hashes."""

import hashlib
import hmac
import secrets
from pathlib import Path
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator


def hash_password(password: str) -> str:
    if not 12 <= len(password) <= 1024:
        raise ValueError("Admin password must contain 12 to 1024 characters")
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(
        password.encode(), salt=salt, n=2**17, r=8, p=1, maxmem=256 * 1024 * 1024, dklen=32
    )
    return f"scrypt-v1${salt.hex()}${digest.hex()}"


def valid_hash(value: str) -> bool:
    parts = value.split("$")
    return (
        len(parts) == 3
        and parts[0] == "scrypt-v1"
        and len(parts[1]) == 32
        and len(parts[2]) == 64
        and all(c in "0123456789abcdef" for c in parts[1] + parts[2])
    )


def verify_password(password: str, encoded: str) -> bool:
    if not valid_hash(encoded) or not 1 <= len(password) <= 1024:
        return False
    _, salt, expected = encoded.split("$")
    digest = hashlib.scrypt(
        password.encode(),
        salt=bytes.fromhex(salt),
        n=2**17,
        r=8,
        p=1,
        maxmem=256 * 1024 * 1024,
        dklen=32,
    )
    return hmac.compare_digest(digest.hex(), expected)


class AdminConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)
    username: str = Field(min_length=1, max_length=128, repr=False)
    password_hash: SecretStr
    origin: str
    allow_loopback_http: bool = False
    session_seconds: int = Field(default=3600, ge=60, le=28800)

    @model_validator(mode="after")
    def validate_security(self) -> "AdminConfig":
        if not valid_hash(self.password_hash.get_secret_value()):
            raise ValueError("Invalid admin password hash")
        url = urlsplit(self.origin)
        if (
            url.scheme not in {"http", "https"}
            or not url.hostname
            or url.username
            or url.password
            or url.path
            or url.query
            or url.fragment
            or self.origin != f"{url.scheme}://{url.netloc}"
            or (
                url.scheme == "http"
                and (
                    not self.allow_loopback_http
                    or url.hostname not in {"127.0.0.1", "localhost", "::1"}
                )
            )
        ):
            raise ValueError("Admin origin requires HTTPS or explicit loopback HTTP")
        # Force validation of the port; never accept malformed origin configuration.
        _ = url.port
        return self

    @property
    def secure_cookie(self) -> bool:
        return self.origin.startswith("https://")

    @property
    def credential_hash(self) -> str:
        return hashlib.sha256(
            (
                self.username + "\0" + self.password_hash.get_secret_value() + "\0" + self.origin
            ).encode()
        ).hexdigest()


def load_admin_config(path: Path, *, production: bool = False) -> AdminConfig:
    try:
        if path.stat().st_size > 8192:
            raise ValueError
        config = AdminConfig.model_validate_json(path.read_bytes())
        if production and config.allow_loopback_http:
            raise ValueError
        return config
    except (OSError, ValueError):
        raise ValueError("Invalid ADMIN_CONFIG_FILE") from None
