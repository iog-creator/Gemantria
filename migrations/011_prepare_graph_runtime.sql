-- Idempotent stubs to prevent runtime failures while we wire full persistence

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname='gematria' AND tablename='runs') THEN
    CREATE TABLE gematria.runs(
      run_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      book text, started_at timestamptz DEFAULT now(), finished_at timestamptz, status text
    );
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname='gematria' AND tablename='concepts') THEN
    CREATE TABLE gematria.concepts(
      concept_id bigserial PRIMARY KEY,
      surface text, gematria_value int, class text, analysis jsonb, sources jsonb
    );
  END IF;
END $$;
