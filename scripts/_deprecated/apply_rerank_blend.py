# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVAL = ROOT / "share" / "eval"
GRAPH_IN = EVAL / "graph_latest.json"
GRAPH_OUT = EVAL / "graph_latest.json"  # in-place update


def _clip01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def main() -> int:
    if not GRAPH_IN.exists():
        print("[rerank] missing graph:", GRAPH_IN.relative_to(ROOT))
        return 2
    data = json.loads(GRAPH_IN.read_text(encoding="utf-8"))
    changed = 0
    for e in data.get("edges", []):
        cos = e.get("cosine")
        try:
            cos = float(cos)
        except Exception:
            cos = 0.0
        rer = e.get("rerank")
        if rer is None:
            # simple heuristic if actual reranker score missing: reuse cosine
            rer = cos
            e["rerank"] = rer
            changed += 1
        try:
            rer = float(rer)
        except Exception:
            rer = cos
        strength = 0.5 * cos + 0.5 * rer
        strength = _clip01(strength)
        e["edge_strength"] = strength
        e["class"] = "strong" if strength >= 0.90 else "weak" if strength >= 0.75 else "other"
    GRAPH_OUT.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[rerank] updated edges={len(data.get('edges', []))} (filled={changed}) → {GRAPH_OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
