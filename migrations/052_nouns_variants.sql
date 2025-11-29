-- Phase 2: Ketiv/Qere Policy - Add variant support to nouns table
-- ADR-002: Ketiv primary; variants recorded with variant_type and span information

-- Add variant tracking columns to gematria.nouns
ALTER TABLE gematria.nouns
  ADD COLUMN IF NOT EXISTS variant_type TEXT,
  ADD COLUMN IF NOT EXISTS variant_surface TEXT,
  ADD COLUMN IF NOT EXISTS span_start INTEGER,
  ADD COLUMN IF NOT EXISTS span_end INTEGER,
  ADD COLUMN IF NOT EXISTS is_ketiv BOOLEAN DEFAULT TRUE;

-- Add comment explaining Ketiv-primary policy
COMMENT ON COLUMN gematria.nouns.is_ketiv IS 'TRUE if this is the Ketiv (written form), FALSE if Qere (read form). Ketiv is primary for gematria calculations per ADR-002.';
COMMENT ON COLUMN gematria.nouns.variant_type IS 'Type of variant: ketiv, qere, or other textual variant';
COMMENT ON COLUMN gematria.nouns.variant_surface IS 'Alternative surface form (e.g., Qere reading when this record is Ketiv)';
COMMENT ON COLUMN gematria.nouns.span_start IS 'Character position where variant begins in source text';
COMMENT ON COLUMN gematria.nouns.span_end IS 'Character position where variant ends in source text';

-- Create index for variant lookups
CREATE INDEX IF NOT EXISTS idx_nouns_variant_type ON gematria.nouns(variant_type) WHERE variant_type IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_nouns_is_ketiv ON gematria.nouns(is_ketiv);

