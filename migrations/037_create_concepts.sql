-- 037_create_concepts.sql
-- Idempotent create for `concepts` and minimal backfill to unblock joins
CREATE EXTENSION IF NOT EXISTS pgcrypto;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_schema='public' AND table_name='concepts'
  ) THEN
    CREATE TABLE public.concepts (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      name TEXT NOT NULL,
      hebrew_text TEXT,
      gematria_value INTEGER,
      strong_number TEXT,
      primary_verse TEXT,
      book TEXT,
      chapter INTEGER,
      freq INTEGER,
      content_hash TEXT UNIQUE,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE INDEX IF NOT EXISTS idx_concepts_name ON concepts (name);
    CREATE INDEX IF NOT EXISTS idx_concepts_hash ON concepts (content_hash);
  END IF;
END$$;

-- Optional: stub backfill so existing concept_network joins work
-- (replace with real data ingestion later)
INSERT INTO concepts (name, content_hash)
SELECT DISTINCT 'stub_concept_' || concept_id, 'stub_' || concept_id
FROM concept_network
WHERE concept_id NOT IN (SELECT id FROM concepts)
ON CONFLICT (content_hash) DO NOTHING;
