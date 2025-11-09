#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import pathlib
import time


def main() -> int:
    src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("exports/graph_latest.scored.json")

    if not src.exists():
        # fall back to unscored graph
        src = pathlib.Path("exports/graph_latest.json")

    data = json.loads(src.read_text(encoding="utf-8"))

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    n, m = len(nodes), len(edges)
    max_edges = max(1, n * (n - 1) / 2)
    density = min(1.0, m / max_edges) if n > 1 else 0.0

    out = {
        "schema": "graph-stats.v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "pipeline_version": os.getenv("PIPELINE_VERSION", "dev"),
        "nodes": n,
        "edges": m,
        "clusters": 0,
        "density": round(density, 6),
        "centrality": {"avg_degree": round((2 * m / max(1, n)) / max(1, n), 6), "avg_betweenness": 0.0},
        "metadata": {"source": "file_first", "input": str(src)},
    }
    pathlib.Path("exports").mkdir(parents=True, exist_ok=True)
    pathlib.Path("exports/graph_stats.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"OK: wrote exports/graph_stats.json from {src}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
