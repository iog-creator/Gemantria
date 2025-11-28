#!/usr/bin/env python3
"""
Control-plane graph compliance metrics export for E90.

Exports compliance metrics aggregated by:
- Tool (from agent_run.tool)
- Node (extracted from agent_run.args_json/result_json if available)
- Pattern/Cluster (extracted if available)
- Extraction batch (extracted if available)

Uses centralized DSN loader (never os.getenv directly).
Tolerates empty/nonexistent DB (exits 0, writes JSON with ok=false for CI tolerance).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, UTC, timedelta
from pathlib import Path

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.config.env import get_rw_dsn

try:
    import psycopg
except ImportError:
    print(
        "WARN: psycopg not available; skipping graph compliance export (CI empty-DB tolerance).",
        file=sys.stderr,
    )
    # Write empty export for CI tolerance
    output_dir = REPO / "share" / "atlas" / "control_plane"
    output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC).isoformat()
    payload = {
        "schema": "graph_compliance_v1",
        "generated_at": now,
        "ok": False,
        "connection_ok": False,
        "error": "psycopg not available",
        "metrics": {
            "by_tool": {},
            "by_node": {},
            "by_pattern": {},
            "by_batch": {},
        },
    }
    (output_dir / "graph_compliance.json").write_text(json.dumps(payload, indent=2))
    sys.exit(0)

DSN = get_rw_dsn()
if not DSN:
    print("SKIP: GEMATRIA_DSN not set (empty-DB tolerance).", file=sys.stderr)
    # Write empty export for CI tolerance
    output_dir = REPO / "share" / "atlas" / "control_plane"
    output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC).isoformat()
    payload = {
        "schema": "graph_compliance_v1",
        "generated_at": now,
        "ok": False,
        "connection_ok": False,
        "error": "DSN not set",
        "metrics": {
            "by_tool": {},
            "by_node": {},
            "by_pattern": {},
            "by_batch": {},
        },
    }
    (output_dir / "graph_compliance.json").write_text(json.dumps(payload, indent=2))
    sys.exit(0)


def extract_node_id(data: dict) -> str | None:
    """Extract node_id from args_json or result_json if available."""
    if isinstance(data, dict):
        # Check common field names
        for key in ["node_id", "nodeId", "node", "concept_id", "conceptId"]:
            if key in data:
                value = data[key]
                if isinstance(value, str):
                    return value
        # Check nested structures
        if "args" in data:
            return extract_node_id(data["args"])
        if "result" in data:
            return extract_node_id(data["result"])
    return None


def extract_pattern_id(data: dict) -> str | None:
    """Extract pattern/cluster ID from args_json or result_json if available."""
    if isinstance(data, dict):
        for key in ["pattern_id", "patternId", "cluster_id", "clusterId", "pattern", "cluster"]:
            if key in data:
                value = data[key]
                if isinstance(value, (str, int)):
                    return str(value)
        if "args" in data:
            return extract_pattern_id(data["args"])
        if "result" in data:
            return extract_pattern_id(data["result"])
    return None


def extract_batch_id(data: dict) -> str | None:
    """Extract batch ID from args_json or result_json if available."""
    if isinstance(data, dict):
        for key in ["batch_id", "batchId", "batch", "extraction_batch", "extractionBatch"]:
            if key in data:
                value = data[key]
                if isinstance(value, (str, int)):
                    return str(value)
        if "args" in data:
            return extract_batch_id(data["args"])
        if "result" in data:
            return extract_batch_id(data["result"])
    return None


def export_graph_compliance_metrics(cur: psycopg.Cursor, window_days: int = 30) -> dict:
    """Export compliance metrics aggregated by tool, node, pattern, and batch."""
    try:
        cutoff = datetime.now(UTC) - timedelta(days=window_days)

        # Query agent_run with violations
        cur.execute(
            """
            SELECT tool, args_json, result_json, violations_json, created_at
            FROM control.agent_run
            WHERE created_at >= %s
              AND violations_json != '[]'::jsonb
            ORDER BY created_at DESC
            """,
            (cutoff,),
        )

        rows = cur.fetchall()

        # Aggregate metrics
        by_tool: dict[str, dict[str, int]] = {}
        by_node: dict[str, dict[str, int]] = {}
        by_pattern: dict[str, dict[str, int]] = {}
        by_batch: dict[str, dict[str, int]] = {}

        for row in rows:
            tool = row[0]
            args_json = row[1] or {}
            result_json = row[2] or {}
            violations_json = row[3] or []
            created_at = row[4]

            if not violations_json:
                continue

            # Extract violation codes
            violation_codes = []
            for violation in violations_json:
                if isinstance(violation, dict) and "code" in violation:
                    violation_codes.append(violation["code"])

            if not violation_codes:
                continue

            # Aggregate by tool
            if tool not in by_tool:
                by_tool[tool] = {}
            for code in violation_codes:
                by_tool[tool][code] = by_tool[tool].get(code, 0) + 1

            # Try to extract node_id
            node_id = extract_node_id(args_json) or extract_node_id(result_json)
            if node_id:
                if node_id not in by_node:
                    by_node[node_id] = {}
                for code in violation_codes:
                    by_node[node_id][code] = by_node[node_id].get(code, 0) + 1

            # Try to extract pattern_id
            pattern_id = extract_pattern_id(args_json) or extract_pattern_id(result_json)
            if pattern_id:
                if pattern_id not in by_pattern:
                    by_pattern[pattern_id] = {}
                for code in violation_codes:
                    by_pattern[pattern_id][code] = by_pattern[pattern_id].get(code, 0) + 1

            # Try to extract batch_id
            batch_id = extract_batch_id(args_json) or extract_batch_id(result_json)
            if batch_id:
                if batch_id not in by_batch:
                    by_batch[batch_id] = {}
                for code in violation_codes:
                    by_batch[batch_id][code] = by_batch[batch_id].get(code, 0) + 1

        return {
            "metrics": {
                "by_tool": by_tool,
                "by_node": by_node,
                "by_pattern": by_pattern,
                "by_batch": by_batch,
            },
            "window_days": window_days,
            "total_runs_with_violations": len(rows),
        }
    except Exception as e:
        return {
            "metrics": {
                "by_tool": {},
                "by_node": {},
                "by_pattern": {},
                "by_batch": {},
            },
            "error": str(e),
        }


def main() -> int:
    """Generate graph compliance metrics export."""
    parser = argparse.ArgumentParser(description="Export graph compliance metrics")
    parser.add_argument(
        "--window-days",
        type=int,
        default=30,
        help="Time window in days (default: 30)",
    )
    args = parser.parse_args()

    output_dir = REPO / "share" / "atlas" / "control_plane"
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        with psycopg.connect(DSN) as conn, conn.cursor() as cur:
            metrics = export_graph_compliance_metrics(cur, args.window_days)

            payload = {
                "schema": "graph_compliance_v1",
                "generated_at": datetime.now(UTC).isoformat(),
                "ok": True,
                "connection_ok": True,
                **metrics,
            }

            output_file = output_dir / "graph_compliance.json"
            output_file.write_text(json.dumps(payload, indent=2))
            print(f"[control_graph_compliance_metrics_export] Wrote {output_file}")
            return 0
    except Exception as e:
        # Write error payload
        payload = {
            "schema": "graph_compliance_v1",
            "generated_at": datetime.now(UTC).isoformat(),
            "ok": False,
            "connection_ok": False,
            "error": str(e),
            "metrics": {
                "by_tool": {},
                "by_node": {},
                "by_pattern": {},
                "by_batch": {},
            },
        }
        output_file = output_dir / "graph_compliance.json"
        output_file.write_text(json.dumps(payload, indent=2))
        print(f"[control_graph_compliance_metrics_export] ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
