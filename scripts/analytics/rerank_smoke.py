#!/usr/bin/env python3
"""Rerank smoke test - verify edge rerank fields"""

import sys
import json
import pathlib

p = pathlib.Path("exports/graph_latest.json")
if not p.exists():
    print("[rerank.smoke] SKIP: no graph_latest.json yet")
    sys.exit(0)

doc = json.load(open(p, encoding="utf-8"))
edges = doc.get("edges", [])

if not edges:
    print("[rerank.smoke] OK: 0 edges (empty DB, expected)")
    sys.exit(0)

# Check for rerank fields when edges exist
sample = edges[0] if edges else {}
has_rerank = "rerank" in sample or "rerank_score" in sample
has_strength = "edge_strength" in sample or "strength" in sample

print(f"[rerank.smoke] edges={len(edges)}, has_rerank={has_rerank}, has_strength={has_strength}")
status = "PASS" if (has_rerank and has_strength) or not edges else "WARN: missing rerank fields"
print(f"[rerank.smoke] {status}")
sys.exit(0 if "PASS" in status else 1)
