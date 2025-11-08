# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
Reclassify edges according to env-configurable thresholds.

Env:
EDGE_STRONG (default 0.90)
EDGE_WEAK   (default 0.75)

Input:
share/eval/edges/edge_inputs.json  (or derive from exports/graph_stats.json)

Output:
share/eval/edges/edge_class_counts.json
"""

from __future__ import annotations
import json, os, sys
from pathlib import Path
from typing import Dict, Any


def _load_json(p: Path) -> Any:
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def _dump_json(p: Path, data: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(p)


def _to_float(name: str, default: float) -> float:
    v = os.getenv(name, "").strip()
    if not v:
        return default
    try:
        x = float(v)
    except ValueError:
        print(f"[HINT] {name}='{v}' invalid; using default {default}", file=sys.stderr)
        return default
    if not (0.0 <= x <= 1.0):
        print(f"[HINT] {name}={x} out of [0,1]; using default {default}", file=sys.stderr)
        return default
    return x


def main() -> int:
    strong = _to_float("EDGE_STRONG", 0.90)
    weak = _to_float("EDGE_WEAK", 0.75)
    if weak > strong:
        print(
            f"[HINT] EDGE_WEAK ({weak}) > EDGE_STRONG ({strong}); swapping.",
            file=sys.stderr,
        )
        strong, weak = weak, strong

    # Prefer a precomputed inputs file; otherwise derive from graph export.
    inputs_path = Path("share/eval/edges/edge_inputs.json")
    if inputs_path.exists():
        edges = _load_json(inputs_path)
    else:
        graph_path = Path("exports/graph_latest.json")
        if graph_path.exists():
            graph = _load_json(graph_path)
            edges = graph.get("edges", [])
        else:
            edges = []

    counts = {"strong": 0, "weak": 0, "other": 0}
    for e in edges:
        # SSOT edge_strength first; legacy strength; then cosine/similarity
        s = e.get("edge_strength")
        if s is None:
            s = e.get("strength")
        if s is None:
            s = e.get("cosine") or e.get("similarity") or 0.0

        if s >= strong:
            counts["strong"] += 1
        elif s >= weak:
            counts["weak"] += 1
        else:
            counts["other"] += 1

    outp = Path("share/eval/edges/edge_class_counts.json")
    _dump_json(outp, {"thresholds": {"strong": strong, "weak": weak}, "counts": counts})
    print(f"[OK] wrote {outp} with thresholds strong={strong}, weak={weak}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
