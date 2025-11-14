#!/usr/bin/env python3
"""
Print a human-readable summary of DB health JSON output.

Reads JSON from stdin (from guard.db.health) and prints a single summary line.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def print_summary(health_json: dict) -> str:
    """
    Generate a human-readable summary line from DB health JSON.

    Args:
        health_json: Dictionary from guard_db_health.check_db_health()

    Returns:
        Summary string like "DB_HEALTH: mode=ready (all checks passed)"
    """
    mode = health_json.get("mode", "unknown")
    ok = health_json.get("ok", False)
    checks = health_json.get("checks", {})
    errors = health_json.get("details", {}).get("errors", [])

    # Build reason string
    if ok and mode == "ready":
        reason = "all checks passed"
    elif mode == "db_off":
        if not checks.get("driver_available", False):
            reason = "driver not installed"
        elif not checks.get("connection_ok", False):
            reason = "connection failed"
        else:
            reason = "database unavailable"
    elif mode == "partial":
        if not checks.get("graph_stats_ready", False):
            reason = "graph_stats table missing"
        else:
            reason = "partial readiness"
    else:
        if errors:
            # Use first error as reason (truncate if too long)
            reason = errors[0].split(":")[-1].strip()[:50]
        else:
            reason = "unknown status"

    return f"DB_HEALTH: mode={mode} ({reason})"


def main() -> int:
    """Read JSON from stdin and print summary."""
    try:
        data = json.load(sys.stdin)
        summary = print_summary(data)
        print(summary)
        return 0
    except json.JSONDecodeError as e:
        print(f"DB_HEALTH: mode=error (invalid JSON: {e})", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"DB_HEALTH: mode=error ({e})", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
