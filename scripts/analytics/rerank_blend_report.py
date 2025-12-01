#!/usr/bin/env python3
# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

from __future__ import annotations

import json
import os
import pathlib
import time


def main() -> int:
    # Centralized thresholds with env overrides (PDF guidance → SSOT)
    cfg = {}
    try:
        cfg = json.loads(pathlib.Path("configs/rerank_blend.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        cfg = {"hint": 0.80, "strict": 0.90}

    hint_thr = float(os.getenv("RERANK_THRESHOLD_HINT", cfg.get("hint", 0.80)))
    strict_thr = float(os.getenv("RERANK_THRESHOLD_STRICT", cfg.get("strict", 0.90)))

    # Load graph if available
    gpath = pathlib.Path("exports/graph_latest.json")
    if not gpath.exists():
        gpath = pathlib.Path("exports/graph_latest.scored.json")

    source_mode = "file_first"
    if not gpath.exists():
        source_mode = "missing"
        edges = []
    else:
        data = json.loads(gpath.read_text(encoding="utf-8"))
        edges = data.get("edges", [])

    # Classify edges by thresholds
    below_hint = []
    below_strict = []
    ok_hint = []
    ok_strict = []

    for e in edges:
        strength = e.get("edge_strength") or e.get("strength", 0.0)
        try:
            strength_val = float(strength)
        except (ValueError, TypeError):
            strength_val = 0.0

        if strength_val < hint_thr:
            below_hint.append(
                {"source": e.get("source"), "target": e.get("target"), "strength": strength_val}
            )
        else:
            ok_hint.append(
                {"source": e.get("source"), "target": e.get("target"), "strength": strength_val}
            )

        if strength_val < strict_thr:
            below_strict.append(
                {"source": e.get("source"), "target": e.get("target"), "strength": strength_val}
            )
        else:
            ok_strict.append(
                {"source": e.get("source"), "target": e.get("target"), "strength": strength_val}
            )

    out = {
        "schema": "rerank-blend.v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": {"mode": source_mode, "input": str(gpath) if gpath.exists() else None},
        "thresholds": {"hint": hint_thr, "strict": strict_thr},
        "below": {"hint": len(below_hint), "strict": len(below_strict)},
        "ok": {"hint": len(ok_hint), "strict": len(ok_strict)},
        "total_edges": len(edges),
    }

    pathlib.Path("share/eval").mkdir(parents=True, exist_ok=True)
    pathlib.Path("share/eval/rerank_blend_report.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
