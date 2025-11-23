#!/usr/bin/env python3
"""
Control-plane Autopilot summary export for Phase D.

Exports aggregated metrics from control.agent_run for tool='autopilot' or 'pmagent'.
Uses centralized DSN loader (never os.getenv directly).
Tolerates empty/nonexistent DB (exits 0, writes JSON with ok=false for CI tolerance).
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.config.env import get_rw_dsn

try:
    import psycopg
except ImportError:
    print(
        "WARN: psycopg not available; skipping autopilot summary export (CI empty-DB tolerance).",
        file=sys.stderr,
    )
    # Write empty export for CI tolerance
    output_dir = REPO / "share" / "atlas" / "control_plane"
    output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC).isoformat()
    payload = {
        "schema": "autopilot_summary_v1",
        "generated_at": now,
        "ok": False,
        "connection_ok": False,
        "error": "psycopg not available",
        "stats": {},
        "window_days": 7,
    }
    (output_dir / "autopilot_summary.json").write_text(json.dumps(payload, indent=2))
    sys.exit(0)

DSN = get_rw_dsn()
if not DSN:
    print("SKIP: GEMATRIA_DSN not set (empty-DB tolerance).", file=sys.stderr)
    # Write empty export for CI tolerance
    output_dir = REPO / "share" / "atlas" / "control_plane"
    output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC).isoformat()
    payload = {
        "schema": "autopilot_summary_v1",
        "generated_at": now,
        "ok": False,
        "connection_ok": False,
        "error": "DSN not set",
        "stats": {},
        "window_days": 7,
    }
    (output_dir / "autopilot_summary.json").write_text(json.dumps(payload, indent=2))
    sys.exit(0)


def export_autopilot_summary(cur, window_days: int = 7) -> dict:
    """Export autopilot summary statistics from control.agent_run."""
    cutoff = datetime.now(UTC) - timedelta(days=window_days)
    # Query agent_run and determine status from violations_json (empty = success, non-empty = error)
    cur.execute(
        """
        SELECT 
            tool,
            CASE 
                WHEN violations_json = '[]'::jsonb OR violations_json IS NULL THEN 'success'
                ELSE 'error'
            END AS status,
            count(*)
        FROM control.agent_run
        WHERE created_at >= %s
          AND (tool = 'autopilot' OR tool = 'pmagent')
        GROUP BY tool, status
    """,
        (cutoff,),
    )

    stats: dict[str, dict[str, int]] = {}
    for tool, status, count in cur.fetchall():
        if tool not in stats:
            stats[tool] = {"total": 0, "success": 0, "error": 0}
        stats[tool]["total"] += count
        if status == "success":
            stats[tool]["success"] += count
        elif status == "error":
            stats[tool]["error"] += count

    return {"stats": stats, "window_days": window_days}


def main() -> None:
    """Main export function."""
    output_dir = REPO / "share" / "atlas" / "control_plane"
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        with psycopg.connect(DSN) as conn, conn.cursor() as cur:
            data = export_autopilot_summary(cur)
            payload = {
                "schema": "autopilot_summary_v1",
                "generated_at": datetime.now(UTC).isoformat(),
                "ok": True,
                "connection_ok": True,
                **data,
            }
            output_file = output_dir / "autopilot_summary.json"
            output_file.write_text(json.dumps(payload, indent=2))
            print(f"Wrote {output_file}")
    except Exception as e:
        payload = {
            "schema": "autopilot_summary_v1",
            "generated_at": datetime.now(UTC).isoformat(),
            "ok": False,
            "connection_ok": False,
            "error": str(e),
            "stats": {},
            "window_days": 7,
        }
        output_file = output_dir / "autopilot_summary.json"
        output_file.write_text(json.dumps(payload, indent=2))
        print(f"Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
