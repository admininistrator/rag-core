"""Authenticated identity; no session or document permissions are implied."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Principal:
    app_id: str
    user_id: str


class InvalidCredentials(Exception):
    """Invalid authentication without exposing token or key details."""


class AuthUnavailable(Exception):
    """Trusted auth configuration or key service is unavailable."""
