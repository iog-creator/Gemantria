-- Migration 056: TSVECTOR + GIN Index for Hybrid RAG
-- Purpose: Enable hybrid search (semantic + keyword) for faster queries
-- Related: Gate 2 of KB Registry Architectural Course Correction

BEGIN;

-- Add TSVECTOR column
ALTER TABLE control.doc_fragment
    ADD COLUMN IF NOT EXISTS content_tsvector tsvector;

-- Create GIN index for full-text search
CREATE INDEX IF NOT EXISTS idx_doc_fragment_content_tsvector
    ON control.doc_fragment
    USING gin (content_tsvector);

-- Update trigger to auto-populate TSVECTOR
CREATE OR REPLACE FUNCTION control.update_doc_fragment_tsvector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.content_tsvector := to_tsvector('english', COALESCE(NEW.content, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop trigger if it exists (to avoid conflicts on re-run)
DROP TRIGGER IF EXISTS doc_fragment_tsvector_update ON control.doc_fragment;

CREATE TRIGGER doc_fragment_tsvector_update
    BEFORE INSERT OR UPDATE ON control.doc_fragment
    FOR EACH ROW
    EXECUTE FUNCTION control.update_doc_fragment_tsvector();

-- Backfill existing fragments
UPDATE control.doc_fragment
SET content_tsvector = to_tsvector('english', COALESCE(content, ''))
WHERE content_tsvector IS NULL;

COMMIT;

