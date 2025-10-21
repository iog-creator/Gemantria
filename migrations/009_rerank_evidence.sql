BEGIN;

-- Add rerank evidence columns to concept_relations table
-- This supports PR-011: Rerank-Driven Relationship Refinement

ALTER TABLE concept_relations
    ADD COLUMN IF NOT EXISTS cosine NUMERIC(6,5),
    ADD COLUMN IF NOT EXISTS rerank_score NUMERIC(6,5),
    ADD COLUMN IF NOT EXISTS edge_strength NUMERIC(6,5),
    ADD COLUMN IF NOT EXISTS rerank_model TEXT,
    ADD COLUMN IF NOT EXISTS rerank_at TIMESTAMPTZ DEFAULT now();

-- Add constraint to ensure edge_strength is computed correctly
ALTER TABLE concept_relations
    ADD CONSTRAINT check_edge_strength
    CHECK (edge_strength IS NULL OR (edge_strength >= 0 AND edge_strength <= 1));

-- Add index for rerank_at for time-based queries
CREATE INDEX IF NOT EXISTS idx_concept_relations_rerank_at
    ON concept_relations (rerank_at);

-- Add index for rerank_score for filtering
CREATE INDEX IF NOT EXISTS idx_concept_relations_rerank_score
    ON concept_relations (rerank_score DESC);

-- Add index for edge_strength for strength-based queries
CREATE INDEX IF NOT EXISTS idx_concept_relations_edge_strength
    ON concept_relations (edge_strength DESC);

-- Update existing rows to populate cosine with current similarity values
-- (edge_strength and rerank_score will be NULL for existing data)
UPDATE concept_relations
SET cosine = similarity
WHERE cosine IS NULL;

COMMIT;

