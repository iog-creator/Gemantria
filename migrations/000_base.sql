-- P1-DB base: schemas + minimal tables needed by current pipeline

CREATE SCHEMA IF NOT EXISTS gematria;

-- Tracks applied migrations (very small, no deps)
CREATE TABLE IF NOT EXISTS gematria.schema_migrations (
  id         TEXT PRIMARY KEY,
  applied_at TIMESTAMPTZ DEFAULT now()
);

-- Nouns discovered (subset to keep phase 1 tight)
CREATE TABLE IF NOT EXISTS gematria.nouns (
  noun_id    UUID PRIMARY KEY,
  surface    TEXT NOT NULL,
  class      TEXT,
  lemma      TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Optional: verse cross-references captured during enrichment (P11)
CREATE TABLE IF NOT EXISTS gematria.enrichment_crossrefs (
  id           BIGSERIAL PRIMARY KEY,
  run_id       TEXT NOT NULL,
  osis_ref_src TEXT NOT NULL,
  surface      TEXT NOT NULL,
  strongs_id   TEXT,
  target_osis  TEXT NOT NULL,
  target_label TEXT,
  confidence   REAL,
  created_at   TIMESTAMPTZ DEFAULT now()
);
