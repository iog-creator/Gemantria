-- Confidence Validation Storage
-- Schema: gematria (same DB as analysis)

BEGIN;

CREATE TABLE IF NOT EXISTS confidence_validation_log (
    id                    BIGSERIAL PRIMARY KEY,
    run_id                UUID        NOT NULL,
    node                  TEXT        NOT NULL,
    noun_id               UUID        NOT NULL,
    gematria_confidence   NUMERIC(5,4) CHECK (gematria_confidence BETWEEN 0 AND 1),
    ai_confidence         NUMERIC(5,4) CHECK (ai_confidence BETWEEN 0 AND 1),
    gematria_threshold    NUMERIC(5,4) CHECK (gematria_threshold BETWEEN 0 AND 1),
    ai_threshold          NUMERIC(5,4) CHECK (ai_threshold BETWEEN 0 AND 1),
    validation_passed     BOOLEAN     NOT NULL,
    abort_reason          TEXT,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    meta                  JSONB       NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS confidence_validation_run_idx     ON confidence_validation_log(run_id);
CREATE INDEX IF NOT EXISTS confidence_validation_node_idx    ON confidence_validation_log(node);
CREATE INDEX IF NOT EXISTS confidence_validation_passed_idx  ON confidence_validation_log(validation_passed);

-- Add a view for run confidence summary
CREATE OR REPLACE VIEW v_run_confidence_summary AS
SELECT
    run_id,
    COUNT(*) as total_validations,
    AVG(gematria_confidence) as avg_gematria_confidence,
    AVG(ai_confidence) as avg_ai_confidence,
    SUM(CASE WHEN validation_passed THEN 1 ELSE 0 END) as passed_validations,
    SUM(CASE WHEN NOT validation_passed THEN 1 ELSE 0 END) as failed_validations,
    MIN(created_at) as run_started_at,
    MAX(created_at) as run_completed_at
FROM confidence_validation_log
GROUP BY run_id;

COMMIT;
