#!/usr/bin/env python3
import json
import pathlib
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVAL = ROOT / "share" / "eval"
BADGES = EVAL / "badges"
BADGES.mkdir(parents=True, exist_ok=True)
HIST = EVAL / "quality_history.jsonl"
SVG = BADGES / "quality_trend.svg"


def parse_quality() -> dict:
    rpt = (
        (EVAL / "quality_report.txt").read_text(encoding="utf-8")
        if (EVAL / "quality_report.txt").exists()
        else ""
    )
    failed = "FAIL:" in rpt
    stats = {"edges": 0, "strong": 0, "weak": 0, "other": 0}
    for line in rpt.splitlines():
        if line.startswith("edges="):
            # edges=26 strong=0 weak=0 other=26
            parts = line.split()
            for p in parts:
                if p.startswith("edges="):
                    stats["edges"] = int(p.split("=")[1])
                if p.startswith("strong="):
                    stats["strong"] = int(p.split("=")[1])
                if p.startswith("weak="):
                    stats["weak"] = int(p.split("=")[1])
                if p.startswith("other="):
                    stats["other"] = int(p.split("=")[1])
    return {"ts": int(time.time()), "pass": (not failed), **stats}


def sparkline(vals, w=120, h=20, pad=2):
    if not vals:
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"/>'
    mn, mx = min(vals), max(vals)
    rng = (mx - mn) or 1.0
    xs = [pad + i * (w - 2 * pad) / max(1, len(vals) - 1) for i in range(len(vals))]
    ys = [h - pad - (v - mn) * (h - 2 * pad) / rng for v in vals]
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys, strict=False))
    color = "#4c1" if vals and vals[-1] else "#e05d44"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">
  <polyline fill="none" stroke="{color}" stroke-width="2" points="{pts}"/>
</svg>"""


def main() -> int:
    rec = parse_quality()
    with HIST.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    # trend = last 30 pass/fail as 1/0
    last = []
    try:
        lines = HIST.read_text(encoding="utf-8").splitlines()[-30:]
        for ln in lines:
            d = json.loads(ln) if ln.strip() else {}
            last.append(1 if d.get("pass") else 0)
    except Exception:
        pass
    SVG.write_text(sparkline(last), encoding="utf-8")
    print(
        f"[quality.trend] appended history ({len(last)} pts), wrote {SVG.relative_to(ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
