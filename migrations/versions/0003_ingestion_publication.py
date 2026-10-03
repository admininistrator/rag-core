"""Fenced ingestion generations and durable source-mapped chunks (additive)."""

from alembic import op

revision = "0003_ingestion_publication"
down_revision = "0002_upload_registrations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE index_generations
            ADD COLUMN job_id uuid,
            ADD COLUMN lease_owner text,
            ADD COLUMN pipeline_fingerprint text,
            ADD COLUMN chunk_count integer CHECK (chunk_count > 0),
            ADD COLUMN manifest_sha256 text CHECK (manifest_sha256 ~ '^[0-9a-f]{64}$'),
            ADD CONSTRAINT fk_generation_job FOREIGN KEY (app_id,owner_id,job_id)
                REFERENCES ingestion_jobs (app_id,owner_id,job_id),
            ADD CONSTRAINT ck_generation_lease CHECK ((job_id IS NULL)=(lease_owner IS NULL))
    """)
    op.execute("""
        CREATE TABLE chunks (
            chunk_id uuid PRIMARY KEY,
            app_id text NOT NULL,
            owner_id text NOT NULL,
            version_id uuid NOT NULL,
            generation_id uuid NOT NULL,
            ordinal integer NOT NULL CHECK (ordinal >= 0),
            text text NOT NULL CHECK (length(text) BETWEEN 1 AND 33554432),
            checksum text NOT NULL CHECK (checksum ~ '^[0-9a-f]{64}$'),
            token_count integer NOT NULL CHECK (token_count BETWEEN 1 AND 512),
            language text NOT NULL CHECK (language IN ('en','vi','und')),
            unit_id text NOT NULL,
            source_map jsonb NOT NULL CHECK (jsonb_typeof(source_map)='object'),
            CONSTRAINT fk_chunk_generation FOREIGN KEY
                (app_id,owner_id,version_id,generation_id) REFERENCES index_generations
                (app_id,owner_id,version_id,generation_id),
            CONSTRAINT uq_chunk_ordinal UNIQUE (app_id,owner_id,generation_id,ordinal)
        )
    """)
    op.execute("""
        CREATE INDEX ix_job_expired ON ingestion_jobs (lease_until)
        WHERE lease_until IS NOT NULL
    """)


def downgrade() -> None:
    op.execute("DROP INDEX ix_job_expired")
    op.execute("DROP TABLE chunks")
    op.execute("""
        ALTER TABLE index_generations DROP CONSTRAINT ck_generation_lease,
            DROP CONSTRAINT fk_generation_job, DROP COLUMN job_id, DROP COLUMN lease_owner,
            DROP COLUMN pipeline_fingerprint, DROP COLUMN chunk_count, DROP COLUMN manifest_sha256
    """)
