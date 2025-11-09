#!/usr/bin/env python3
# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

from __future__ import annotations

import json
import os
import sys
import math
import pathlib
import time

IN = pathlib.Path("ui/public/xrefs/xrefs_index.v1.json")
OUT_DIR = pathlib.Path("share/eval/badges")
OUT_DIR.mkdir(parents=True, exist_ok=True)
METRICS = pathlib.Path("share/eval/xrefs_metrics.json")


def shield(label: str, value: str) -> str:
    # minimal static SVG shield (no external calls; hermetic)
    # width estimates: 6px per char; pad boxes
    l_w = max(70, 6 * len(label) + 14)
    v_w = max(70, 6 * len(value) + 14)
    w = l_w + v_w
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="20" role="img" aria-label="{label}: {value}">
  <linearGradient id="s" x2="0" y2="100%"><stop offset="0" stop-color="#fff" stop-opacity=".7"/><stop offset=".1" stop-opacity=".1"/><stop offset=".9" stop-opacity=".3"/></linearGradient>
  <mask id="m"><rect width="{w}" height="20" rx="3" fill="#fff"/></mask>
  <g mask="url(#m)">
    <rect width="{l_w}" height="20" fill="#555"/>
    <rect x="{l_w}" width="{v_w}" height="20" fill="#007ec6"/>
    <rect width="{w}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva" font-size="11">
    <text x="{l_w / 2}" y="15">{label}</text>
    <text x="{l_w + v_w / 2}" y="15">{value}</text>
  </g>
</svg>'''


def main() -> int:
    if not IN.exists():
        print(
            "HINT: xrefs_badges: input not found; expected ui/public/xrefs/xrefs_index.v1.json",
            file=sys.stderr,
        )
        return 0
    data = json.loads(IN.read_text())
    # Expect shape: {"schema": "...", "nodes":[...], "edges":[...]}  (nodes carry xref counts)
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    total_nouns = len(nodes)
    # Handle both xref_count field and xrefs array
    nouns_with_xrefs = sum(1 for n in nodes if n.get("xref_count", 0) > 0 or len(n.get("xrefs", [])) > 0)
    total_xrefs = sum(n.get("xref_count", 0) or len(n.get("xrefs", [])) for n in nodes)
    # Coverage: % nouns that have >=1 xref; Rate: xrefs per noun (2 decimals)
    coverage = 0 if total_nouns == 0 else (100.0 * nouns_with_xrefs / total_nouns)
    rate = 0 if total_nouns == 0 else (total_xrefs / total_nouns)
    # Write badges
    (OUT_DIR / "xrefs_coverage.svg").write_text(shield("xref coverage", f"{coverage:.1f}%"))
    (OUT_DIR / "xrefs_rate.svg").write_text(shield("xref rate", f"{rate:.2f}/noun"))
    # Metrics JSON
    METRICS.parent.mkdir(parents=True, exist_ok=True)
    METRICS.write_text(
        json.dumps(
            {
                "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "total_nouns": total_nouns,
                "nouns_with_xrefs": nouns_with_xrefs,
                "total_xrefs": total_xrefs,
                "coverage_pct": round(coverage, 3),
                "xrefs_per_noun": round(rate, 4),
                "source": "fallback_fast_lane",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    print("OK: xref badges written to share/eval/badges/, metrics at share/eval/xrefs_metrics.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
