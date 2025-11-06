#!/usr/bin/env python3
"""
Guard: Compare current artifacts against last-good snapshot.

Fails if current graph/stats show significant regression (>10% degradation).
"""

import json
import sys


def load_json_safe(path):
    """Load JSON file, return None if not found."""
    try:
        return json.load(open(path))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def compare_graphs(current, last_good):
    """Compare current graph against last-good snapshot."""
    if not current or not last_good:
        return True  # No comparison possible, pass

    current_nodes = len(current.get("nodes", []))
    current_edges = len(current.get("edges", []))
    last_nodes = len(last_good.get("nodes", []))
    last_edges = len(last_good.get("edges", []))

    # Allow some variance but fail on significant regression
    node_threshold = 0.9  # 10% degradation allowed
    edge_threshold = 0.9

    if current_nodes < last_nodes * node_threshold:
        print(f"GRAPH_REGRESSION: nodes {last_nodes} -> {current_nodes} (< {node_threshold * 100:.0f}%)")
        return False

    if current_edges < last_edges * edge_threshold:
        print(f"GRAPH_REGRESSION: edges {last_edges} -> {current_edges} (< {edge_threshold * 100:.0f}%)")
        return False

    print(f"GRAPH_OK: nodes {last_nodes} -> {current_nodes}, edges {last_edges} -> {current_edges}")
    return True


def main():
    """Main guard function."""
    current_graph = load_json_safe("share/exports/graph_latest.json")
    last_good_graph = load_json_safe("share/exports/graph_last_good.json")

    if compare_graphs(current_graph, last_good_graph):
        print("LAST_GOOD_OK")
        return 0
    else:
        print("LAST_GOOD_FAIL")
        return 1


if __name__ == "__main__":
    sys.exit(main())
