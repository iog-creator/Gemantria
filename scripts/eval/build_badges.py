#!/usr/bin/env python3
import json
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_EVAL = ROOT / "share" / "eval"
EVAL_OUTDIR = os.environ.get("EVAL_OUTDIR")
EVAL = (ROOT / EVAL_OUTDIR) if EVAL_OUTDIR else DEFAULT_EVAL
DEFAULT_BADGES = EVAL / "badges"
BADGES_OUTDIR = os.environ.get("BADGES_OUTDIR")
BADGES = (ROOT / BADGES_OUTDIR) if BADGES_OUTDIR else DEFAULT_BADGES
REPORT_JSON = EVAL / "report.json"


def main():
    print("[eval.badges] starting")

    BADGES.mkdir(parents=True, exist_ok=True)

    # Load report data
    if not REPORT_JSON.exists():
        print(f"[eval.badges] FAIL no report.json at {REPORT_JSON}")
        return 1

    try:
        report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[eval.badges] FAIL could not parse report: {e}")
        return 1

    # Extract badge values from report
    summary = report.get("summary", {})
    ok_count = summary.get("ok_count", 0)
    fail_count = summary.get("fail_count", 0)
    total = ok_count + fail_count

    # Create quality badge based on pass rate
    if total == 0:
        color = "lightgrey"
        status = "unknown"
    elif ok_count == total:
        color = "brightgreen"
        status = "passing"
    elif ok_count >= total * 0.8:
        color = "yellow"
        status = "warning"
    else:
        color = "red"
        status = "failing"

    # Create coverage badge
    coverage = summary.get("coverage_percent", 0)
    if coverage >= 98:
        cov_color = "brightgreen"
        cov_status = "excellent"
    elif coverage >= 95:
        cov_color = "yellow"
        cov_status = "good"
    elif coverage >= 90:
        cov_color = "orange"
        cov_status = "adequate"
    else:
        cov_color = "red"
        cov_status = "poor"

    # Write badges as JSON for consumption
    badges_data = {
        "quality": {
            "label": "quality",
            "message": f"{status} ({ok_count}/{total})",
            "color": color
        },
        "coverage": {
            "label": "coverage",
            "message": f"{cov_status} ({coverage:.1f}%)",
            "color": cov_color
        }
    }

    badges_json = BADGES / "badges.json"
    badges_json.write_text(json.dumps(badges_data, indent=2), encoding="utf-8")

    # Create markdown badges for README
    badges_md = BADGES / "badges.md"
    md_content = f"""<!-- Quality Badges -->
![Quality](https://img.shields.io/badge/quality-{status}-{color})
![Coverage](https://img.shields.io/badge/coverage-{cov_status}-{cov_color})
"""
    badges_md.write_text(md_content, encoding="utf-8")

    print(f"[eval.badges] wrote {badges_json.relative_to(ROOT)}")
    print(f"[eval.badges] wrote {badges_md.relative_to(ROOT)}")
    print("[eval.badges] done")


if __name__ == "__main__":
    exit(main() or 0)
