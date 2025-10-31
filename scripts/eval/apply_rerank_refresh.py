#!/usr/bin/env python3
import json
import pathlib
import sys

from rerank_provider import rerank

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVAL = ROOT / "share" / "eval"
GRAPH = EVAL / "graph_latest.json"


def _clip01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def main() -> int:
    if not GRAPH.exists():
        print("[rerank.refresh] missing graph:", GRAPH.relative_to(ROOT))
        return 2
    data = json.loads(GRAPH.read_text(encoding="utf-8"))
    edges = data.get("edges", [])
    filled = 0
    for e in edges:
        cos = e.get("cosine") or 0.0
        try:
            cos = float(cos)
        except Exception:
            cos = 0.0
        # Expect minimal fields; tolerate missing text
        a = e.get("src_text") or e.get("a_text") or ""
        b = e.get("dst_text") or e.get("b_text") or ""
        if not e.get("rerank"):
            e["rerank"] = rerank(a, b)
            filled += 1
        try:
            rr = float(e["rerank"])
        except Exception:
            rr = 0.5
        strength = _clip01(0.5 * cos + 0.5 * rr)
        e["edge_strength"] = strength
        e["class"] = (
            "strong" if strength >= 0.90 else "weak" if strength >= 0.75 else "other"
        )
    GRAPH.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    path_str = GRAPH.relative_to(ROOT)
    print(
        f"[rerank.refresh] updated edges={len(edges)} (filled_from_provider={filled}) → {path_str}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
