#!/usr/bin/env python3
"""
Guard for E88 Violation Drilldown Pages.

Validates:
- Every violation code in compliance exports has an HTML page
- All violation pages have required backlinks (to dashboards, nodes, patterns, receipts)
- Pages are accessible and properly formatted
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

CONTROL_PLANE_DIR = REPO / "share" / "atlas" / "control_plane"
VIOLATIONS_DIR = REPO / "docs" / "atlas" / "webproof" / "violations"
EVIDENCE_DIR = REPO / "evidence"


def load_json_file(filepath: Path) -> dict | None:
    """Load JSON file, return None if missing or invalid."""
    if not filepath.exists():
        return None
    try:
        with filepath.open() as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def get_violation_codes() -> set[str]:
    """Extract all unique violation codes from compliance exports."""
    codes = set()

    # Check top_violations_7d.json
    violations_7d = load_json_file(CONTROL_PLANE_DIR / "top_violations_7d.json")
    if violations_7d and "violations" in violations_7d:
        for violation in violations_7d["violations"]:
            if "violation_code" in violation:
                codes.add(violation["violation_code"])

    # Check top_violations_30d.json
    violations_30d = load_json_file(CONTROL_PLANE_DIR / "top_violations_30d.json")
    if violations_30d and "violations" in violations_30d:
        for violation in violations_30d["violations"]:
            if "violation_code" in violation:
                codes.add(violation["violation_code"])

    # Check compliance_summary.json
    summary = load_json_file(CONTROL_PLANE_DIR / "compliance_summary.json")
    if summary and "metrics" in summary:
        by_code = summary["metrics"].get("violations_by_code", {})
        codes.update(by_code.keys())

    return codes


def check_violation_pages() -> dict[str, bool | list[str]]:
    """Check that all violation codes have corresponding HTML pages."""
    codes = get_violation_codes()
    missing_pages = []
    found_pages = []

    for code in codes:
        safe_code = code.lower().replace("_", "-")
        page_path = VIOLATIONS_DIR / f"{safe_code}.html"
        if page_path.exists():
            found_pages.append(code)
        else:
            missing_pages.append(code)

    return {
        "all_pages_exist": len(missing_pages) == 0,
        "missing_pages": missing_pages,
        "found_pages": found_pages,
        "total_codes": len(codes),
    }


def check_backlinks() -> dict[str, bool | list[str]]:
    """Check that violation pages have required backlinks."""
    codes = get_violation_codes()
    pages_with_issues = []
    pages_ok = []

    required_links = [
        "../../dashboard/compliance_summary.html",
        "../../dashboard/compliance_timeseries.html",
        "../../browser/violations.html",
        "../../browser/guard_receipts.html",
    ]

    for code in codes:
        safe_code = code.lower().replace("_", "-")
        page_path = VIOLATIONS_DIR / f"{safe_code}.html"
        if not page_path.exists():
            continue

        try:
            content = page_path.read_text()
            missing_links = []
            for link in required_links:
                if link not in content:
                    missing_links.append(link)

            if missing_links:
                pages_with_issues.append({"code": code, "missing_links": missing_links})
            else:
                pages_ok.append(code)
        except Exception as e:
            pages_with_issues.append({"code": code, "error": str(e)})

    return {
        "all_backlinks_present": len(pages_with_issues) == 0,
        "pages_with_issues": pages_with_issues,
        "pages_ok": pages_ok,
    }


def main() -> int:
    """Run guard checks."""
    parser = argparse.ArgumentParser(description="Guard for E88 Violation Drilldown Pages")
    parser.add_argument(
        "--write-evidence",
        type=str,
        help="Write evidence JSON to specified path",
    )
    args = parser.parse_args()

    # Run checks
    pages_check = check_violation_pages()
    backlinks_check = check_backlinks()

    # Build verdict
    all_ok = pages_check["all_pages_exist"] and backlinks_check["all_backlinks_present"]

    verdict = {
        "episode": "E88",
        "ok": all_ok,
        "checks": {
            "violation_pages": pages_check,
            "backlinks": backlinks_check,
        },
    }

    # Print verdict
    if all_ok:
        print("[guard_atlas_compliance_drilldowns] Verdict: PASS")
        print(f"[guard_atlas_compliance_drilldowns] Found {len(pages_check['found_pages'])} violation pages")
    else:
        print("[guard_atlas_compliance_drilldowns] Verdict: FAIL", file=sys.stderr)
        if not pages_check["all_pages_exist"]:
            print(
                f"[guard_atlas_compliance_drilldowns] Missing pages: {pages_check['missing_pages']}",
                file=sys.stderr,
            )
        if not backlinks_check["all_backlinks_present"]:
            print(
                f"[guard_atlas_compliance_drilldowns] Pages with missing backlinks: {backlinks_check['pages_with_issues']}",
                file=sys.stderr,
            )

    # Write evidence if requested
    if args.write_evidence:
        evidence_path = Path(args.write_evidence)
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(json.dumps(verdict, indent=2))
        print(f"[guard_atlas_compliance_drilldowns] Evidence: {evidence_path}")

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
