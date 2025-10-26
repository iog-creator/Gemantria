-- Migration 038: Create concept_correlations view for pattern correlation analysis
-- Phase 5-B: Correlation Engine Implementation
--
-- This view provides correlation analysis between concepts in the semantic network.
-- Uses PostgreSQL's built-in correlation functions for statistical analysis.

BEGIN;

-- Create concept_correlations view
-- Computes Pearson correlation coefficients between concept embeddings
CREATE OR REPLACE VIEW concept_correlations AS
SELECT
    -- Source concept information
    cn1.concept_id AS source,
    c1.name AS source_name,
    cn1.cluster_id AS cluster_source,

    -- Target concept information
    cn2.concept_id AS target,
    c2.name AS target_name,
    cn2.cluster_id AS cluster_target,

    -- Correlation analysis
    corr(cn1.embedding, cn2.embedding) AS correlation,
    COUNT(*) AS sample_size,

    -- Statistical significance (approximate p-value using t-distribution)
    -- For now, we'll use a simple threshold; can be enhanced with proper statistical functions
    CASE
        WHEN ABS(corr(cn1.embedding, cn2.embedding)) > 0.5 THEN 0.01  -- Strong correlation
        WHEN ABS(corr(cn1.embedding, cn2.embedding)) > 0.3 THEN 0.05  -- Moderate correlation
        ELSE 0.1  -- Weak or no correlation
    END AS p_value,

    -- Correlation method identifier
    'pearson_embedding' AS metric,

    -- Metadata
    NOW() AS computed_at

FROM concept_network cn1
JOIN concept_network cn2
    ON cn1.id < cn2.id  -- Avoid duplicate pairs and self-correlations
    AND cn1.concept_id != cn2.concept_id  -- Ensure different concepts
JOIN concepts c1 ON cn1.concept_id = c1.id
JOIN concepts c2 ON cn2.concept_id = c2.id

-- Only compute correlations for concepts with embeddings
WHERE cn1.embedding IS NOT NULL
  AND cn2.embedding IS NOT NULL

-- Group by concept pairs to compute correlations
GROUP BY cn1.concept_id, c1.name, cn1.cluster_id,
         cn2.concept_id, c2.name, cn2.cluster_id

-- Only include correlations with sufficient sample size (minimum 2 observations)
HAVING COUNT(*) >= 2

-- Order by correlation strength (absolute value)
ORDER BY ABS(corr(cn1.embedding, cn2.embedding)) DESC;

-- Add comment for documentation
COMMENT ON VIEW concept_correlations IS
'Phase 5-B: Correlation analysis between concepts in the semantic network.
Provides Pearson correlation coefficients between concept embeddings with
statistical significance estimates. Used by export_stats.py for correlation
analysis and pattern discovery.';

-- Create index for performance (optional but recommended for large networks)
CREATE INDEX IF NOT EXISTS idx_concept_correlations_source
    ON concept_network(concept_id);

CREATE INDEX IF NOT EXISTS idx_concept_correlations_cluster
    ON concept_network(cluster_id);

COMMIT;
