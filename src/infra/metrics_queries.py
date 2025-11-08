# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

from __future__ import annotations

import os

import psycopg

from .env_loader import ensure_env_loaded

# Ensure environment variables are loaded
ensure_env_loaded()

DSN = os.getenv("GEMATRIA_DSN")


def _q(sql: str, *params) -> list[tuple]:
    dsn = os.getenv("GEMATRIA_DSN")
    if not dsn:
        raise RuntimeError("GEMATRIA_DSN is not set")
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute(sql, params or None)
        return cur.fetchall()


def node_latency_7d() -> list[tuple]:
    return _q("SELECT node, calls, avg_ms, p50_ms, p90_ms, p95_ms, p99_ms FROM v_node_latency_7d ORDER BY node")  # noqa: E501


def pipeline_runs(limit: int = 50) -> list[tuple]:
    return _q(
        "SELECT run_id, started_at, finished_at, duration_ms FROM v_pipeline_runs ORDER BY started_at DESC LIMIT %s",  # noqa: E501
        limit,
    )


def recent_errors_7d() -> list[tuple]:
    return _q(
        "SELECT node, error_count, last_seen, error_types FROM v_recent_errors_7d ORDER BY error_count DESC, last_seen DESC"  # noqa: E501
    )


def node_throughput_24h(node: str | None = None) -> list[tuple]:
    if node:
        return _q(
            "SELECT minute, items_out FROM v_node_throughput_24h WHERE node=%s ORDER BY minute DESC",
            node,
        )
    return _q("SELECT node, minute, items_out FROM v_node_throughput_24h ORDER BY minute DESC")


def embedding_requests_24h() -> list[tuple]:
    """Get embedding request counts over the last 24 hours."""
    return _q(
        """
        SELECT DATE_TRUNC('hour', started_at) as hour,
               COUNT(*) as requests,
               SUM(CASE WHEN meta->>'embeddings_generated' IS NOT NULL
                        THEN (meta->>'embeddings_generated')::int ELSE 0 END) as total_embeddings
        FROM metrics_log
        WHERE node = 'network_aggregator' AND started_at > NOW() - INTERVAL '24 hours'
        GROUP BY hour
        ORDER BY hour DESC
    """
    )


def rerank_metrics_24h() -> list[tuple]:
    """Get rerank performance metrics over the last 24 hours."""
    return _q(
        """
        SELECT DATE_TRUNC('hour', started_at) as hour,
               SUM(CASE WHEN meta->>'rerank_calls' IS NOT NULL
                        THEN (meta->>'rerank_calls')::int ELSE 0 END) as rerank_calls,
               ROUND(AVG(CASE WHEN meta->>'rerank_yes_ratio' IS NOT NULL
                              THEN (meta->>'rerank_yes_ratio')::numeric ELSE NULL END), 3) as avg_yes_ratio,
               ROUND(AVG(CASE WHEN meta->>'avg_edge_strength' IS NOT NULL
                              THEN (meta->>'avg_edge_strength')::numeric ELSE NULL END), 3) as avg_edge_strength
        FROM metrics_log
        WHERE node = 'network_aggregator' AND started_at > NOW() - INTERVAL '24 hours'
        GROUP BY hour
        ORDER BY hour DESC
    """
    )


def qwen_usage_totals() -> list[tuple]:
    """Get total Qwen model usage statistics."""
    return _q(
        """
        SELECT
            COUNT(*) as total_runs,
            SUM(CASE WHEN meta->>'embeddings_generated' IS NOT NULL
                     THEN (meta->>'embeddings_generated')::int ELSE 0 END) as total_embeddings,
            SUM(CASE WHEN meta->>'rerank_calls' IS NOT NULL
                     THEN (meta->>'rerank_calls')::int ELSE 0 END) as total_rerank_calls,
            ROUND(AVG(CASE WHEN meta->>'rerank_yes_ratio' IS NOT NULL
                           THEN (meta->>'rerank_yes_ratio')::numeric ELSE NULL END), 3) as avg_yes_ratio,
            ROUND(AVG(CASE WHEN meta->>'avg_edge_strength' IS NOT NULL
                           THEN (meta->>'avg_edge_strength')::numeric ELSE NULL END), 3) as avg_edge_strength
        FROM metrics_log
        WHERE node = 'network_aggregator'
    """
    )


def top_rerank_pairs(limit: int = 10) -> list[tuple]:
    """Get top concept pairs by cosine similarity from concept relations."""
    return _q(
        """
        SELECT cr.source_id, cr.target_id,
               ROUND(cr.cosine::numeric, 4) as cosine,
               cr.rerank_score,
               cr.cosine,
               CASE WHEN cr.decided_yes IS TRUE THEN 'decided_yes' ELSE 'auto' END as relation_type,
               'qwen-reranker' as rerank_model
        FROM concept_relations cr
        WHERE cr.rerank_score IS NOT NULL
        ORDER BY cr.cosine DESC
        LIMIT %s
    """,
        limit,
    )


