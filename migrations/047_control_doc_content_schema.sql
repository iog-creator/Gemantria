-- Migration: control.doc_content_schema
-- Purpose: Add doc_fragment (content chunks) and doc_embedding (pgvector) tables
-- Context: Doc Content + pgvector Ingestion Plan (DOC_CONTENT_VECTOR_PLAN.md)
-- Notes:
--   - Extends control schema with content chunking and embedding storage.
--   - doc_fragment stores text chunks from docs in control.doc_registry.
--   - doc_embedding stores pgvector embeddings for RAG queries.
--   - Note: There is an existing control.doc_fragment table (migration 040) used for PoR.
--     This migration creates a new table structure for content chunks. The existing
--     PoR table can coexist as it serves a different purpose.

BEGIN;

CREATE SCHEMA IF NOT EXISTS control;

-- Ensure pgvector extension is available
CREATE EXTENSION IF NOT EXISTS vector;

-- Create control.doc_fragment table for content chunks
-- Note: There is an existing control.doc_fragment table (migration 040) used for PoR
-- with schema: (id uuid, project_id, src, anchor, sha256, created_at).
-- This migration extends it by adding new columns for content chunking.
-- The existing PoR columns remain for backward compatibility.
DO $$
BEGIN
    -- Check if doc_fragment table exists (from migration 040)
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'control'
        AND table_name = 'doc_fragment'
    ) THEN
        -- Table exists - add new columns for content chunking
        -- Add doc_id column if it doesn't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'control'
            AND table_name = 'doc_fragment'
            AND column_name = 'doc_id'
        ) THEN
            -- Make PoR columns nullable to allow content chunks without PoR data
            ALTER TABLE control.doc_fragment
                ALTER COLUMN project_id DROP NOT NULL,
                ALTER COLUMN src DROP NOT NULL,
                ALTER COLUMN anchor DROP NOT NULL,
                ALTER COLUMN sha256 DROP NOT NULL;

            -- Add new columns for content chunking
            ALTER TABLE control.doc_fragment
                ADD COLUMN doc_id UUID REFERENCES control.doc_registry(doc_id) ON DELETE CASCADE,
                ADD COLUMN version_id BIGINT REFERENCES control.doc_version(id) ON DELETE SET NULL,
                ADD COLUMN fragment_index INT,
                ADD COLUMN fragment_type TEXT,
                ADD COLUMN content TEXT,
                ADD COLUMN updated_at TIMESTAMPTZ DEFAULT NOW();

            -- Add indexes for new columns
            CREATE INDEX IF NOT EXISTS idx_doc_fragment_doc_id
                ON control.doc_fragment(doc_id);
            CREATE INDEX IF NOT EXISTS idx_doc_fragment_version_id
                ON control.doc_fragment(version_id);
            CREATE INDEX IF NOT EXISTS idx_doc_fragment_type
                ON control.doc_fragment(fragment_type);

            -- Add unique constraint for (doc_id, version_id, fragment_index) when all are non-null
            -- Note: This allows NULLs for PoR rows (which don't have doc_id)
            CREATE UNIQUE INDEX IF NOT EXISTS idx_doc_fragment_content_unique
                ON control.doc_fragment(doc_id, version_id, fragment_index)
                WHERE doc_id IS NOT NULL AND version_id IS NOT NULL AND fragment_index IS NOT NULL;
        END IF;
    ELSE
        -- Table doesn't exist - create it with both PoR and content chunking columns
        CREATE TABLE control.doc_fragment (
            id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            project_id      BIGINT,
            src             TEXT,
            anchor          TEXT,
            sha256          TEXT,
            doc_id          UUID REFERENCES control.doc_registry(doc_id) ON DELETE CASCADE,
            version_id      BIGINT REFERENCES control.doc_version(id) ON DELETE SET NULL,
            fragment_index  INT,
            fragment_type   TEXT,
            content         TEXT,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE (project_id, src, anchor),
            UNIQUE (doc_id, version_id, fragment_index)
        );

        CREATE INDEX IF NOT EXISTS idx_doc_fragment_project ON control.doc_fragment (project_id);
        CREATE INDEX IF NOT EXISTS idx_doc_fragment_src ON control.doc_fragment (src);
        CREATE INDEX IF NOT EXISTS idx_doc_fragment_sha256 ON control.doc_fragment (sha256);
        CREATE INDEX IF NOT EXISTS idx_doc_fragment_doc_id ON control.doc_fragment(doc_id);
        CREATE INDEX IF NOT EXISTS idx_doc_fragment_version_id ON control.doc_fragment(version_id);
        CREATE INDEX IF NOT EXISTS idx_doc_fragment_type ON control.doc_fragment(fragment_type);
    END IF;
END $$;

-- Create control.doc_embedding table for pgvector embeddings
-- Note: fragment_id references control.doc_fragment(id) which is UUID (from migration 040)
-- This maintains compatibility with the existing PoR table structure.
CREATE TABLE IF NOT EXISTS control.doc_embedding (
    id              BIGSERIAL PRIMARY KEY,
    fragment_id     UUID NOT NULL REFERENCES control.doc_fragment(id) ON DELETE CASCADE,
    model_name      TEXT NOT NULL,
    embedding       vector(1024) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_doc_embedding_fragment_id
    ON control.doc_embedding(fragment_id);
CREATE INDEX IF NOT EXISTS idx_doc_embedding_model_name
    ON control.doc_embedding(model_name);

-- Unique constraint: one embedding per fragment/model combination
CREATE UNIQUE INDEX IF NOT EXISTS idx_doc_embedding_fragment_model_unique
    ON control.doc_embedding(fragment_id, model_name);

-- Add vector similarity search index (ivfflat for approximate nearest neighbor)
-- Note: This requires at least some data to be present. We'll create it later
-- when we have embeddings, or make it optional.
-- CREATE INDEX IF NOT EXISTS idx_doc_embedding_vector_ivfflat
--     ON control.doc_embedding
--     USING ivfflat (embedding vector_cosine_ops)
--     WITH (lists = 100);

COMMIT;

