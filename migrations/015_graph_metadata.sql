BEGIN;

-- Optional migration: Add metadata table for richer graph exports
-- Purpose: Enable enhanced JSON-LD/RDF exports with human-readable labels and descriptions
-- Impact: Adds optional metadata storage for better semantic web compliance
-- ADR: ADR-015 JSON-LD & Visualization

CREATE TABLE IF NOT EXISTS concept_metadata (
  concept_id UUID PRIMARY KEY,
  label TEXT NOT NULL,
  description TEXT,
  source TEXT,  -- e.g., 'genesis', 'exodus', or 'derived'
  language TEXT DEFAULT 'he',  -- ISO language code
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Add foreign key constraint to concept_network (optional, allows nulls)
-- ALTER TABLE concept_metadata ADD CONSTRAINT fk_concept_metadata_concept_id
--   FOREIGN KEY (concept_id) REFERENCES concept_network(concept_id) ON DELETE CASCADE;

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_concept_metadata_label ON concept_metadata (label);
CREATE INDEX IF NOT EXISTS idx_concept_metadata_source ON concept_metadata (source);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_concept_metadata_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at
CREATE TRIGGER trig_concept_metadata_updated_at
  BEFORE UPDATE ON concept_metadata
  FOR EACH ROW EXECUTE FUNCTION update_concept_metadata_updated_at();

COMMIT;
