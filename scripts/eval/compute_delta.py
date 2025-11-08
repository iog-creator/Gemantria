# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
import json
import pathlib
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVAL = ROOT / "share" / "eval"
CUR = EVAL / "graph_latest.json"
PREV = EVAL / "graph_prev.json"
DELTAJ = EVAL / "delta.json"
BADGES = EVAL / "badges"
BADGES.mkdir(parents=True, exist_ok=True)
BADGE = BADGES / "edges_delta.svg"


def _counts(edges: list[dict]) -> tuple[int, int, int]:
    s = w = o = 0
    for e in edges:
        c = e.get("class")
        if c == "strong":
            s += 1
        elif c == "weak":
            w += 1
        else:
            o += 1
    return s, w, o


def _badge_svg(ds: int, dw: int) -> str:
    # simple shield style
    txt = f"Δ strong:{ds:+d} | Δ weak:{dw:+d}"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="220" height="20" role="img" aria-label="{txt}">
  <linearGradient id="g" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <rect rx="3" width="220" height="20" fill="#555"/>
  <rect rx="3" x="70" width="150" height="20" fill="#4c1"/>
  <path fill="#4c1" d="M70 0h4v20h-4z"/>
  <rect rx="3" width="220" height="20" fill="url(#g)"/>
  <g fill="#fff" text-anchor="start" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="6" y="14">graph delta</text>
    <text x="76" y="14">{txt}</text>
  </g>
</svg>"""


def main() -> int:
    if not CUR.exists():
        print("[delta] missing", CUR)
        return 2
    cur = json.loads(CUR.read_text(encoding="utf-8"))
    prev = json.loads(PREV.read_text(encoding="utf-8")) if PREV.exists() else {"edges": []}
    cs, cw, _ = _counts(cur.get("edges", []))
    ps, pw, _ = _counts(prev.get("edges", []))
    ds, dw = cs - ps, cw - pw
    out = {
        "generated_at": int(time.time()),
        "prev_present": PREV.exists(),
        "counts": {
            "current": {"strong": cs, "weak": cw},
            "previous": {"strong": ps, "weak": pw},
            "delta": {"strong": ds, "weak": dw},
        },
    }
    DELTAJ.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    BADGE.write_text(_badge_svg(ds, dw), encoding="utf-8")
    print(f"[delta] wrote {DELTAJ.relative_to(ROOT)} and badge {BADGE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
