-- AI Metadata Storage
-- Schema: gematria (same DB as analysis)

BEGIN;

CREATE TABLE IF NOT EXISTS ai_enrichment_log (
    id                BIGSERIAL PRIMARY KEY,
    run_id            UUID        NOT NULL,
    node              TEXT        NOT NULL,
    noun_id           UUID        NOT NULL,
    model_name        TEXT        NOT NULL,
    confidence_model  TEXT        NULL,
    confidence_score  NUMERIC(5,4) CHECK (confidence_score BETWEEN 0 AND 1),
    insights          TEXT        NOT NULL,
    significance      TEXT        NOT NULL,
    tokens_used       INTEGER     NOT NULL,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    meta              JSONB       NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS ai_enrichment_run_idx   ON ai_enrichment_log(run_id);
CREATE INDEX IF NOT EXISTS ai_enrichment_node_idx  ON ai_enrichment_log(node);

COMMIT;
