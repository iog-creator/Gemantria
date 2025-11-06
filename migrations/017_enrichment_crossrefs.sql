-- Migration: Add enrichment cross-references table
-- Purpose: Store OSIS-normalized verse cross-references extracted from enrichment insights
-- Schema: gematria

BEGIN;

CREATE TABLE IF NOT EXISTS gematria.enrichment_crossrefs (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(255) NOT NULL,
    osis_ref_src VARCHAR(50) NOT NULL,  -- Source noun's OSIS reference (e.g., "Gen.1.1")
    surface VARCHAR(255) NOT NULL,      -- Hebrew surface form of the noun
    target_osis VARCHAR(50) NOT NULL,   -- Target verse OSIS reference (e.g., "Ps.30.5")
    target_label VARCHAR(255) NOT NULL, -- Original label from enrichment text (e.g., "Psalm 30:5")
    confidence DECIMAL(3,2) NOT NULL,   -- Confidence score of the enrichment (0.00-1.00)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for efficient lookups by run_id
CREATE INDEX IF NOT EXISTS idx_enrichment_crossrefs_run_id
    ON gematria.enrichment_crossrefs(run_id);

-- Index for efficient lookups by source reference
CREATE INDEX IF NOT EXISTS idx_enrichment_crossrefs_src
    ON gematria.enrichment_crossrefs(osis_ref_src);

-- Index for efficient lookups by target reference
CREATE INDEX IF NOT EXISTS idx_enrichment_crossrefs_target
    ON gematria.enrichment_crossrefs(target_osis);

-- Composite index for common queries
CREATE INDEX IF NOT EXISTS idx_enrichment_crossrefs_run_src
    ON gematria.enrichment_crossrefs(run_id, osis_ref_src);

COMMENT ON TABLE gematria.enrichment_crossrefs IS 'OSIS-normalized verse cross-references extracted from AI enrichment insights';
COMMENT ON COLUMN gematria.enrichment_crossrefs.osis_ref_src IS 'Source noun verse reference in OSIS format';
COMMENT ON COLUMN gematria.enrichment_crossrefs.target_osis IS 'Referenced verse in OSIS format';
COMMENT ON COLUMN gematria.enrichment_crossrefs.target_label IS 'Original text label before OSIS normalization';

COMMIT;
