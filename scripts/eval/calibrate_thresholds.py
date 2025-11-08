# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
import json
import pathlib
import statistics as st

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVAL = ROOT / "share" / "eval"
GRAPH = EVAL / "graph_latest.json"
OUT = EVAL / "calibration_suggest.json"


def percentile(vals, p):
    if not vals:
        return 0.0
    vals = sorted(vals)
    k = (len(vals) - 1) * p
    f = int(k)
    c = min(f + 1, len(vals) - 1)
    d = k - f
    return vals[f] * (1 - d) + vals[c] * d


def main() -> int:
    if not GRAPH.exists():
        print("[calibrate] missing graph")
        return 2
    data = json.loads(GRAPH.read_text(encoding="utf-8"))
    strengths = [float(e.get("edge_strength", 0.0) or 0.0) for e in data.get("edges", [])]
    sugg = {
        "n_edges": len(strengths),
        "mean": st.fmean(strengths) if strengths else 0.0,
        "p50": percentile(strengths, 0.50),
        "p75": percentile(strengths, 0.75),
        "p90": percentile(strengths, 0.90),
        "suggested": {
            "EDGE_WEAK_THRESH": round(percentile(strengths, 0.75), 4),
            "EDGE_STRONG_THRESH": round(percentile(strengths, 0.90), 4),
            "EDGE_BLEND_WEIGHT": 0.5,
        },
    }
    OUT.write_text(json.dumps(sugg, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[calibrate] wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
