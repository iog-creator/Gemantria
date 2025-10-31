-- Metrics Views & Materialized Views
-- Schema: gematria (same DB as analysis)

BEGIN;

-- 1) A flat, normalized view for analysts
CREATE OR REPLACE VIEW v_metrics_flat AS
SELECT
  id,
  run_id,
  workflow,
  thread_id,
  node,
  event,
  status,
  started_at,
  finished_at,
  EXTRACT(EPOCH FROM (finished_at - started_at)) * 1000.0 AS duration_ms,
  COALESCE(items_in, 0)  AS items_in,
  COALESCE(items_out, 0) AS items_out,
  error_json,
  meta
FROM metrics_log;

-- 2) Last event per (run_id, node) for quick "where are we" checks
CREATE OR REPLACE VIEW v_metrics_last_event AS
SELECT DISTINCT ON (run_id, node)
  run_id, node, event, status, started_at, finished_at
FROM metrics_log
ORDER BY run_id, node, started_at DESC;

-- 3) Pipeline runs (derive start/end + overall duration)
CREATE OR REPLACE VIEW v_pipeline_runs AS
WITH bounds AS (
  SELECT
    run_id,
    MIN(started_at) AS t0,
    MAX(COALESCE(finished_at, started_at)) AS t1
  FROM metrics_log
  GROUP BY run_id
)
SELECT
  b.run_id,
  b.t0 AS started_at,
  b.t1 AS finished_at,
  EXTRACT(EPOCH FROM (b.t1 - b.t0)) * 1000.0 AS duration_ms
FROM bounds b;

-- 4) Node latency aggregates (rolling 7d)
CREATE OR REPLACE VIEW v_node_latency_7d AS
SELECT
  node,
  COUNT(*) AS calls,
  AVG(duration_ms)           AS avg_ms,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY duration_ms) AS p50_ms,
  PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY duration_ms) AS p90_ms,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration_ms) AS p95_ms,
  PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY duration_ms) AS p99_ms
FROM v_metrics_flat
WHERE event = 'node_end'
  AND started_at >= NOW() - INTERVAL '7 days'
GROUP BY node
ORDER BY node;

-- 5) Throughput (items_out per minute, rolling 24h)
CREATE OR REPLACE VIEW v_node_throughput_24h AS
SELECT
  node,
  date_trunc('minute', finished_at) AS minute,
  SUM(items_out) AS items_out
FROM v_metrics_flat
WHERE event = 'node_end'
  AND finished_at >= NOW() - INTERVAL '24 hours'
GROUP BY node, date_trunc('minute', finished_at)
ORDER BY minute DESC, node;

-- 6) Recent errors (7d) with counts and last occurrence
CREATE OR REPLACE VIEW v_recent_errors_7d AS
SELECT
  node,
  COUNT(*) AS error_count,
  MAX(finished_at) AS last_seen,
  JSONB_AGG(DISTINCT error_json->>'type') FILTER (WHERE error_json IS NOT NULL) AS error_types
FROM v_metrics_flat
WHERE event = 'node_error'
  AND started_at >= NOW() - INTERVAL '7 days'
GROUP BY node
ORDER BY error_count DESC, last_seen DESC;

-- 7) Optional: Materialized view for latency (faster dashboards)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_node_latency_7d AS
SELECT * FROM v_node_latency_7d;

CREATE INDEX IF NOT EXISTS mv_node_latency_7d_node_idx ON mv_node_latency_7d (node);

-- Helper function to refresh materialized views
CREATE OR REPLACE FUNCTION refresh_metrics_materialized()
RETURNS void LANGUAGE plpgsql AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY mv_node_latency_7d;
END $$;

COMMIT;
