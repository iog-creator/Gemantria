#!/usr/bin/env python3
"""Normalize JSON exports with canonical field mappings."""

import json
import sys
from pathlib import Path

src = Path("exports/graph_latest.json")

if not src.exists():
    print("ERROR: exports/graph_latest.json not found", file=sys.stderr)
    sys.exit(1)

data = json.loads(src.read_text())

nodes = data.get("nodes") or data.get("concepts") or []
edges = data.get("edges") or data.get("relations") or []


def norm_edge(e):
    m = {}
    # map source/destination variants
    m["src_concept_id"] = e.get("source") or e.get("src") or e.get("from") or e.get("src_concept_id")
    m["dst_concept_id"] = e.get("target") or e.get("dst") or e.get("to") or e.get("dst_concept_id")

    # classification/type
    m["relation_type"] = (e.get("relation_type") or e.get("type") or "semantic").lower()

    # weights
    m["weight"] = float(e.get("weight") or e.get("strength") or e.get("edge_strength") or 0)
    m["cosine"] = float(e.get("cosine") or e.get("similarity") or 0)
    m["rerank_score"] = float(e.get("rerank_score") or e.get("rerank") or 0)

    # class
    c = (e.get("class") or e.get("classification") or "").lower()
    if not c:
        s = m["weight"]
        c = "strong" if s >= 0.90 else "weak" if s >= 0.75 else "very_weak"
    m["class"] = c
    return m


norm_nodes = []
for n in nodes:
    norm_nodes.append(
        {
            "concept_id": n.get("id") or n.get("concept_id"),
            "lemma": n.get("lemma") or n.get("label") or n.get("name"),
            "surface": n.get("surface"),
            "book": n.get("book") or "Genesis",
            "metadata": n.get("metadata") or {},
        }
    )

norm_edges = [norm_edge(e) for e in edges]

out = {"concepts": norm_nodes, "relations": norm_edges}
path = Path("exports/graph_latest.normalized.json")
path.write_text(json.dumps(out, ensure_ascii=False, indent=2))
print("NORMALIZED_EXPORT_WRITTEN", path)
