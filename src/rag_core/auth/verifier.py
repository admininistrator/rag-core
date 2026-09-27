"""RS256 validation with bounded per-app JWKS cache and fail-closed refresh."""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import time
from dataclasses import dataclass, field
from typing import Any

import httpx
import jwt
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

from rag_core.auth import AuthUnavailable, InvalidCredentials, Principal
from rag_core.auth.config import AppIdentity, AuthConfig


@dataclass
class _Cache:
    keys: dict[str, jwt.PyJWK] = field(default_factory=dict)
    expires: float = 0
    next_refresh: float = 0
    failed: bool = False
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


class Authenticator:
    def __init__(self, config: AuthConfig) -> None:
        self.config = config
        self._caches = {app.app_id: _Cache() for app in config.apps}

    async def authenticate(self, service_key: str, token: str) -> Principal:
        if not 32 <= len(service_key) <= 512 or not 1 <= len(token) <= 16384:
            raise InvalidCredentials
        digest = hashlib.sha256(service_key.encode()).hexdigest()
        app = next(
            (
                app
                for app in self.config.apps
                if hmac.compare_digest(app.service_key_sha256, digest)
            ),
            None,
        )
        if app is None:
            raise InvalidCredentials
        try:
            header = jwt.get_unverified_header(token)
            kid = header.get("kid")
            if (
                header.get("alg") != "RS256"
                or not isinstance(kid, str)
                or not 1 <= len(kid) <= 128
                or any(name in header for name in ("jku", "jwk", "x5u", "x5c", "crit"))
            ):
                raise InvalidCredentials
            key = await self._key(app, kid)
            claims = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                issuer=app.issuer,
                audience=app.audience,
                options={"require": ["sub", "app_id", "iss", "aud", "exp", "nbf", "iat"]},
                leeway=0,
            )
            subject = claims["sub"]
            if (
                claims["app_id"] != app.app_id
                or not isinstance(subject, str)
                or not subject.strip()
                or len(subject) > 256
                or any(type(claims[name]) is not int for name in ("exp", "nbf", "iat"))
                or claims["exp"] <= max(claims["nbf"], claims["iat"])
            ):
                raise InvalidCredentials
            return Principal(app_id=app.app_id, user_id=subject)
        except (jwt.PyJWTError, ValueError, TypeError, OverflowError):
            raise InvalidCredentials from None

    async def _key(self, app: AppIdentity, kid: str) -> jwt.PyJWK:
        cache = self._caches[app.app_id]
        async with cache.lock:
            now = time.monotonic()
            if now < cache.expires and kid in cache.keys:
                return cache.keys[kid]
            if now >= cache.next_refresh:
                # Coalesce unknown-kid floods and failed refreshes, without unbounded negative cache.
                cache.next_refresh = now + self.config.refresh_interval_seconds
                try:
                    keys = await self._fetch(app)
                except AuthUnavailable:
                    cache.failed = True
                    raise
                cache.keys = keys  # Replace: removed keys must not survive a successful refresh.
                cache.expires = time.monotonic() + self.config.cache_ttl_seconds
                cache.failed = False
            if cache.failed or time.monotonic() >= cache.expires:
                raise AuthUnavailable
            if kid not in cache.keys:
                raise InvalidCredentials
            return cache.keys[kid]

    async def _fetch(self, app: AppIdentity) -> dict[str, jwt.PyJWK]:
        try:
            # No environment proxy, redirect, token-selected URL, or unbounded response.
            async with asyncio.timeout(self.config.jwks_timeout_seconds):
                async with httpx.AsyncClient(
                    timeout=self.config.jwks_timeout_seconds,
                    follow_redirects=False,
                    trust_env=False,
                ) as client:
                    async with client.stream("GET", app.jwks_url) as response:
                        response.raise_for_status()
                        body = bytearray()
                        async for chunk in response.aiter_bytes(chunk_size=16384):
                            body.extend(chunk)
                            if len(body) > 131072:
                                raise ValueError("oversized JWKS")
            return self._parse_keys(json.loads(body))
        except (httpx.HTTPError, TimeoutError, ValueError, TypeError, KeyError, jwt.PyJWTError):
            raise AuthUnavailable from None

    @staticmethod
    def _parse_keys(document: Any) -> dict[str, jwt.PyJWK]:
        if not isinstance(document, dict) or not isinstance(document.get("keys"), list):
            raise ValueError("invalid JWKS")
        if not 1 <= len(document["keys"]) <= 32:
            raise ValueError("invalid JWKS key count")
        keys: dict[str, jwt.PyJWK] = {}
        for entry in document["keys"]:
            if not isinstance(entry, dict):
                raise ValueError("invalid JWK")
            # Other algorithms may coexist in an issuer's key set; never select them.
            if entry.get("kty") != "RSA" or entry.get("alg", "RS256") != "RS256":
                continue
            if entry.get("use", "sig") != "sig" or entry.get("key_ops", ["verify"]) != ["verify"]:
                continue
            kid = entry.get("kid")
            if (
                not isinstance(kid, str)
                or not 1 <= len(kid) <= 128
                or kid in keys
                or any(name in entry for name in ("d", "p", "q", "dp", "dq", "qi", "oth"))
            ):
                raise ValueError("ambiguous or private JWK")
            key = jwt.PyJWK(entry, algorithm="RS256")
            if not isinstance(key.key, RSAPublicKey) or not 2048 <= key.key.key_size <= 8192:
                raise ValueError("invalid RSA key size")
            keys[kid] = key
        return keys
