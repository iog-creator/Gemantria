CREATE SCHEMA IF NOT EXISTS gematria;
CREATE TABLE IF NOT EXISTS gematria.runs_ledger (
  run_id      TEXT PRIMARY KEY,
  book        TEXT NOT NULL,
  started_at  TIMESTAMPTZ DEFAULT now(),
  finished_at TIMESTAMPTZ,
  notes       TEXT
);
