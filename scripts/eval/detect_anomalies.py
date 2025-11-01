#!/usr/bin/env python3
import json
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVAL = ROOT / "share" / "eval"
G = EVAL / "graph_latest.json"
OUTJ = EVAL / "anomalies.json"
BADG_DIR = EVAL / "badges"
BADG_DIR.mkdir(parents=True, exist_ok=True)
BADG = BADG_DIR / "anomalies.svg"


def _f(name, d):
    try:
        return float(os.environ.get(name, d))
    except Exception:
        return float(d)


def _badge(n):
    color = "#4c1" if n == 0 else "#e05d44"
    txt = f"anomalies:{n}"
    w = 130
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="20" role="img" aria-label="{txt}">
  <linearGradient id="g" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <rect rx="3" width="{w}" height="20" fill="#555"/>
  <rect rx="3" x="75" width="{w - 75}" height="20" fill="{color}"/>
  <path fill="{color}" d="M75 0h4v20h-4z"/><rect rx="3" width="{w}" height="20" fill="url(#g)"/>
  <g fill="#fff" text-anchor="start" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="6" y="14">anomalies</text>
    <text x="81" y="14">{n}</text>
  </g>
</svg>"""


def main() -> int:
    if not G.exists():
        print("[anoms] missing graph")
        return 2
    data = json.loads(G.read_text(encoding="utf-8"))
    edges = data.get("edges", [])
    # thresholds (MANDATORY env knobs, with defaults)
    COS_RR_GAP = _f("ANOM_COS_RERANK_GAP", 0.40)  # |cos - rerank| >= gap
    LOW_STRONG = _f("ANOM_LOW_STRONG", 0.85)  # edge_strength >= strong_thresh but class not strong (suspect)
    HI_OTHER = _f("ANOM_HI_OTHER", 0.70)  # edge_strength >= this but class==other (suspect)

    anoms = []
    for e in edges:
        try:
            cos = float(e.get("cosine", 0.0) or 0.0)
            rr = float(e.get("rerank", 0.0) or 0.0)
            st = float(e.get("edge_strength", 0.0) or 0.0)
        except Exception:
            cos, rr, st = 0.0, 0.0, 0.0
        cls = e.get("class")
        flags = []
        if abs(cos - rr) >= COS_RR_GAP:
            flags.append("cos_vs_rerank_gap")
        if st >= LOW_STRONG and cls != "strong":
            flags.append("strong_misclass")
        if st >= HI_OTHER and cls == "other":
            flags.append("other_too_high")
        if flags:
            anoms.append(
                {
                    "src": e.get("src"),
                    "dst": e.get("dst"),
                    "cosine": cos,
                    "rerank": rr,
                    "edge_strength": st,
                    "class": cls,
                    "flags": flags,
                }
            )

    OUTJ.write_text(json.dumps({"count": len(anoms), "items": anoms}, indent=2, sort_keys=True), encoding="utf-8")  # noqa: E501
    BADG.write_text(_badge(len(anoms)), encoding="utf-8")
    print(f"[anoms] count={len(anoms)} wrote {OUTJ.relative_to(ROOT)} and {BADG.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
