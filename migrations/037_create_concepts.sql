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
-- Supports multiple table naming patterns: concept_network, gematria.concept_network, etc.
DO $$
DECLARE
    network_table_name TEXT;
    concept_id_col TEXT := 'concept_id';
BEGIN
  -- Find the concept network table (try multiple naming patterns)
  SELECT table_name INTO network_table_name
  FROM information_schema.tables
  WHERE table_name IN ('concept_network', 'concepts_network', 'semantic_network')
     AND table_schema IN ('public', 'gematria')
  ORDER BY
    CASE WHEN table_schema = 'gematria' THEN 1 ELSE 2 END,
    CASE WHEN table_name = 'concept_network' THEN 1 ELSE 2 END
  LIMIT 1;

  IF network_table_name IS NOT NULL THEN
    -- Check if concept_id column exists
    IF EXISTS (
      SELECT 1 FROM information_schema.columns
      WHERE table_name = network_table_name
        AND column_name = concept_id_col
        AND table_schema = (SELECT table_schema FROM information_schema.tables WHERE table_name = network_table_name LIMIT 1)
    ) THEN
      -- Dynamic backfill using EXECUTE to handle schema-qualified table names
      EXECUTE format(
        'INSERT INTO concepts (id, name, content_hash) ' ||
        'SELECT DISTINCT cn.%I, ''concept_''||LEFT(cast(cn.%I AS TEXT), 8), md5(cast(cn.%I AS TEXT)) ' ||
        'FROM %I cn ' ||
        'LEFT JOIN concepts c ON c.id = cn.%I ' ||
        'WHERE c.id IS NULL',
        concept_id_col, concept_id_col, concept_id_col, network_table_name, concept_id_col
      );
    END IF;
  END IF;
END$$;
