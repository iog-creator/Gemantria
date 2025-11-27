-- Migration 049: Add embedding column to control.kb_document
-- Purpose: Enable semantic search for documentation by adding vector support
-- Context: Robust Vector DMS & Intelligent Discovery (Phase 2)
-- Depends on: pgvector extension (verified available)

BEGIN;

-- Add embedding column (1024 dimensions for BGE-M3)
ALTER TABLE control.kb_document
ADD COLUMN IF NOT EXISTS embedding vector(1024);

-- Create HNSW index for fast similarity search
-- using cosine distance (vector_cosine_ops)
CREATE INDEX IF NOT EXISTS idx_kb_document_embedding 
ON control.kb_document 
USING hnsw (embedding vector_cosine_ops);

COMMENT ON COLUMN control.kb_document.embedding IS 'BGE-M3 embedding vector (1024-dim)';

COMMIT;
