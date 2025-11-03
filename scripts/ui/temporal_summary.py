#!/usr/bin/env python3

"""

Read ui/out/temporal_strip.csv and write a concise Markdown summary to ui/out/temporal_summary.md.

Safe if the CSV is missing (prints SKIP and exits 0).

"""

from __future__ import annotations

import csv, os, sys, statistics as stats

from pathlib import Path


IN_CSV = os.environ.get("TEMPORAL_CSV", "ui/out/temporal_strip.csv")

OUT_MD = os.environ.get("TEMPORAL_MD", "ui/out/temporal_summary.md")

TOP_N = int(os.environ.get("TEMPORAL_TOP", "10"))


def load_rows(path: str):
    p = Path(path)
    if not p.exists():
        print(f"[TEMPORAL] SKIP: CSV not found at {p}", file=sys.stderr)
        return []
    rows = []
    with p.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                y = int(row["year"])
                c = int(row["count"])
            except Exception:
                continue
            rows.append((y, c))
    return rows


def main() -> int:
    rows = load_rows(IN_CSV)
    if not rows:
        # Write empty summary to keep downstream simple
        Path(OUT_MD).write_text("# Temporal Summary\n\n_No data found._\n", encoding="utf-8")
        print(f"[TEMPORAL] Wrote empty summary to {OUT_MD}", file=sys.stderr)
        return 0

    rows.sort(key=lambda t: t[0])
    years = [y for y, _ in rows]
    counts = [c for _, c in rows]
    total = sum(counts)
    min_year, max_year = years[0], years[-1]
    nonzero = [(y, c) for y, c in rows if c > 0]
    nz_years = [y for y, _ in nonzero]
    nz_counts = [c for _, c in nonzero] or [0]
    span = (min_year, max_year)
    mean = stats.fmean(nz_counts)
    median = stats.median(nz_counts)
    peak_y, peak_c = max(nonzero, key=lambda t: t[1]) if nonzero else (None, 0)
    top = sorted(nonzero, key=lambda t: t[1], reverse=True)[:TOP_N]

    # Build Markdown
    lines = []
    lines.append("# Temporal Summary")
    lines.append("")
    lines.append(f"- **Years:** {span[0]} — {span[1]}")
    lines.append(f"- **Active years (nonzero):** {len(nz_years)} / {len(years)}")
    lines.append(f"- **Total count:** {total}")
    lines.append(f"- **Peak:** {peak_y} ({peak_c})" if peak_y is not None else "- **Peak:** n/a")
    lines.append(f"- **Mean/Median (nonzero):** {mean:.2f} / {median}")
    lines.append("")
    lines.append("## Top years")
    lines.append("")
    lines.append("| year | count |")
    lines.append("|-----:|------:|")
    for y, c in top:
        lines.append(f"| {y} | {c} |")
    lines.append("")

    Path(OUT_MD).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[TEMPORAL] Wrote {OUT_MD}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
