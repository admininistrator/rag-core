"""Opaque revocable PG sessions; no application credential can mint admin authority."""

import asyncio
import hashlib
import hmac
import secrets
from dataclasses import dataclass
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from rag_core.admin.config import AdminConfig, verify_password

COOKIE = "rag_admin"
COOKIE_PATH = "/v1/admin"


class AdminError(Exception):
    def __init__(self, code: str, status: int) -> None:
        self.code, self.status = code, status
        super().__init__(code)


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def csrf_token(token: str) -> str:
    return hmac.new(token.encode(), b"rag-admin-csrf-v1", "sha256").hexdigest()


async def audit(
    conn: AsyncConnection,
    action: str,
    request_id: UUID,
    *,
    target: UUID | None = None,
    related: UUID | None = None,
    outcome: str = "success",
) -> None:
    await conn.execute(
        text("""
        INSERT INTO audit_events (event_id,actor,action,target_id,related_id,request_id,outcome)
        VALUES (:event,'local_admin',:action,:target,:related,:request,:outcome)
    """),
        {
            "event": uuid4(),
            "action": action,
            "target": target,
            "related": related,
            "request": request_id,
            "outcome": outcome,
        },
    )


@dataclass(frozen=True)
class AdminServices:
    engine: AsyncEngine
    config: AdminConfig


class AdminAuthentication:
    def __init__(self, services: AdminServices) -> None:
        self.services = services
        self.hash_slots = asyncio.Semaphore(2)

    async def login(
        self, username: str, password: str, request_id: UUID, old_token: str | None = None
    ) -> str:
        config = self.services.config
        # Persistent, account-wide limit. No caller-supplied IP/username can bypass it.
        async with self.services.engine.begin() as conn:
            allowed = (
                await conn.execute(
                    text("""
                INSERT INTO admin_login_limits (credential_hash) VALUES (:credential)
                ON CONFLICT (credential_hash) DO UPDATE SET
                    attempts=CASE WHEN admin_login_limits.window_start<=now()-interval '60 seconds'
                        THEN 1 ELSE admin_login_limits.attempts+1 END,
                    window_start=CASE WHEN admin_login_limits.window_start<=now()-interval '60 seconds'
                        THEN now() ELSE admin_login_limits.window_start END
                WHERE admin_login_limits.attempts<10
                    OR admin_login_limits.window_start<=now()-interval '60 seconds'
                RETURNING attempts
            """),
                    {"credential": config.credential_hash},
                )
            ).scalar_one_or_none()
            if allowed is None:
                await audit(conn, "login", request_id, outcome="denied")
        if allowed is None:
            raise AdminError("rate_limited", 429)
        try:
            async with asyncio.timeout(0.05):
                await self.hash_slots.acquire()
        except TimeoutError:
            async with self.services.engine.begin() as conn:
                await audit(conn, "login", request_id, outcome="denied")
            raise AdminError("rate_limited", 429) from None
        task = asyncio.create_task(
            asyncio.to_thread(verify_password, password, config.password_hash.get_secret_value())
        )
        # A disconnected client cannot release the slot while its hashing thread still runs.
        task.add_done_callback(lambda _task: self.hash_slots.release())
        password_ok = await asyncio.shield(task)
        valid = hmac.compare_digest(username.encode(), config.username.encode()) and password_ok
        token = secrets.token_urlsafe(32)
        async with self.services.engine.begin() as conn:
            await audit(conn, "login", request_id, outcome="success" if valid else "denied")
            if valid:
                # Bounded cleanup of expired/revoked sessions during authenticated login.
                await conn.execute(
                    text("""
                    DELETE FROM admin_sessions WHERE token_hash IN (
                        SELECT token_hash FROM admin_sessions
                        WHERE expires_at<=now() OR revoked_at IS NOT NULL LIMIT 100)
                """)
                )
                if old_token:
                    await conn.execute(
                        text("""
                        UPDATE admin_sessions SET revoked_at=now() WHERE token_hash=:token
                    """),
                        {"token": digest(old_token)},
                    )
                await conn.execute(
                    text("""
                    INSERT INTO admin_sessions (token_hash,csrf_hash,credential_hash,expires_at)
                    VALUES (:token,:csrf,:credential,now()+(:ttl*interval '1 second'))
                """),
                    {
                        "token": digest(token),
                        "csrf": digest(csrf_token(token)),
                        "credential": config.credential_hash,
                        "ttl": config.session_seconds,
                    },
                )
        if not valid:
            raise AdminError("invalid_credentials", 401)
        return token

    async def require(self, conn: AsyncConnection, token: str | None) -> str:
        if (
            not token
            or len(token) != 43
            or any(
                c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
                for c in token
            )
        ):
            raise AdminError("invalid_credentials", 401)
        row = (
            await conn.execute(
                text("""
            SELECT csrf_hash FROM admin_sessions WHERE token_hash=:token
                AND credential_hash=:credential AND expires_at>now() AND revoked_at IS NULL
            FOR UPDATE
        """),
                {"token": digest(token), "credential": self.services.config.credential_hash},
            )
        ).scalar_one_or_none()
        if row is None:
            raise AdminError("invalid_credentials", 401)
        return str(row)
