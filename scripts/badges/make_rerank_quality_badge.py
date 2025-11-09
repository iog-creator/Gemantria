#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

BADGE_PATH = pathlib.Path("share/eval/badges/rerank_quality.svg")
BLEND_JSON = pathlib.Path("share/eval/rerank_blend_report.json")


def ensure_blend() -> dict:
    if not BLEND_JSON.exists():
        subprocess.run([sys.executable, "scripts/analytics/rerank_blend_report.py"], check=False)
    if BLEND_JSON.exists():
        return json.loads(BLEND_JSON.read_text(encoding="utf-8"))
    return {}


def shield_svg(label: str, value: str, ok: bool) -> str:
    # Minimal local shield (no external deps). Widths are simple estimates.
    l_w = max(70, 8 * len(label) + 20)
    v_w = max(66, 8 * len(value) + 18)
    total = l_w + v_w
    color = "#2ea043" if ok else "#d97706"  # green vs amber

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{total}" height="20" role="img" aria-label="{label}: {value}">
  <linearGradient id="s" x2="0" y2="100%"><stop offset="0" stop-color="#fff" stop-opacity=".7"/><stop offset=".1" stop-opacity=".1"/><stop offset=".9" stop-opacity=".3"/><stop offset="1" stop-opacity=".5"/></linearGradient>
  <mask id="m"><rect width="{total}" height="20" rx="3" fill="#fff"/></mask>
  <g mask="url(#m)">
    <rect width="{l_w}" height="20" fill="#555"/>
    <rect x="{l_w}" width="{v_w}" height="20" fill="{color}"/>
    <rect width="{total}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="{l_w / 2:.1f}" y="15" fill="#010101" fill-opacity=".3">{label}</text>
    <text x="{l_w / 2:.1f}" y="14">{label}</text>
    <text x="{l_w + v_w / 2:.1f}" y="15" fill="#010101" fill-opacity=".3">{value}</text>
    <text x="{l_w + v_w / 2:.1f}" y="14">{value}</text>
  </g>
</svg>'''


def main() -> int:
    data = ensure_blend()

    total_edges = data.get("total_edges", 0)
    ok_strict = data.get("ok", {}).get("strict", 0)
    below_strict = data.get("below", {}).get("strict", 0)

    # Calculate quality: percentage meeting strict threshold
    if total_edges > 0:
        pct = (ok_strict / total_edges) * 100
        value = f"{pct:.0f}%"
        ok = below_strict == 0  # All edges meet strict threshold
    else:
        value = "no-data"
        ok = True  # Empty is valid

    label = "rerank quality"

    BADGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    BADGE_PATH.write_text(shield_svg(label, value, ok), encoding="utf-8")
    print(f"[badge] wrote {BADGE_PATH} (ok={ok}, value={value}, total={total_edges})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
