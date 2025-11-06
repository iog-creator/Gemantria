#!/usr/bin/env python3
"""
Graph Drift Guard

Detects significant regressions in graph quality vs. last good run.
Fails closed if current graph has zero nodes/edges when previous had data.

Usage: python scripts/guard_graph_drift.py
"""

import glob
import json
import sys
from pathlib import Path


def main():
    # Current graph stats
    cur_path = "share/exports/graph_latest.json"
    if not Path(cur_path).exists():
        print("GRAPH_DRIFT_OK (no current graph)")
        return

    cur = json.load(open(cur_path))

    # Get stats from current graph
    cur_stats = cur.get("stats", {})
    cur_nodes = cur_stats.get("nodes") or len(cur.get("nodes", []))
    cur_edges = cur_stats.get("edges") or len(cur.get("edges", []))

    # Find previous graph evidence files
    prev_files = sorted(glob.glob("share/evidence/*graph*summary_*.json"))
    if not prev_files:
        print("GRAPH_DRIFT_OK (first run)")
        return

    # Load most recent previous evidence
    prev = json.load(open(prev_files[-1]))
    prev_stats = prev.get("data", {}).get("output_summary", {}).get("stats", {})
    prev_nodes = prev_stats.get("nodes", 0)
    prev_edges = prev_stats.get("edges", 0)

    # Check for drift (zero nodes/edges when previous had data)
    if (prev_nodes > 0 and cur_nodes == 0) or (prev_edges > 0 and cur_edges == 0):
        sys.stderr.write(f"DRIFT: nodes {prev_nodes}->{cur_nodes}, edges {prev_edges}->{cur_edges}\n")
        sys.exit(1)

    print("GRAPH_DRIFT_OK")


if __name__ == "__main__":
    main()
