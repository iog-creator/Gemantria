#!/usr/bin/env python3
"""OPS report utility - analytics check stub"""

import sys
import json
from pathlib import Path


def check_analytics() -> int:
    """Verify analytics export is present and readable"""
    graph_path = Path("exports/graph_latest.json")

    if not graph_path.exists():
        print("[ops_report --check-analytics] FAIL: exports/graph_latest.json missing", file=sys.stderr)
        return 1

    try:
        doc = json.loads(graph_path.read_text(encoding="utf-8"))
        nodes = doc.get("nodes", [])
        edges = doc.get("edges", [])
        schema = doc.get("schema", "")
        ts = doc.get("generated_at", "")

        print(f"[ops_report --check-analytics] OK: {len(nodes)} nodes, {len(edges)} edges")
        print(f"  schema: {schema}")
        print(f"  generated_at: {ts}")
        return 0
    except Exception as e:
        print(f"[ops_report --check-analytics] FAIL: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    if "--check-analytics" in sys.argv:
        sys.exit(check_analytics())
    else:
        print("Usage: ops_report.py --check-analytics")
        sys.exit(0)
