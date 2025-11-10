-- 050_matviews.sql
-- Materialized views for Atlas and reporting
-- Idempotent: safe to run multiple times

BEGIN;

-- ===============================
-- MATERIALIZED VIEWS: Run Summaries
-- ===============================

-- Pipeline run summary (for Atlas dashboard)
CREATE MATERIALIZED VIEW IF NOT EXISTS ops.pipeline_run_summary AS
SELECT
    run_id,
    workflow,
    MIN(started_at) AS run_started_at,
    MAX(finished_at) AS run_finished_at,
    COUNT(*) FILTER (WHERE event = 'node_start') AS nodes_started,
    COUNT(*) FILTER (WHERE event = 'node_end') AS nodes_completed,
    COUNT(*) FILTER (WHERE event = 'node_error') AS nodes_failed,
    SUM(duration_ms) AS total_duration_ms,
    SUM(items_in) AS total_items_in,
    SUM(items_out) AS total_items_out,
    COUNT(DISTINCT node) AS unique_nodes
FROM telemetry.metrics_log
GROUP BY run_id, workflow;

-- Index for fast lookups
CREATE UNIQUE INDEX IF NOT EXISTS idx_pipeline_run_summary_run_id 
    ON ops.pipeline_run_summary(run_id);

-- Node performance summary
CREATE MATERIALIZED VIEW IF NOT EXISTS ops.node_performance_summary AS
SELECT
    node,
    workflow,
    COUNT(*) AS execution_count,
    AVG(duration_ms) AS avg_duration_ms,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY duration_ms) AS median_duration_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration_ms) AS p95_duration_ms,
    SUM(items_in) AS total_items_in,
    SUM(items_out) AS total_items_out,
    COUNT(*) FILTER (WHERE status = 'error') AS error_count,
    MAX(started_at) AS last_execution_at
FROM telemetry.metrics_log
WHERE event = 'node_end'
GROUP BY node, workflow;

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_node_performance_summary_node 
    ON ops.node_performance_summary(node, workflow);

-- Graph statistics summary (for Atlas)
CREATE MATERIALIZED VIEW IF NOT EXISTS ops.graph_stats_summary AS
SELECT
    COUNT(DISTINCT n.node_id) AS total_nodes,
    COUNT(DISTINCT e.edge_id) AS total_edges,
    COUNT(DISTINCT e.src_node_id) AS nodes_with_outgoing_edges,
    COUNT(DISTINCT e.dst_node_id) AS nodes_with_incoming_edges,
    AVG(e.edge_strength) AS avg_edge_strength,
    COUNT(*) FILTER (WHERE e.edge_strength >= 0.90) AS strong_edges,
    COUNT(*) FILTER (WHERE e.edge_strength >= 0.75 AND e.edge_strength < 0.90) AS weak_edges,
    MAX(n.created_at) AS last_node_created_at,
    MAX(e.created_at) AS last_edge_created_at
FROM gematria.nodes n
LEFT JOIN gematria.edges e ON n.node_id = e.src_node_id OR n.node_id = e.dst_node_id;

-- Refresh functions (call these periodically or after data updates)
-- REFRESH MATERIALIZED VIEW CONCURRENTLY ops.pipeline_run_summary;
-- REFRESH MATERIALIZED VIEW CONCURRENTLY ops.node_performance_summary;
-- REFRESH MATERIALIZED VIEW CONCURRENTLY ops.graph_stats_summary;

COMMIT;

