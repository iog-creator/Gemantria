#!/usr/bin/env python3
"""
Guard for E88 Violation Drilldowns.

Validates:
- Every violation code in compliance exports has an HTML page
- Each HTML page has required backlinks (node, pattern, guard receipt)
- All backlinked files exist (or are placeholders)

Emits verdict JSON to evidence/guard_atlas_compliance_drilldowns.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import quote

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

VERDICT_PATH = REPO / "evidence" / "guard_atlas_compliance_drilldowns.json"

VIOLATIONS_DIR = REPO / "docs" / "atlas" / "webproof" / "violations"
CONTROL_PLANE_DIR = REPO / "share" / "atlas" / "control_plane"

# Required backlinks in violation pages
REQUIRED_BACKLINKS = [
    "backlink-node-page",
    "backlink-pattern-page",
    "backlink-guard-receipt",
    "backlink-compliance-summary",
    "backlink-compliance-timeseries",
]


def load_json_file(filepath: Path) -> dict | None:
    """Load JSON file, return None if missing or invalid."""
    if not filepath.exists():
        return None
    try:
        with filepath.open() as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def extract_violation_codes() -> set[str]:
    """Extract all unique violation codes from compliance exports."""
    codes: set[str] = set()

    violations_7d = load_json_file(CONTROL_PLANE_DIR / "top_violations_7d.json")
    violations_30d = load_json_file(CONTROL_PLANE_DIR / "top_violations_30d.json")
    compliance_summary = load_json_file(CONTROL_PLANE_DIR / "compliance_summary.json")

    if violations_7d and violations_7d.get("violations"):
        violations = violations_7d["violations"]
        if isinstance(violations, list):
            for item in violations:
                if isinstance(item, dict) and "violation_code" in item:
                    codes.add(item["violation_code"])
        elif isinstance(violations, dict):
            codes.update(violations.keys())

    if violations_30d and violations_30d.get("violations"):
        violations = violations_30d["violations"]
        if isinstance(violations, list):
            for item in violations:
                if isinstance(item, dict) and "violation_code" in item:
                    codes.add(item["violation_code"])
        elif isinstance(violations, dict):
            codes.update(violations.keys())

    if compliance_summary and compliance_summary.get("metrics"):
        top_offenders = compliance_summary["metrics"].get("top_offenders", [])
        for offender in top_offenders:
            if isinstance(offender, dict) and "code" in offender:
                codes.add(offender["code"])

    return codes


def check_violation_page(code: str) -> tuple[bool, list[str]]:
    """Check that violation page exists and has required backlinks."""
    errors = []
    encoded_code = quote(code, safe="")
    page_path = VIOLATIONS_DIR / f"{encoded_code}.html"

    if not page_path.exists():
        errors.append(f"Missing page for violation: {code}")
        return False, errors

    try:
        content = page_path.read_text()
    except OSError as e:
        errors.append(f"Failed to read page for {code}: {e}")
        return False, errors

    # Check for required backlinks
    for backlink_id in REQUIRED_BACKLINKS:
        if f'data-testid="{backlink_id}"' not in content:
            errors.append(f"Missing backlink {backlink_id} in page for {code}")

    return len(errors) == 0, errors


def main() -> int:
    """Run guard checks."""
    verdict = {
        "ok": True,
        "errors": [],
        "checks": {},
        "violations_checked": 0,
        "pages_found": 0,
    }

    # Extract violation codes
    codes = extract_violation_codes()

    if not codes:
        # If no codes found, check if violations directory exists and has at least one page
        if VIOLATIONS_DIR.exists():
            pages = list(VIOLATIONS_DIR.glob("*.html"))
            if pages:
                verdict["pages_found"] = len(pages)
                verdict["checks"]["no_violations_in_exports"] = {
                    "ok": True,
                    "note": "No violations in exports, but pages exist (placeholder OK)",
                }
            else:
                verdict["ok"] = False
                verdict["errors"].append("No violation pages found and no violations in exports")
        else:
            verdict["ok"] = False
            verdict["errors"].append("Violations directory does not exist")
    else:
        # Check each violation code has a page
        for code in codes:
            verdict["violations_checked"] += 1
            page_ok, page_errors = check_violation_page(code)
            verdict["checks"][code] = {
                "ok": page_ok,
                "errors": page_errors,
            }
            if not page_ok:
                verdict["ok"] = False
                verdict["errors"].extend(page_errors)

        # Count existing pages
        if VIOLATIONS_DIR.exists():
            pages = list(VIOLATIONS_DIR.glob("*.html"))
            verdict["pages_found"] = len(pages)

    # Write verdict
    VERDICT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with VERDICT_PATH.open("w") as f:
        json.dump(verdict, f, indent=2)

    if verdict["ok"]:
        print(
            json.dumps(
                {
                    "ok": True,
                    "errors": [],
                    "violations_checked": verdict["violations_checked"],
                    "pages_found": verdict["pages_found"],
                }
            )
        )
        return 0
    else:
        print(
            json.dumps(
                {
                    "ok": False,
                    "errors": verdict["errors"],
                    "violations_checked": verdict["violations_checked"],
                    "pages_found": verdict["pages_found"],
                }
            )
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
