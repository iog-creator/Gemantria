#!/usr/bin/env python3
"""
Phase-3A DB Head CLI — Query database head rows for smoke testing.

Usage:
    python -m scripts.db_head graph --limit 10
    python -m scripts.db_head stats --limit 10
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agentpm.db.loader import (
    DbDriverMissingError,
    DbUnavailableError,
    TableMissingError,
    fetch_graph_head,
    fetch_graph_stats_head,
)


def main() -> int:
    """CLI entrypoint."""
    if len(sys.argv) < 2:
        print(
            json.dumps({"ok": False, "error": "Usage: db_head <graph|stats> [--limit N]"}, indent=2)
        )
        return 1

    kind = sys.argv[1]
    limit = 10

    # Parse --limit if present
    if "--limit" in sys.argv:
        idx = sys.argv.index("--limit")
        if idx + 1 < len(sys.argv):
            try:
                limit = int(sys.argv[idx + 1])
            except ValueError:
                print(json.dumps({"ok": False, "error": "Invalid limit value"}, indent=2))
                return 1

    try:
        if kind == "graph":
            rows = fetch_graph_head(limit=limit)
            result = {"ok": True, "kind": "graph", "rows": rows}
        elif kind == "stats":
            rows = fetch_graph_stats_head(limit=limit)
            result = {"ok": True, "kind": "stats", "rows": rows}
        else:
            result = {"ok": False, "error": f"Unknown kind: {kind} (expected 'graph' or 'stats')"}
            return 1

        print(json.dumps(result, indent=2, default=str))
        return 0

    except DbDriverMissingError as e:
        result = {
            "ok": False,
            "kind": kind,
            "mode": "db_off",
            "error": "database driver not installed",
        }
        print(json.dumps(result, indent=2))
        return 1

    except DbUnavailableError as e:
        result = {
            "ok": False,
            "kind": kind,
            "mode": "db_off",
            "error": str(e),
        }
        print(json.dumps(result, indent=2))
        return 1

    except TableMissingError as e:
        result = {
            "ok": False,
            "kind": kind,
            "mode": "table_missing",
            "error": str(e),
        }
        print(json.dumps(result, indent=2))
        return 1

    except Exception as e:
        result = {
            "ok": False,
            "kind": kind,
            "error": f"Unexpected error: {e}",
        }
        print(json.dumps(result, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
