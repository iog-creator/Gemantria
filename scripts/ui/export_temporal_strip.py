#!/usr/bin/env python3

"""

Build a temporal "strip" (year -> count) from an envelope and write CSV + PNG.

Usage:

  python scripts/ui/export_temporal_strip.py share/exports/envelope.json \

      --outdir ui/out --mode point --min-year -4000 --max-year 2100

Notes:

  - Uses node.year OR node.data.year OR node.data.start_year (fallbacks).

  - If mode=span and start_year/end_year exist, counts each year in the span

    up to a safety cap to avoid huge loops.

"""

from __future__ import annotations

import argparse, json, os, sys

from typing import Any, Dict


def argp() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("envelope", help="Path to envelope.json")
    p.add_argument("--outdir", default="ui/out", help="Output directory")
    p.add_argument(
        "--mode",
        choices=["point", "span"],
        default="point",
        help="point: count a single year; span: count all years in [start,end]",
    )
    p.add_argument("--min-year", type=int, default=-4000)
    p.add_argument("--max-year", type=int, default=2100)
    p.add_argument("--span-cap", type=int, default=5000, help="max years per node when mode=span")
    return p.parse_args()


def extract_years(node: Dict[str, Any]) -> tuple[int, int | None] | None:
    d = node.get("data", {}) if isinstance(node.get("data"), dict) else {}
    # Common keys
    for k in ("year",):
        if isinstance(node.get(k), int):
            return node[k], None
    for k in ("year", "start_year"):
        v = d.get(k)
        if isinstance(v, int):
            end = d.get("end_year")
            return v, (int(end) if isinstance(end, int) else None)
    return None


def clamp(y: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, y))


def main() -> int:
    a = argp()
    if not os.path.exists(a.envelope):
        print(f"[TEMPORAL] SKIP: envelope not found at {a.envelope}", file=sys.stderr)
        return 0
    with open(a.envelope, encoding="utf-8") as f:
        env = json.load(f)
    nodes = env.get("nodes") or []
    if not isinstance(nodes, list):
        raise SystemExit("envelope.nodes must be a list")
    # Build histogram
    hist: Dict[int, int] = {}
    lo, hi = a.min_year, a.max_year
    for n in nodes:
        yrs = extract_years(n)
        if not yrs:
            continue
        start, end = yrs
        if a.mode == "span" and end is not None:
            s = clamp(start, lo, hi)
            e = clamp(end, lo, hi)
            if e < s:
                s, e = e, s
            span_len = e - s + 1
            if span_len > a.span_cap:
                # protect against pathological spans
                e = s + a.span_cap - 1
            for y in range(s, e + 1):
                hist[y] = hist.get(y, 0) + 1
        else:
            y = clamp(int(start), lo, hi)
            hist[y] = hist.get(y, 0) + 1

    if not hist:
        print("[TEMPORAL] NOTE: no usable year data found; writing empty CSV", file=sys.stderr)

    os.makedirs(a.outdir, exist_ok=True)
    csv_path = os.path.join(a.outdir, "temporal_strip.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("year,count\n")
        for y in sorted(hist.keys()):
            f.write(f"{y},{hist[y]}\n")

    # Optional PNG (matplotlib if available)
    png_path = os.path.join(a.outdir, "temporal_strip.png")
    try:
        import matplotlib.pyplot as plt  # matplotlib is in requirements.txt

        years = sorted(hist.keys())
        counts = [hist[y] for y in years]
        plt.figure()
        plt.plot(years, counts)
        plt.xlabel("Year")
        plt.ylabel("Count")
        plt.title("Temporal Strip")
        plt.tight_layout()
        plt.savefig(png_path, dpi=144)
        plt.close()
        print(f"[TEMPORAL] Wrote {csv_path} and {png_path}")
    except Exception as e:
        # Still success if CSV written
        print(f"[TEMPORAL] Wrote {csv_path}; PNG skipped ({e})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
