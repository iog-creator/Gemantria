#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

BLEND = pathlib.Path("share/eval/rerank_blend_report.json")
PATTERNS = pathlib.Path("share/eval/patterns.json")
OUT = pathlib.Path("share/eval/badges/patterns_badge.svg")


def ensure_patterns() -> dict:
    if not PATTERNS.exists():
        subprocess.run([sys.executable, "scripts/analytics/export_patterns_from_json.py"], check=False)
    return json.loads(PATTERNS.read_text(encoding="utf-8")) if PATTERNS.exists() else {}


def shield_svg(label: str, value: str) -> str:
    l_w = max(84, 8 * len(label) + 20)
    v_w = max(64, 8 * len(value) + 18)
    total = l_w + v_w
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total}" height="20" role="img" aria-label="{label}: {value}">
  <linearGradient id="s" x2="0" y2="100%"><stop offset="0" stop-color="#fff" stop-opacity=".7"/><stop offset=".1" stop-opacity=".1"/><stop offset=".9" stop-opacity=".3"/><stop offset="1" stop-opacity=".5"/></linearGradient>
  <mask id="m"><rect width="{total}" height="20" rx="3" fill="#fff"/></mask>
  <g mask="url(#m)">
    <rect width="{l_w}" height="20" fill="#555"/>
    <rect x="{l_w}" width="{v_w}" height="20" fill="#0366d6"/>
    <rect width="{total}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="{l_w / 2:.1f}" y="15" fill="#010101" fill-opacity=".3">patterns top</text>
    <text x="{l_w / 2:.1f}" y="14">patterns top</text>
    <text x="{l_w + v_w / 2:.1f}" y="15" fill="#010101" fill-opacity=".3">{value}</text>
    <text x="{l_w + v_w / 2:.1f}" y="14">{value}</text>
  </g>
</svg>"""


def main() -> int:
    data = ensure_patterns()
    top = data.get("top_pairs") or []
    top_score = top[0]["score"] if top else None
    value = f"{float(top_score):.2f}" if isinstance(top_score, (int, float)) else "no-data"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(shield_svg("patterns top", value), encoding="utf-8")
    print(f"[badge] wrote {OUT} (top={value})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
