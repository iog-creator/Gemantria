-- Migration 043: Knowledge Schema
-- Purpose: Create knowledge schema with kb_document and kb_embedding tables for Phase-6 6C (Knowledge Slice v0)
-- Related: Phase-6 Plan (6C), ADR-066 (LM Studio Control-Plane Integration)

CREATE SCHEMA IF NOT EXISTS knowledge;

-- Enable pgvector extension if available (required for kb_embedding)
CREATE EXTENSION IF NOT EXISTS vector;

-- ===============================
-- KB DOCUMENT
-- ===============================

CREATE TABLE IF NOT EXISTS knowledge.kb_document (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    title text NOT NULL,
    section text NOT NULL,
    slug text NOT NULL UNIQUE,
    body_md text NOT NULL,
    tags text[] NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_kb_document_section ON knowledge.kb_document (section);
CREATE INDEX IF NOT EXISTS idx_kb_document_slug ON knowledge.kb_document (slug);
CREATE INDEX IF NOT EXISTS idx_kb_document_tags ON knowledge.kb_document USING GIN (tags);
CREATE INDEX IF NOT EXISTS idx_kb_document_created ON knowledge.kb_document (created_at);

COMMENT ON TABLE knowledge.kb_document IS 'Phase-6 6C: Knowledge base documents (markdown content)';
COMMENT ON COLUMN knowledge.kb_document.id IS 'Document UUID (gen_random_uuid for now; future: uuidv7)';
COMMENT ON COLUMN knowledge.kb_document.title IS 'Document title (from H1 or filename)';
COMMENT ON COLUMN knowledge.kb_document.section IS 'Document section/category (from parent directory or "general")';
COMMENT ON COLUMN knowledge.kb_document.slug IS 'Unique slug derived from file path';
COMMENT ON COLUMN knowledge.kb_document.body_md IS 'Full markdown content';
COMMENT ON COLUMN knowledge.kb_document.tags IS 'Array of tags (from frontmatter or empty)';

-- ===============================
-- KB EMBEDDING
-- ===============================

CREATE TABLE IF NOT EXISTS knowledge.kb_embedding (
    doc_id uuid NOT NULL REFERENCES knowledge.kb_document(id) ON DELETE CASCADE,
    embedding vector(1024) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (doc_id)
);

CREATE INDEX IF NOT EXISTS idx_kb_embedding_doc ON knowledge.kb_embedding (doc_id);
-- Vector similarity index (IVFFlat for approximate nearest neighbor)
-- Note: Requires pgvector >= 0.5.0; creation may fail if extension unavailable
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
        CREATE INDEX IF NOT EXISTS idx_kb_embedding_vector ON knowledge.kb_embedding
            USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        -- Index creation failed (pgvector not available or version too old)
        -- This is non-fatal; embeddings table still works without the index
        NULL;
END $$;

COMMENT ON TABLE knowledge.kb_embedding IS 'Phase-6 6C: Vector embeddings for knowledge documents (pgvector)';
COMMENT ON COLUMN knowledge.kb_embedding.doc_id IS 'Foreign key to knowledge.kb_document';
COMMENT ON COLUMN knowledge.kb_embedding.embedding IS 'Vector embedding (1024 dimensions)';