def edge_strength_distribution() -> list[tuple]:
    """Get distribution of edge strengths."""
    return _q(
        """
        SELECT
            CASE
                WHEN cosine >= 0.9 THEN 'strong (≥0.90)'
                WHEN cosine >= 0.75 THEN 'weak (0.75-0.89)'
                ELSE 'filtered (<0.75)'
            END as strength_bucket,
            COUNT(*) as count,
            ROUND(AVG(cosine)::numeric, 3) as avg_strength
        FROM concept_relations
        GROUP BY strength_bucket
        ORDER BY avg_strength DESC
    """
    )


def enrichment_metrics_24h() -> list[tuple]:
    """Get enrichment node performance metrics over the last 24 hours."""
    return _q(
        """
        SELECT DATE_TRUNC('hour', started_at) as hour,
               COUNT(*) as batch_count,
               SUM(CASE WHEN meta->>'batch_size' IS NOT NULL
                        THEN (meta->>'batch_size')::int ELSE 0 END) as total_nouns,
               ROUND(AVG(CASE WHEN meta->>'latency_ms' IS NOT NULL
                              THEN (meta->>'latency_ms')::numeric ELSE NULL END), 1) as avg_batch_latency_ms,
               SUM(CASE WHEN meta->>'success_count' IS NOT NULL
                        THEN (meta->>'success_count')::int ELSE 0 END) as successful_enrichments
        FROM metrics_log
        WHERE node = 'enrichment' AND event = 'batch_processed' AND started_at > NOW() - INTERVAL '24 hours'
        GROUP BY hour
        ORDER BY hour DESC
    """
    )


def enrichment_totals() -> list[tuple]:
    """Get total enrichment statistics."""
    return _q(
        """
        SELECT
            COUNT(*) as total_batches,
            SUM(CASE WHEN meta->>'batch_size' IS NOT NULL
                     THEN (meta->>'batch_size')::int ELSE 0 END) as total_nouns_processed,
            SUM(CASE WHEN meta->>'success_count' IS NOT NULL
                     THEN (meta->>'success_count')::int ELSE 0 END) as total_successful_enrichments,
            ROUND(AVG(CASE WHEN meta->>'latency_ms' IS NOT NULL
                           THEN (meta->>'latency_ms')::numeric ELSE NULL END), 1) as avg_batch_latency_ms,
            ROUND(SUM(CASE WHEN meta->>'latency_ms' IS NOT NULL
                           THEN (meta->>'latency_ms')::numeric ELSE 0 END) / 1000.0, 1) as total_seconds_processing
        FROM metrics_log
        WHERE node = 'enrichment' AND event = 'batch_processed'
    """
    )


def relations_metrics_24h() -> list[tuple]:
    """Get relations building metrics over the last 24 hours."""
    return _q(
        """
        SELECT DATE_TRUNC('hour', started_at) as hour,
               SUM(CASE WHEN meta->>'edges_persisted' IS NOT NULL
                        THEN (meta->>'edges_persisted')::int ELSE 0 END) as edges_persisted,
               SUM(CASE WHEN meta->>'rerank_calls' IS NOT NULL
                        THEN (meta->>'rerank_calls')::int ELSE 0 END) as rerank_calls
        FROM metrics_log
        WHERE node = 'network_aggregator' AND started_at > NOW() - INTERVAL '24 hours'
        GROUP BY hour
        ORDER BY hour DESC
    """
    )


def confidence_gate_tallies_24h() -> list[tuple]:
    """Get confidence gate violation tallies over the last 24 hours."""
    return _q(
        """
        SELECT DATE_TRUNC('hour', started_at) as hour,
               SUM(CASE WHEN event = 'ai_conf_soft_warn' THEN 1 ELSE 0 END) as soft_warnings,
               SUM(CASE WHEN event = 'ai_conf_hard_fail' THEN 1 ELSE 0 END) as hard_failures
        FROM metrics_log
        WHERE event IN ('ai_conf_soft_warn', 'ai_conf_hard_fail')
              AND started_at > NOW() - INTERVAL '24 hours'
        GROUP BY hour
        ORDER BY hour DESC
    """
    )


def pattern_metrics_latest() -> list[tuple]:
    """Get latest pattern discovery metrics."""
    return _q(
        """
        SELECT
            (SELECT COUNT(DISTINCT cluster_id) FROM concept_clusters) as clusters_found,
            (SELECT COUNT(*) FROM concept_clusters GROUP BY cluster_id ORDER BY COUNT(*) DESC LIMIT 1)
            as largest_cluster_size,
            (SELECT COUNT(*) FROM concept_centrality WHERE degree > 0) as nodes_with_centrality,
            (SELECT ROUND(AVG(degree), 3) FROM concept_centrality) as avg_degree_centrality,
            (SELECT concept_id FROM concept_centrality ORDER BY degree DESC LIMIT 1) as top_hub_concept
        FROM (SELECT 1) as dummy
    """
    )
