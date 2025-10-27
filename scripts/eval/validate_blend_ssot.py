#!/usr/bin/env python3
from __future__ import annotations
import json, os, sys
from pathlib import Path
from typing import Any, Dict, List

def _load_json(p: Path) -> Any:
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

def _dump_json(p: Path, data: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(p)

def _get_float(name: str, default: float) -> float:
    v = os.getenv(name, "").strip()
    if not v:
        return default
    try:
        x = float(v)
        return x
    except ValueError:
        print(f"[HINT] {name}='{v}' invalid; using default {default}", file=sys.stderr)
        return default

def main() -> int:
    # SSOT defaults
    alpha = _get_float("EDGE_ALPHA", 0.5)
    tol   = _get_float("BLEND_TOL", 0.005)

    gpath = Path("exports/graph_latest.json")
    if not gpath.exists():
        # Hermetic non-fatal behavior: still emit report with HINT
        print("[HINT] exports/graph_latest.json not found; skipping blend validation.", file=sys.stderr)
        out = {
            "alpha": alpha, "tolerance": tol,
            "checked_edges": 0, "blend_mismatch": 0, "missing_fields": 0,
            "examples": {"blend_mismatch": [], "missing_fields": []}
        }
        _dump_json(Path("share/eval/edges/blend_ssot_report.json"), out)
        _dump_json(Path("share/eval/edges/blend_ssot_report.md"),
                   {"note": "No graph export present; validation skipped (non-fatal)."})
        return 0

    graph = _load_json(gpath)
    edges = graph.get("edges", [])
    checked = 0
    mism = 0
    miss = 0
    ex_mism: List[Dict[str, Any]] = []
    ex_miss: List[Dict[str, Any]] = []

    for e in edges:
        cos = e.get("cosine")
        rrs = e.get("rerank_score")
        es  = e.get("edge_strength")
        if cos is None or rrs is None or es is None:
            miss += 1
            if len(ex_miss) < 10:
                ex_miss.append({"source": e.get("source"), "target": e.get("target")})
            continue
        checked += 1
        expected = alpha * float(cos) + (1.0 - alpha) * float(rrs)
        diff = abs(expected - float(es))
        if diff > tol:
            mism += 1
            if len(ex_mism) < 10:
                ex_mism.append({
                    "source": e.get("source"), "target": e.get("target"),
                    "cosine": cos, "rerank_score": rrs, "edge_strength": es,
                    "expected": round(expected, 6), "diff": round(diff, 6)
                })

    out = {
        "alpha": alpha, "tolerance": tol,
        "checked_edges": checked,
        "blend_mismatch": mism,
        "missing_fields": miss,
        "examples": {"blend_mismatch": ex_mism, "missing_fields": ex_miss}
    }
    _dump_json(Path("share/eval/edges/blend_ssot_report.json"), out)

    # Also emit a tiny MD summary for quick review
    md = [
        "# Blend SSOT Validation",
        f"- alpha: {alpha}",
        f"- tolerance: ±{tol}",
        f"- checked_edges: {checked}",
        f"- blend_mismatch: {mism}",
        f"- missing_fields: {miss}",
    ]
    _dump_json(Path("share/eval/edges/blend_ssot_report.md"), {"lines": md})

    if miss > 0:
        print(f"[HINT] blend_ssot: {miss} edges missing fields (cosine/rerank_score/edge_strength)", file=sys.stderr)
    if mism > 0:
        print(f"[HINT] blend_ssot: {mism} edges differ from SSOT blend beyond ±{tol}", file=sys.stderr)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
