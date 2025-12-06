-- Migration 055: IVFFlat Index for RAG Performance
-- Purpose: Fast Approximate Nearest Neighbor (ANN) search for RAG
-- Requirement: Must have >1000 embeddings to be effective
-- Related: Gate 2 of KB Registry Architectural Course Correction

BEGIN;

CREATE INDEX IF NOT EXISTS idx_doc_embedding_vector
    ON control.doc_embedding
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

COMMIT;

