"""Owner-bound session metadata and retained document generations.

Frozen DDL: this revision does not import mutable application table definitions.
"""

from alembic import op

revision = "0001_session_metadata"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE sessions (
            session_id uuid PRIMARY KEY,
            app_id text NOT NULL CHECK (length(app_id) > 0),
            owner_id text NOT NULL CHECK (length(owner_id) > 0),
            external_session_id text NOT NULL CHECK (length(btrim(external_session_id)) > 0),
            status text NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'deleted')),
            scope_revision bigint NOT NULL DEFAULT 0 CHECK (scope_revision >= 0),
            created_at timestamptz NOT NULL DEFAULT now(),
            deleted_at timestamptz,
            CONSTRAINT uq_session_external UNIQUE (app_id, owner_id, external_session_id),
            CONSTRAINT uq_session_owner UNIQUE (app_id, owner_id, session_id),
            CHECK ((status = 'deleted') = (deleted_at IS NOT NULL))
        )
    """)
    op.execute("""
        CREATE TABLE documents (
            document_id uuid PRIMARY KEY,
            app_id text NOT NULL,
            owner_id text NOT NULL,
            filename text NOT NULL CHECK (length(btrim(filename)) > 0),
            storage_alias text NOT NULL,
            bucket text NOT NULL,
            object_key text NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now(),
            CONSTRAINT uq_document_owner UNIQUE (app_id, owner_id, document_id)
        )
    """)
    op.execute("""
        CREATE TABLE document_versions (
            version_id uuid PRIMARY KEY,
            app_id text NOT NULL,
            owner_id text NOT NULL,
            document_id uuid NOT NULL,
            source_version_id text,
            source_sha256 text CHECK (source_sha256 ~ '^[0-9a-f]{64}$'),
            content_type text NOT NULL,
            size_bytes bigint CHECK (size_bytes >= 0 AND size_bytes <= 104857600),
            extraction_fingerprint text,
            index_fingerprint text,
            state text NOT NULL DEFAULT 'queued' CHECK (state IN
                ('queued','fetching','parsing','chunking','embedding','indexing',
                 'ready','failed','cancelled')),
            active_generation_id uuid,
            created_at timestamptz NOT NULL DEFAULT now(),
            CONSTRAINT fk_version_document FOREIGN KEY (app_id, owner_id, document_id)
                REFERENCES documents (app_id, owner_id, document_id),
            CONSTRAINT uq_version_owner UNIQUE (app_id, owner_id, document_id, version_id),
            CONSTRAINT uq_version_identity UNIQUE (app_id, owner_id, version_id),
            CHECK (source_sha256 IS NOT NULL OR
                   (source_version_id IS NOT NULL AND length(source_version_id) > 0)),
            CHECK (state <> 'ready' OR active_generation_id IS NOT NULL)
        )
    """)
    op.execute("""
        CREATE TABLE index_generations (
            generation_id uuid PRIMARY KEY,
            app_id text NOT NULL,
            owner_id text NOT NULL,
            version_id uuid NOT NULL,
            state text NOT NULL DEFAULT 'staging' CHECK (state IN ('staging','ready','failed')),
            index_fingerprint text NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now(),
            CONSTRAINT fk_generation_version FOREIGN KEY (app_id, owner_id, version_id)
                REFERENCES document_versions (app_id, owner_id, version_id),
            CONSTRAINT uq_generation_version UNIQUE
                (app_id, owner_id, version_id, generation_id)
        )
    """)
    op.execute("""
        ALTER TABLE document_versions ADD CONSTRAINT fk_active_generation
        FOREIGN KEY (app_id, owner_id, version_id, active_generation_id)
        REFERENCES index_generations (app_id, owner_id, version_id, generation_id)
    """)
    op.execute("""
        CREATE TABLE session_documents (
            link_id uuid PRIMARY KEY,
            app_id text NOT NULL,
            owner_id text NOT NULL,
            session_id uuid NOT NULL,
            document_id uuid NOT NULL,
            version_id uuid NOT NULL,
            upload_registration_id uuid NOT NULL,
            status text NOT NULL DEFAULT 'attached' CHECK (status IN ('attached','detached')),
            attached_at timestamptz NOT NULL DEFAULT now(),
            detached_at timestamptz,
            CONSTRAINT fk_link_session FOREIGN KEY (app_id, owner_id, session_id)
                REFERENCES sessions (app_id, owner_id, session_id),
            CONSTRAINT fk_link_version FOREIGN KEY (app_id, owner_id, document_id, version_id)
                REFERENCES document_versions (app_id, owner_id, document_id, version_id),
            CONSTRAINT uq_link_registration UNIQUE (app_id, owner_id, session_id,
                                                    upload_registration_id),
            CHECK ((status = 'detached') = (detached_at IS NOT NULL))
        )
    """)
    op.execute("""
        CREATE UNIQUE INDEX uq_attached_document ON session_documents
        (app_id, owner_id, session_id, document_id) WHERE status = 'attached'
    """)
    op.execute("""
        CREATE TABLE ingestion_jobs (
            job_id uuid PRIMARY KEY,
            app_id text NOT NULL,
            owner_id text NOT NULL,
            version_id uuid NOT NULL,
            state text NOT NULL DEFAULT 'queued' CHECK (state IN
                ('queued','fetching','parsing','chunking','embedding','indexing',
                 'ready','failed','cancelled')),
            progress integer NOT NULL DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
            error_code text,
            attempts integer NOT NULL DEFAULT 0 CHECK (attempts >= 0),
            max_attempts integer NOT NULL DEFAULT 3 CHECK (max_attempts > 0),
            lease_owner text,
            lease_until timestamptz,
            task_fingerprint text NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            CONSTRAINT fk_job_version FOREIGN KEY (app_id, owner_id, version_id)
                REFERENCES document_versions (app_id, owner_id, version_id),
            CONSTRAINT uq_job_owner UNIQUE (app_id, owner_id, job_id),
            CONSTRAINT uq_job_task UNIQUE (app_id, owner_id, version_id, task_fingerprint),
            CHECK (attempts <= max_attempts),
            CHECK ((lease_owner IS NULL) = (lease_until IS NULL))
        )
    """)
    op.execute("""
        CREATE TABLE outbox_events (
            event_id uuid PRIMARY KEY,
            app_id text NOT NULL,
            owner_id text NOT NULL,
            job_id uuid NOT NULL,
            event_type text NOT NULL CHECK (length(event_type) > 0),
            payload jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(payload) = 'object'),
            created_at timestamptz NOT NULL DEFAULT now(),
            available_at timestamptz NOT NULL DEFAULT now(),
            dispatched_at timestamptz,
            attempts integer NOT NULL DEFAULT 0 CHECK (attempts >= 0),
            CONSTRAINT fk_outbox_job FOREIGN KEY (app_id, owner_id, job_id)
                REFERENCES ingestion_jobs (app_id, owner_id, job_id)
        )
    """)
    op.execute("""
        CREATE INDEX ix_outbox_pending ON outbox_events (available_at, event_id)
        WHERE dispatched_at IS NULL
    """)


def downgrade() -> None:
    # Explicit, destructive operator action; never called by session lifecycle.
    for table in ("outbox_events", "ingestion_jobs", "session_documents"):
        op.execute(f"DROP TABLE {table}")
    op.execute("ALTER TABLE document_versions DROP CONSTRAINT fk_active_generation")
    for table in ("index_generations", "document_versions", "documents", "sessions"):
        op.execute(f"DROP TABLE {table}")
