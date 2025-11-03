#!/usr/bin/env python3

"""

Headless acceptance check for UI envelope outputs.

Validates basic schema and enforces minimal counts.

Usage:

  python scripts/acceptance/check_envelope.py share/exports/envelope.json \

      --min-nodes 1 --min-edges 0 [--allow-empty]

Environment override (optional):

  MIN_NODES, MIN_EDGES, ALLOW_EMPTY=1

"""

from __future__ import annotations

import argparse, json, os, sys

from typing import Any, Dict


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("path", help="Path to envelope.json (export output)")
    p.add_argument("--min-nodes", type=int, default=int(os.getenv("MIN_NODES", "1")))
    p.add_argument("--min-edges", type=int, default=int(os.getenv("MIN_EDGES", "0")))
    p.add_argument("--allow-empty", action="store_true", default=os.getenv("ALLOW_EMPTY") == "1")
    return p.parse_args()


def soft_schema_check(envelope: Dict[str, Any]) -> None:
    # Require top-level lists
    if not isinstance(envelope.get("nodes"), list):
        raise ValueError("envelope.nodes must be a list")
    if not isinstance(envelope.get("edges"), list):
        raise ValueError("envelope.edges must be a list")
    # Minimal per-item keys (React Flow-friendly)
    for i, n in enumerate(envelope["nodes"][:10]):
        if not isinstance(n, dict) or "id" not in n:
            raise ValueError(f"node[{i}] missing 'id'")
    for i, e in enumerate(envelope["edges"][:10]):
        if not isinstance(e, dict) or not {"source", "target"}.issubset(e.keys()):
            raise ValueError(f"edge[{i}] missing 'source'/'target'")


def main() -> int:
    a = parse_args()
    if not os.path.exists(a.path):
        print(f"[ACCEPT] SKIP: envelope not found at {a.path}", file=sys.stderr)
        return 0
    with open(a.path, encoding="utf-8") as f:
        env = json.load(f)
    soft_schema_check(env)
    nodes, edges = env.get("nodes", []), env.get("edges", [])
    n_nodes, n_edges = len(nodes), len(edges)
    if a.allow_empty and n_nodes == 0:
        print(f"[ACCEPT] OK (empty allowed): nodes={n_nodes} edges={n_edges}")
        return 0
    if n_nodes < a.min_nodes:
        raise SystemExit(f"[ACCEPT] FAIL: nodes {n_nodes} < min {a.min_nodes}")
    if n_edges < a.min_edges:
        raise SystemExit(f"[ACCEPT] FAIL: edges {n_edges} < min {a.min_edges}")
    print(f"[ACCEPT] OK: nodes={n_nodes} edges={n_edges} (min_nodes={a.min_nodes} min_edges={a.min_edges})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
