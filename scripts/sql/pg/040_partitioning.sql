-- 040_partitioning.sql
-- Partitioning for time-series tables (rolling window)
-- Idempotent: safe to run multiple times
-- Note: Partitioning requires careful planning; this is a skeleton

BEGIN;

-- ===============================
-- PARTITIONING: telemetry.metrics_log
-- ===============================

-- Strategy: Range partitioning by date (rolling 10-day window)
-- Note: This is a template; actual implementation should:
-- 1. Create parent table with partitioning
-- 2. Create partitions for current and future dates
-- 3. Set up automatic partition creation (via pg_cron or application logic)
-- 4. Implement partition pruning/dropping for old data

-- Example structure (commented - requires careful migration planning):
/*
-- Drop existing table if recreating (CAUTION: data loss)
-- DROP TABLE IF EXISTS telemetry.metrics_log CASCADE;

-- Create partitioned parent table
CREATE TABLE telemetry.metrics_log (
    id BIGSERIAL,
    run_id UUID NOT NULL,
    workflow TEXT NOT NULL,
    thread_id TEXT NOT NULL,
    node TEXT NOT NULL,
    event TEXT NOT NULL CHECK (event IN ('node_start','node_end','node_error','pipeline_start','pipeline_end')),
    status TEXT NOT NULL CHECK (status IN ('ok','error','skip')),
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ,
    duration_ms NUMERIC,
    items_in INTEGER,
    items_out INTEGER,
    error_json JSONB,
    meta JSONB,
    PRIMARY KEY (id, started_at)
) PARTITION BY RANGE (started_at);

-- Create partitions (example: daily partitions for 10 days)
-- DO $$
-- DECLARE
--     day_offset INTEGER;
--     partition_name TEXT;
--     partition_start DATE;
--     partition_end DATE;
-- BEGIN
--     FOR day_offset IN 0..9 LOOP
--         partition_start := CURRENT_DATE + (day_offset || ' days')::INTERVAL;
--         partition_end := partition_start + '1 day'::INTERVAL;
--         partition_name := 'metrics_log_' || to_char(partition_start, 'YYYY_MM_DD');
--         
--         EXECUTE format('
--             CREATE TABLE IF NOT EXISTS telemetry.%I PARTITION OF telemetry.metrics_log
--             FOR VALUES FROM (%L) TO (%L)',
--             partition_name, partition_start, partition_end
--         );
--     END LOOP;
-- END $$;

-- Create indexes on parent (propagates to partitions)
-- CREATE INDEX IF NOT EXISTS idx_metrics_log_run ON telemetry.metrics_log(run_id);
-- CREATE INDEX IF NOT EXISTS idx_metrics_log_thread ON telemetry.metrics_log(thread_id);
-- CREATE INDEX IF NOT EXISTS idx_metrics_log_node_ts ON telemetry.metrics_log(node, started_at DESC);
*/

-- For now, keep non-partitioned table (migration to partitioning is P4+)
-- Partitioning will be implemented when telemetry volume requires it

COMMIT;

