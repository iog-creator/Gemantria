-- Migration 018: Pipeline schema enhancements for LangGraph completion
-- Adds missing tables and columns for concept_occurrences, concept_embeddings alignment,
-- and run_id tracking for centrality/clusters

BEGIN;

-- Concept occurrences table (tracks where concepts appear in text)
CREATE TABLE IF NOT EXISTS concept_occurrences (
    concept_id UUID NOT NULL,
    ref TEXT NOT NULL,
    offset INT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (concept_id, ref, offset)
);

-- Index for efficient lookups
CREATE INDEX IF NOT EXISTS idx_concept_occurrences_concept_id ON concept_occurrences(concept_id);
CREATE INDEX IF NOT EXISTS idx_concept_occurrences_ref ON concept_occurrences(ref);

-- Ensure concept_relations has edge_strength and class columns
DO $$
BEGIN
    -- Add edge_strength column if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'concept_relations' AND column_name = 'edge_strength') THEN
        ALTER TABLE concept_relations ADD COLUMN edge_strength FLOAT;
        -- Compute edge_strength from existing cosine and rerank_score if available
        UPDATE concept_relations
        SET edge_strength = COALESCE(
            0.5 * COALESCE(cosine, 0.0) + 0.5 * COALESCE(rerank_score, 0.0),
            cosine,
            0.0
        )
        WHERE edge_strength IS NULL;
    END IF;

    -- Add class column if missing (strong/weak/candidate)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'concept_relations' AND column_name = 'class') THEN
        ALTER TABLE concept_relations ADD COLUMN class TEXT;
        -- Classify existing edges based on edge_strength
        UPDATE concept_relations
        SET class = CASE
            WHEN edge_strength >= 0.90 THEN 'strong'
            WHEN edge_strength >= 0.75 THEN 'weak'
            ELSE 'candidate'
        END
        WHERE class IS NULL AND edge_strength IS NOT NULL;
    END IF;

    -- Ensure relation_type constraint allows all types
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.check_constraints
        WHERE constraint_name = 'concept_relations_type_check'
    ) THEN
        ALTER TABLE concept_relations
        ADD CONSTRAINT concept_relations_type_check
        CHECK (relation_type IN ('strong', 'weak', 'candidate', 'semantic', 'cooccur', 'theology', 'other'));
    END IF;
END $$;

-- Add run_id to concept_centrality for tracking which run computed the metrics
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'concept_centrality' AND column_name = 'run_id') THEN
        ALTER TABLE concept_centrality ADD COLUMN run_id UUID;
        CREATE INDEX IF NOT EXISTS idx_concept_centrality_run_id ON concept_centrality(run_id);
    END IF;
END $$;

-- Add run_id to concept_clusters for tracking which run computed the clusters
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'concept_clusters' AND column_name = 'run_id') THEN
        ALTER TABLE concept_clusters ADD COLUMN run_id UUID;
        CREATE INDEX IF NOT EXISTS idx_concept_clusters_run_id ON concept_clusters(run_id);
    END IF;

    -- Add algo and params columns if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'concept_clusters' AND column_name = 'algo') THEN
        ALTER TABLE concept_clusters ADD COLUMN algo TEXT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'concept_clusters' AND column_name = 'params') THEN
        ALTER TABLE concept_clusters ADD COLUMN params JSONB;
    END IF;
END $$;

-- Ensure concepts table has proper structure for SSOT
DO $$
BEGIN
    -- Add surface column if missing (canonical Hebrew surface form)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'concepts' AND column_name = 'surface') THEN
        ALTER TABLE concepts ADD COLUMN surface TEXT;
        -- Copy hebrew_text to surface if available
        UPDATE concepts SET surface = hebrew_text WHERE surface IS NULL AND hebrew_text IS NOT NULL;
    END IF;

    -- Add letters column if missing (array of Hebrew letters)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'concepts' AND column_name = 'letters') THEN
        ALTER TABLE concepts ADD COLUMN letters TEXT[];
    END IF;

    -- Add class column if missing (person/place/thing/other)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'concepts' AND column_name = 'class') THEN
        ALTER TABLE concepts ADD COLUMN class TEXT;
    END IF;

    -- Ensure analysis column exists (JSONB for enrichment data)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'concepts' AND column_name = 'analysis') THEN
        ALTER TABLE concepts ADD COLUMN analysis JSONB DEFAULT '{}'::jsonb;
    END IF;

    -- Ensure sources column exists (JSONB array for source references)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'concepts' AND column_name = 'sources') THEN
        ALTER TABLE concepts ADD COLUMN sources JSONB DEFAULT '[]'::jsonb;
    END IF;
END $$;

COMMIT;

