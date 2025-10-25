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

-- Optional: stub backfill so existing network rows don't break joins
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='concept_network')
     AND EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='concept_network' AND column_name='concept_id') THEN
    INSERT INTO concepts (id, name, content_hash)
    SELECT DISTINCT cn.concept_id, 'concept_'||LEFT(cast(cn.concept_id AS TEXT), 8), md5(cast(cn.concept_id AS TEXT))
    FROM concept_network cn
    LEFT JOIN concepts c ON c.id = cn.concept_id
    WHERE c.id IS NULL;
  END IF;
END$$;
