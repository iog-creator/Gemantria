#!/usr/bin/env python3
"""
Phase-3B Feature #1: DB-backed graph overview command.

Queries graph_stats table to provide a summary of graph statistics.
Honors DB health modes (db_off/partial/ready) and prints JSON + human summary.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agentpm.db.loader import get_control_engine
from agentpm.db.models_graph_stats import GraphStatsSnapshot
from scripts.guards.guard_db_health import check_db_health


def compute_graph_overview() -> dict:
    """
    Compute graph overview statistics from database.

    Returns:
        Dictionary with overview stats:
        {
            "ok": bool,
            "mode": "db_on" | "db_off" | "partial",
            "stats": {
                "nodes": int | None,
                "edges": int | None,
                "avg_degree": float | None,
                "snapshot_count": int | None,
                "last_import_at": str | None (ISO8601)
            },
            "reason": str | None
        }
    """
    result: dict = {
        "ok": False,
        "mode": "db_off",
        "stats": {
            "nodes": None,
            "edges": None,
            "avg_degree": None,
            "snapshot_count": None,
            "last_import_at": None,
        },
        "reason": None,
    }

    # Check DB health first
    health = check_db_health()

    if not health.get("ok") or health.get("mode") != "ready":
        result["mode"] = health.get("mode", "db_off")
        if health.get("details", {}).get("errors"):
            result["reason"] = health["details"]["errors"][0].split(":")[-1].strip()
        else:
            result["reason"] = f"database not ready (mode: {result['mode']})"
        return result

    # DB is ready, query stats
    try:
        engine = get_control_engine()
        SessionLocal = sessionmaker(bind=engine)

        with SessionLocal() as session:
            # Get latest snapshot (most recent created_at)
            latest_snapshot_query = (
                select(GraphStatsSnapshot.snapshot_id)
                .order_by(GraphStatsSnapshot.created_at.desc())
                .limit(1)
            )
            latest_snapshot_result = session.execute(latest_snapshot_query).scalar_one_or_none()

            if latest_snapshot_result is None:
                # No snapshots in database
                result["ok"] = True
                result["mode"] = "db_on"
                result["reason"] = "no snapshots found"
                return result

            latest_snapshot_id = latest_snapshot_result

            # Get nodes and edges from latest snapshot
            nodes_query = (
                select(GraphStatsSnapshot.metric_value)
                .where(
                    GraphStatsSnapshot.snapshot_id == latest_snapshot_id,
                    GraphStatsSnapshot.metric_name == "nodes",
                )
                .limit(1)
            )
            nodes = session.execute(nodes_query).scalar_one_or_none()

            edges_query = (
                select(GraphStatsSnapshot.metric_value)
                .where(
                    GraphStatsSnapshot.snapshot_id == latest_snapshot_id,
                    GraphStatsSnapshot.metric_name == "edges",
                )
                .limit(1)
            )
            edges = session.execute(edges_query).scalar_one_or_none()

            # Try to get avg_degree from metric, otherwise calculate
            avg_degree_query = (
                select(GraphStatsSnapshot.metric_value)
                .where(
                    GraphStatsSnapshot.snapshot_id == latest_snapshot_id,
                    GraphStatsSnapshot.metric_name == "centrality.avg_degree",
                )
                .limit(1)
            )
            avg_degree = session.execute(avg_degree_query).scalar_one_or_none()

            # Calculate avg_degree if not found and we have nodes/edges
            if avg_degree is None and nodes is not None and edges is not None and nodes > 0:
                avg_degree = (edges * 2.0) / nodes

            # Get snapshot count
            snapshot_count_query = select(func.count(func.distinct(GraphStatsSnapshot.snapshot_id)))
            snapshot_count = session.execute(snapshot_count_query).scalar_one()

            # Get last import timestamp
            last_import_query = select(func.max(GraphStatsSnapshot.created_at))
            last_import_at = session.execute(last_import_query).scalar_one_or_none()

            # Build result
            result["ok"] = True
            result["mode"] = "db_on"
            result["stats"]["nodes"] = int(nodes) if nodes is not None else None
            result["stats"]["edges"] = int(edges) if edges is not None else None
            result["stats"]["avg_degree"] = float(avg_degree) if avg_degree is not None else None
            result["stats"]["snapshot_count"] = int(snapshot_count) if snapshot_count else 0
            result["stats"]["last_import_at"] = (
                last_import_at.isoformat() if last_import_at else None
            )

            return result

    except Exception as e:
        result["mode"] = "db_off"
        result["reason"] = f"query error: {e}"
        return result


def print_human_summary(overview: dict) -> str:
    """
    Generate human-readable summary line from overview JSON.

    Args:
        overview: Dictionary from compute_graph_overview()

    Returns:
        Summary string like "GRAPH_OVERVIEW: nodes=100 edges=200 avg_degree=4.0 snapshots=1"
    """
    mode = overview.get("mode", "unknown")
    ok = overview.get("ok", False)

    if not ok or mode != "db_on":
        reason = overview.get("reason", "unknown error")
        return f"GRAPH_OVERVIEW: mode={mode} ({reason})"

    stats = overview.get("stats", {})
    nodes = stats.get("nodes", 0) or 0
    edges = stats.get("edges", 0) or 0
    avg_degree = stats.get("avg_degree")
    snapshot_count = stats.get("snapshot_count", 0) or 0

    avg_degree_str = f"{avg_degree:.2f}" if avg_degree is not None else "N/A"

    return f"GRAPH_OVERVIEW: nodes={nodes} edges={edges} avg_degree={avg_degree_str} snapshots={snapshot_count}"


def main() -> int:
    """CLI entrypoint for graph overview."""
    overview = compute_graph_overview()

    # Print JSON to stdout
    print(json.dumps(overview, indent=2))

    # Print human-readable summary to stderr (so JSON can be piped)
    summary = print_human_summary(overview)
    print(summary, file=sys.stderr)

    return 0  # Always exit 0 (hermetic, DB-off-safe)


if __name__ == "__main__":
    sys.exit(main())
