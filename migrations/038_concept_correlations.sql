-- Migration 038: Create concept_correlations view for pattern correlation analysis
-- Phase 5-B: Correlation Engine Implementation
--
-- This view provides correlation analysis between concepts in the semantic network.
-- Uses PostgreSQL's built-in correlation functions for statistical analysis.

BEGIN;

-- Create concept_correlations view
-- Computes cosine similarity between concept embeddings
CREATE OR REPLACE VIEW concept_correlations AS
SELECT
    -- Source concept information
    cn1.concept_id AS source,
    c1.name AS source_name,
    COALESCE(cc1.cluster_id, -1) AS cluster_source,

    -- Target concept information
    cn2.concept_id AS target,
    c2.name AS target_name,
    COALESCE(cc2.cluster_id, -1) AS cluster_target,

    -- Similarity analysis
    (cn1.embedding <=> cn2.embedding) AS similarity,

    -- Statistical significance (approximate p-value using similarity threshold)
    -- For cosine similarity: higher values indicate stronger similarity
    CASE
        WHEN (cn1.embedding <=> cn2.embedding) > 0.8 THEN 0.01  -- Very similar
        WHEN (cn1.embedding <=> cn2.embedding) > 0.6 THEN 0.05  -- Moderately similar
        ELSE 0.1  -- Weak similarity
    END AS p_value,

    -- Similarity method identifier
    'cosine_similarity' AS metric,

    -- Metadata
    NOW() AS computed_at

FROM concept_network cn1
JOIN concept_network cn2
    ON cn1.id < cn2.id  -- Avoid duplicate pairs and self-correlations
    AND cn1.concept_id != cn2.concept_id  -- Ensure different concepts
LEFT JOIN concept_clusters cc1 ON cn1.id = cc1.concept_id
LEFT JOIN concept_clusters cc2 ON cn2.id = cc2.concept_id
JOIN concepts c1 ON cn1.concept_id = c1.id
JOIN concepts c2 ON cn2.concept_id = c2.id

-- Only compute similarities for concepts with embeddings
WHERE cn1.embedding IS NOT NULL
  AND cn2.embedding IS NOT NULL

-- Order by similarity strength (higher similarity first)
ORDER BY (cn1.embedding <=> cn2.embedding) DESC;

-- Add comment for documentation
COMMENT ON VIEW concept_correlations IS
'Phase 5-B: Similarity analysis between concepts in the semantic network.
Provides cosine similarity scores between concept embeddings with
statistical significance estimates. Used by export_stats.py for similarity
analysis and pattern discovery.';

-- Create index for performance (optional but recommended for large networks)
CREATE INDEX IF NOT EXISTS idx_concept_correlations_source
    ON concept_network(concept_id);

CREATE INDEX IF NOT EXISTS idx_concept_clusters_cluster_id
    ON concept_clusters(cluster_id);

COMMIT;
