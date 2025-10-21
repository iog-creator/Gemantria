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
