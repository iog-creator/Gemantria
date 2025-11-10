# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Atlas telemetry queries - read-only, empty-DB tolerant (Rule 046)

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

# Add repo root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

try:
    import psycopg

    HAS_DB = True
except ImportError:
    HAS_DB = False

from src.infra.env_loader import ensure_env_loaded
from scripts.config.env import get_rw_dsn, get_bible_db_dsn

ensure_env_loaded()

DSN = get_rw_dsn()
ATLAS_WINDOW = os.getenv("ATLAS_WINDOW", "24h")
ATLAS_MAX_ROWS = int(os.getenv("ATLAS_MAX_ROWS", "500"))


def _hint(msg: str) -> None:
    """Emit HINT to stderr (hermetic behavior per Rule 046)."""
    print(f"HINT: atlas: {msg}", file=sys.stderr)


def _q(sql: str, *params: Any) -> list[tuple]:
    """
    Execute read-only query with empty-DB tolerance.
    Returns [] if DSN missing or connection fails (never errors).
    """
    if not DSN:
        _hint("GEMATRIA_DSN not set; returning empty results")
        return []
    if not HAS_DB:
        _hint("psycopg not available; returning empty results")
        return []
    try:
        with psycopg.connect(DSN, connect_timeout=2) as conn:
            # Force read-only transaction
            with conn.cursor() as cur:
                cur.execute("SET default_transaction_read_only=on")
                cur.execute(sql, params or None)
                return cur.fetchall()
    except (psycopg.OperationalError, psycopg.Error) as e:
        _hint(f"database query failed: {e}; returning empty results")
        return []


def q_active_runs() -> list[tuple]:
    """Get currently executing pipeline runs."""
    return _q(
        """
        SELECT DISTINCT run_id, MIN(started_at) as started_at
        FROM metrics_log
        WHERE finished_at IS NULL
        GROUP BY run_id
        ORDER BY started_at DESC
        LIMIT %s
        """,
        ATLAS_MAX_ROWS,
    )


def q_errors(window: str | None = None) -> list[tuple]:
    """Get recent errors from v_recent_errors_7d."""
    window_sql = window or ATLAS_WINDOW
    # Map window to interval
    if window_sql == "24h":
        interval = "24 hours"
    elif window_sql == "7d":
        interval = "7 days"
    else:
        interval = "24 hours"
    return _q(
        f"""
        SELECT node, error_count, last_seen, error_types
        FROM v_recent_errors_7d
        WHERE last_seen >= NOW() - INTERVAL '{interval}'
        ORDER BY error_count DESC, last_seen DESC
        LIMIT %s
        """,
        ATLAS_MAX_ROWS,
    )


def q_latency_p90() -> list[tuple]:
    """Get top slowest nodes by p90 latency from v_node_latency_7d."""
    return _q(
        """
        SELECT node, calls, avg_ms, p50_ms, p90_ms, p95_ms, p99_ms
        FROM v_node_latency_7d
        ORDER BY p90_ms DESC NULLS LAST
        LIMIT 5
        """
    )


def q_throughput(window: str | None = None) -> list[tuple]:
    """Get throughput metrics from v_node_throughput_24h."""
    window_sql = window or ATLAS_WINDOW
    if window_sql == "24h":
        interval = "24 hours"
    elif window_sql == "7d":
        interval = "7 days"
    else:
        interval = "24 hours"
    return _q(
        f"""
        SELECT node, minute, items_out
        FROM v_node_throughput_24h
        WHERE minute >= NOW() - INTERVAL '{interval}'
        ORDER BY minute DESC, node
        LIMIT %s
        """,
        ATLAS_MAX_ROWS,
    )


def q_ai_interactions(run_id: str | None = None) -> list[tuple]:
    """Get AI tool usage from ai_interactions table."""
    if run_id:
        return _q(
            """
            SELECT interaction_id, run_id, tool_name, model_name, started_at, finished_at,
                   EXTRACT(EPOCH FROM (finished_at - started_at)) * 1000.0 as duration_ms
            FROM ai_interactions
            WHERE run_id = %s
            ORDER BY started_at DESC
            LIMIT %s
            """,
            run_id,
            ATLAS_MAX_ROWS,
        )
    return _q(
        """
        SELECT interaction_id, run_id, tool_name, model_name, started_at, finished_at,
               EXTRACT(EPOCH FROM (finished_at - started_at)) * 1000.0 as duration_ms
        FROM ai_interactions
        ORDER BY started_at DESC
        LIMIT %s
        """,
        ATLAS_MAX_ROWS,
    )


def q_governance_artifacts(artifact_type: str | None = None) -> list[tuple]:
    """Get governance artifacts from governance_artifacts table."""
    if artifact_type:
        return _q(
            """
            SELECT artifact_id, artifact_type, artifact_name, file_path, updated_at
            FROM governance_artifacts
            WHERE artifact_type = %s
            ORDER BY updated_at DESC
            LIMIT %s
            """,
            artifact_type,
            ATLAS_MAX_ROWS,
        )
    return _q(
        """
        SELECT artifact_id, artifact_type, artifact_name, file_path, updated_at
        FROM governance_artifacts
        ORDER BY updated_at DESC
        LIMIT %s
        """,
        ATLAS_MAX_ROWS,
    )


def q_pipeline_runs(limit: int | None = None) -> list[tuple]:
    """Get pipeline runs from v_pipeline_runs."""
    limit_val = limit or ATLAS_MAX_ROWS
    return _q(
        """
        SELECT run_id, started_at, finished_at, duration_ms
        FROM v_pipeline_runs
        ORDER BY started_at DESC
        LIMIT %s
        """,
        limit_val,
    )


def q_node_sequence(run_id: str) -> list[tuple]:
    """Get ordered node execution sequence for a run."""
    return _q(
        """
        SELECT node, event, started_at, finished_at,
               EXTRACT(EPOCH FROM (finished_at - started_at)) * 1000.0 as duration_ms,
               items_in, items_out, status
        FROM v_metrics_flat
        WHERE run_id = %s
        ORDER BY started_at ASC
        LIMIT %s
        """,
        run_id,
        ATLAS_MAX_ROWS,
    )


def q_checkpoint_progression(run_id: str) -> list[tuple]:
    """Get checkpoint state progression for a run."""
    return _q(
        """
        SELECT checkpoint_id, thread_id, checkpoint_ns, checkpoint_id_seq, created_at
        FROM checkpointer_state
        WHERE thread_id = %s
        ORDER BY created_at ASC
        LIMIT %s
        """,
        run_id,
        ATLAS_MAX_ROWS,
    )
