#!/usr/bin/env python3
import json
import pathlib
import statistics as st

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVAL = ROOT / "share" / "eval"
G = EVAL / "graph_latest.json"
OUT = EVAL / "calibration_adv.json"


def between_class_variance(vals, t1, t2):
    # 2-threshold Otsu-like: [0,t1)=other, [t1,t2)=weak, [t2,1]=strong
    n = len(vals)
    if n == 0 or not (0.0 <= t1 <= t2 <= 1.0):
        return 0.0
    a = [v for v in vals if v < t1]
    b = [v for v in vals if t1 <= v < t2]
    c = [v for v in vals if v >= t2]
    k = [a, b, c]
    if any(len(x) == 0 for x in k):  # avoid empty class blowups
        return 0.0
    mu = st.fmean(vals)
    w = [len(x) / n for x in k]
    m = [st.fmean(x) for x in k]
    # classic between-class variance
    return sum(wi * (mi - mu) ** 2 for wi, mi in zip(w, m, strict=False))


def grid(vals, step=0.01):
    best = (-1.0, 0.75, 0.90)  # score, weak, strong
    pmin, pmax = (min(vals) if vals else 0.0), (max(vals) if vals else 1.0)
    lo = max(0.0, min(pmin, 0.25))
    hi = min(1.0, max(pmax, 0.95))
    t = lo
    while t <= hi:
        u = t + step
        while u <= hi:
            s = between_class_variance(vals, t, u)
            if s > best[0]:
                best = (s, t, u)
            u += step
        t += step
    return best  # score, weak, strong


def main() -> int:
    if not G.exists():
        print("[calibrate.adv] missing graph")
        return 2
    data = json.loads(G.read_text(encoding="utf-8"))
    cos = []
    rr = []
    strg = []
    for e in data.get("edges", []):
        try:
            cos.append(float(e.get("cosine", 0.0)))
        except:
            cos.append(0.0)
        try:
            rr.append(float(e.get("rerank", 0.0) if e.get("rerank") is not None else 0.0))
        except:
            rr.append(0.0)
        try:
            strg.append(float(e.get("edge_strength", 0.0) or 0.0))
        except:
            strg.append(0.0)

    # Scan blend weight W in [0.00..1.00] and choose thresholds per W
    best = {"score": -1.0}
    for i in range(0, 101, 5):  # step 0.05 for speed/determinism
        W = i / 100.0
        vals = [max(0.0, min(1.0, W * c + (1.0 - W) * r)) for c, r in zip(cos, rr, strict=False)]
        score, wth, sth = grid(vals, step=0.01)
        # tie-break: prefer fewer "other" (larger weak/strong share)
        other = sum(v < wth for v in vals)
        metric = (score, -other)
        if metric > (best["score"], best.get("neg_other", float("-inf"))):
            best = {
                "score": score,
                "weak": round(wth, 4),
                "strong": round(sth, 4),
                "W": round(W, 2),
                "neg_other": -other,
            }

    out = {
        "n_edges": len(strg),
        "suggested": {
            "EDGE_BLEND_WEIGHT": best["W"],
            "EDGE_WEAK_THRESH": best["weak"],
            "EDGE_STRONG_THRESH": best["strong"],
        },
        "diagnostics": {
            "objective": "maximize between-class variance; tie-breaker minimizes OTHER",
            "score": best["score"],
        },
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[calibrate.adv] wrote {OUT.relative_to(ROOT)} W={best['W']} weak≥{best['weak']} strong≥{best['strong']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
