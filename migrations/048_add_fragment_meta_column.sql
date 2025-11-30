-- Migration: Add meta JSONB column to control.doc_fragment
-- Purpose: Store AI-derived classification metadata for document fragments
-- Context: Layer 3 Phase 3 - AI Classification Metadata
-- Notes:
--   - Adds meta JSONB column with default empty object
--   - Enables storing subsystem, doc_role, importance, phase_relevance, etc.
--   - Used by classify_fragments.py to annotate fragments with AI metadata

BEGIN;

-- Add meta JSONB column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'control'
        AND table_name = 'doc_fragment'
        AND column_name = 'meta'
    ) THEN
        ALTER TABLE control.doc_fragment
            ADD COLUMN meta JSONB DEFAULT '{}'::jsonb;
        
        -- Add index for meta queries (e.g., WHERE meta->>'subsystem' = 'pm')
        CREATE INDEX IF NOT EXISTS idx_doc_fragment_meta
            ON control.doc_fragment USING gin (meta);
    END IF;
END $$;

COMMIT;

