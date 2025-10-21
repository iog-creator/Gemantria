from __future__ import annotations
import os
from typing import List, Tuple, Dict, Any
import psycopg

DSN = os.getenv("GEMATRIA_DSN")

def _q(sql: str, *params) -> list[tuple]:
    if not DSN:
        raise RuntimeError("GEMATRIA_DSN is not set")
    with psycopg.connect(DSN) as conn, conn.cursor() as cur:
        cur.execute(sql, params or None)
        return cur.fetchall()

def node_latency_7d() -> List[Tuple]:
    return _q("SELECT node, calls, avg_ms, p50_ms, p90_ms, p95_ms, p99_ms FROM v_node_latency_7d ORDER BY node")

def pipeline_runs(limit: int = 50) -> List[Tuple]:
    return _q("SELECT run_id, started_at, finished_at, duration_ms FROM v_pipeline_runs ORDER BY started_at DESC LIMIT %s", limit)

def recent_errors_7d() -> List[Tuple]:
    return _q("SELECT node, error_count, last_seen, error_types FROM v_recent_errors_7d ORDER BY error_count DESC, last_seen DESC")

def node_throughput_24h(node: str | None = None) -> List[Tuple]:
    if node:
        return _q("SELECT minute, items_out FROM v_node_throughput_24h WHERE node=%s ORDER BY minute DESC", node)
    return _q("SELECT node, minute, items_out FROM v_node_throughput_24h ORDER BY minute DESC")

def embedding_requests_24h() -> List[Tuple]:
    """Get embedding request counts over the last 24 hours."""
    return _q("""
        SELECT DATE_TRUNC('hour', started_at) as hour,
               COUNT(*) as requests,
               SUM(CASE WHEN meta->>'embeddings_generated' IS NOT NULL
                        THEN (meta->>'embeddings_generated')::int ELSE 0 END) as total_embeddings
        FROM metrics_log
        WHERE node = 'network_aggregator' AND started_at > NOW() - INTERVAL '24 hours'
        GROUP BY hour
        ORDER BY hour DESC
    """)

def rerank_metrics_24h() -> List[Tuple]:
    """Get rerank performance metrics over the last 24 hours."""
    return _q("""
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
    """)

def qwen_usage_totals() -> List[Tuple]:
    """Get total Qwen model usage statistics."""
    return _q("""
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
    """)

def top_rerank_pairs(limit: int = 10) -> List[Tuple]:
    """Get top concept pairs by edge strength from rerank results."""
    return _q("""
        SELECT cr.source_id, cr.target_id,
               ROUND(cr.edge_strength, 4) as edge_strength,
               ROUND(cr.cosine, 4) as cosine,
               ROUND(cr.rerank_score, 4) as rerank_score,
               cr.relation_type,
               cr.rerank_model
        FROM concept_relations cr
        WHERE cr.edge_strength IS NOT NULL
        ORDER BY cr.edge_strength DESC
        LIMIT %s
    """, limit)

def edge_strength_distribution() -> List[Tuple]:
    """Get distribution of edge strengths."""
    return _q("""
        SELECT
            CASE
                WHEN edge_strength >= 0.9 THEN 'strong (≥0.90)'
                WHEN edge_strength >= 0.75 THEN 'weak (0.75-0.89)'
                ELSE 'filtered (<0.75)'
            END as strength_bucket,
            COUNT(*) as count,
            ROUND(AVG(edge_strength), 3) as avg_strength
        FROM concept_relations
        WHERE edge_strength IS NOT NULL
        GROUP BY strength_bucket
        ORDER BY avg_strength DESC
    """)
