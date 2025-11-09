#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import time

CAND = ["exports/graph_latest.scored.json", "exports/graph_latest.json"]
OUT = pathlib.Path("share/eval/patterns.json")


def load_graph():
    for p in CAND:
        fp = pathlib.Path(p)
        if fp.exists():
            return json.loads(fp.read_text(encoding="utf-8")), str(fp)
    return {"nodes": [], "edges": []}, "missing"


def main() -> int:
    g, src = load_graph()
    edges = g.get("edges", [])
    # Top-K by rerank_score/score with a small floor to avoid noise

    def score(e):
        s = e.get("rerank_score", e.get("score", 0.0))
        try:
            return float(s)
        except Exception:
            return 0.0

    ranked = sorted(edges, key=score, reverse=True)
    top = []
    for e in ranked[:50]:
        top.append(
            {
                "source": e.get("source"),
                "target": e.get("target"),
                "score": score(e),
            }
        )
    out = {
        "schema": "patterns.v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": {"mode": "file_first", "input": src},
        "top_pairs": top,
        "counts": {"edges": len(edges), "top": len(top)},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[analytics.patterns.file] wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
