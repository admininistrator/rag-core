"""Separate local admin sessions, bounded login attempts and metadata-only audit."""

from alembic import op

revision = "0004_admin_audit"
down_revision = "0003_ingestion_publication"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE admin_sessions (
            token_hash text PRIMARY KEY CHECK (token_hash ~ '^[0-9a-f]{64}$'),
            csrf_hash text NOT NULL CHECK (csrf_hash ~ '^[0-9a-f]{64}$'),
            credential_hash text NOT NULL CHECK (credential_hash ~ '^[0-9a-f]{64}$'),
            created_at timestamptz NOT NULL DEFAULT now(),
            expires_at timestamptz NOT NULL,
            revoked_at timestamptz,
            CHECK (expires_at > created_at)
        )
    """)
    op.execute("""
        CREATE TABLE admin_login_limits (
            credential_hash text PRIMARY KEY,
            window_start timestamptz NOT NULL DEFAULT now(),
            attempts integer NOT NULL DEFAULT 1 CHECK (attempts BETWEEN 1 AND 10)
        )
    """)
    op.execute("""
        CREATE TABLE audit_events (
            event_id uuid PRIMARY KEY,
            actor text NOT NULL CHECK (actor = 'local_admin'),
            action text NOT NULL CHECK (action IN
                ('login','logout','job_retry','job_cancel','job_reindex',
                 'session_detach','session_tombstone','csrf_rejected')),
            target_id uuid,
            related_id uuid,
            request_id uuid NOT NULL,
            outcome text NOT NULL CHECK (outcome IN ('success','denied')),
            created_at timestamptz NOT NULL DEFAULT now()
        )
    """)


def downgrade() -> None:
    for table in ("audit_events", "admin_login_limits", "admin_sessions"):
        op.execute(f"DROP TABLE {table}")
