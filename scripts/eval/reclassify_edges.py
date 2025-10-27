#!/usr/bin/env python3
from __future__ import annotations
import json, os, sys
from pathlib import Path
from typing import Dict, Any
from src.rerank.blender import compute_rerank, blend_strength, classify_strength

GRAPH_PATH = Path(os.getenv("GRAPH_JSON", "share/graph/graph_latest.json"))
COUNTS_OUT = Path("share/eval/edges/edge_class_counts.json")

def _read_json(p: Path) -> Dict[str, Any]:
    if not p.exists():
        print(f"[edges] WARN: graph file not found: {p}", file=sys.stderr)
        return {}
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

def _write_json(p: Path, data: Dict[str, Any]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(p)

def main() -> int:
    data = _read_json(GRAPH_PATH)
    if not data:
        # Nothing to do in CI if graph doesn’t exist
        return 0

    edges = data.get("edges") or data.get("graph", {}).get("edges")
    if edges is None:
        print("[edges] WARN: no edges key found in graph JSON; skipping.", file=sys.stderr)
        return 0

    counts = {"strong": 0, "weak": 0, "other": 0}
    changed = False

    for e in edges:
        # Expect fields: source, target, cosine, rerank?, edge_strength?
        cos = e.get("cosine")
        if cos is None:
            # If cosine missing, skip classification (leave as-is)
            e.setdefault("rerank", None)
            e.setdefault("edge_strength", None)
            continue

        rer = e.get("rerank")
        if rer is None:
            # Try to compute rerank from texts where available; else fallback purely on cosine
            src_txt = e.get("source_text") or ""
            tgt_txt = e.get("target_text") or ""
            rer = compute_rerank(src_txt, tgt_txt, float(cos))
            e["rerank"] = rer
            changed = True

        strength = blend_strength(float(cos), float(rer))
        # clamp to [0,1]
        strength = max(0.0, min(1.0, strength))
        e["edge_strength"] = strength
        cls = classify_strength(strength)
        e["class"] = cls
        counts[cls] += 1

    # Persist counts
    _write_json(COUNTS_OUT, counts)

    # If we changed the graph (filled rerank), write it back
    if changed:
        _write_json(GRAPH_PATH, data)

    print(f"[edges] class_counts: {counts}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
