"""Durable owner/session idempotency records for upload registration."""

from alembic import op

revision = "0002_upload_registrations"
down_revision = "0001_session_metadata"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE upload_registrations (
            registration_id uuid PRIMARY KEY,
            app_id text NOT NULL,
            owner_id text NOT NULL,
            session_id uuid NOT NULL,
            idempotency_key text NOT NULL CHECK (length(idempotency_key) BETWEEN 1 AND 256),
            request_hash text NOT NULL CHECK (request_hash ~ '^[0-9a-f]{64}$'),
            external_upload_id text NOT NULL CHECK (length(btrim(external_upload_id)) > 0),
            document_id uuid NOT NULL,
            version_id uuid NOT NULL,
            job_id uuid NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now(),
            CONSTRAINT fk_registration_session FOREIGN KEY (app_id, owner_id, session_id)
                REFERENCES sessions (app_id, owner_id, session_id),
            CONSTRAINT fk_registration_version FOREIGN KEY
                (app_id, owner_id, document_id, version_id)
                REFERENCES document_versions (app_id, owner_id, document_id, version_id),
            CONSTRAINT fk_registration_job FOREIGN KEY (app_id, owner_id, job_id)
                REFERENCES ingestion_jobs (app_id, owner_id, job_id),
            CONSTRAINT uq_registration_key UNIQUE
                (app_id, owner_id, session_id, idempotency_key),
            CONSTRAINT uq_registration_upload UNIQUE
                (app_id, owner_id, session_id, external_upload_id),
            CONSTRAINT uq_registration_job UNIQUE (job_id)
        )
    """)
def downgrade() -> None:
    op.execute("DROP TABLE upload_registrations")
