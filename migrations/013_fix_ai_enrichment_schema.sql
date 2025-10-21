-- Fix ai_enrichment_log schema to allow NULL confidence_model
-- Schema: gematria

BEGIN;

ALTER TABLE ai_enrichment_log ALTER COLUMN confidence_model DROP NOT NULL;

COMMIT;

