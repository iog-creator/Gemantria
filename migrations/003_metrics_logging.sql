-- Metrics & Logging tables
-- Schema: gematria (same DB as analysis)

BEGIN;

CREATE TABLE IF NOT EXISTS metrics_log (
    id                BIGSERIAL PRIMARY KEY,
    run_id            UUID        NOT NULL,
    workflow          TEXT        NOT NULL,
    thread_id         TEXT        NOT NULL,
    node              TEXT        NOT NULL,
    event             TEXT        NOT NULL CHECK (event IN ('node_start','node_end','node_error','pipeline_start','pipeline_end')),
    status            TEXT        NOT NULL CHECK (status IN ('ok','error','skip')),
    started_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at       TIMESTAMPTZ,
    duration_ms       NUMERIC,
    items_in          INTEGER,
    items_out         INTEGER,
    error_json        JSONB,
    meta              JSONB        -- freeform: batch_size, attempt, checkpoint_id, etc.
);

CREATE INDEX IF NOT EXISTS metrics_log_run_idx     ON metrics_log (run_id);
CREATE INDEX IF NOT EXISTS metrics_log_thread_idx  ON metrics_log (thread_id);
CREATE INDEX IF NOT EXISTS metrics_log_node_idx    ON metrics_log (node, started_at DESC);
CREATE INDEX IF NOT EXISTS metrics_log_event_idx   ON metrics_log (event, started_at DESC);
CREATE INDEX IF NOT EXISTS metrics_log_workflow_ts ON metrics_log (workflow, started_at DESC);

COMMIT;
