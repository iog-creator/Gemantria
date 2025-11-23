#!/usr/bin/env python3
"""
Guard for E89 Violation Browser.

Validates:
- Violations browser HTML exists and is properly structured
- Search/filter/sort functionality is present
- All required backlinks are present (dashboards, drilldowns, JSON exports)
- Links resolve correctly
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

BROWSER_FILE = REPO / "docs" / "atlas" / "browser" / "violations.html"
EVIDENCE_DIR = REPO / "evidence"

# Required backlinks (testid attributes)
REQUIRED_BACKLINKS = [
    "backlink-compliance-summary",
    "backlink-compliance-timeseries",
    "backlink-guard-receipts",
    "backlink-json-summary",
    "backlink-json-7d",
    "backlink-json-30d",
    "backlink-json-graph-compliance",
    "backlink-evidence-dir",
]

# Required UI elements
REQUIRED_UI_ELEMENTS = {
    "search": "input#search",
    "codeFilter": "select#codeFilter",
    "sortBy": "select#sortBy",
    "sortOrder": "select#sortOrder",
    "table": "table#violationsTable",
}


def check_file_exists() -> dict[str, bool | str]:
    """Check that violations browser file exists."""
    if not BROWSER_FILE.exists():
        return {
            "exists": False,
            "error": f"File not found: {BROWSER_FILE}",
        }
    return {"exists": True}


def check_html_structure(content: str) -> dict[str, bool | list[str]]:
    """Check HTML structure and required elements."""
    issues = []

    # Check for E89 badge
    if 'class="badge">E89</span>' not in content:
        issues.append("Missing E89 badge")

    # Check for required UI elements
    for name, selector in REQUIRED_UI_ELEMENTS.items():
        # Convert CSS selector to regex pattern
        if selector.startswith("input#"):
            id_name = selector.split("#")[1]
            pattern = rf'<input[^>]*id=["\']{id_name}["\']'
        elif selector.startswith("select#"):
            id_name = selector.split("#")[1]
            pattern = rf'<select[^>]*id=["\']{id_name}["\']'
        elif selector.startswith("table#"):
            id_name = selector.split("#")[1]
            pattern = rf'<table[^>]*id=["\']{id_name}["\']'
        else:
            pattern = selector

        if not re.search(pattern, content, re.IGNORECASE):
            issues.append(f"Missing UI element: {name} ({selector})")

    # Check for JavaScript functionality
    if "applyFilters" not in content:
        issues.append("Missing applyFilters function")
    if "sortTable" not in content:
        issues.append("Missing sortTable function")

    return {
        "structure_ok": len(issues) == 0,
        "issues": issues,
    }


def check_backlinks(content: str) -> dict[str, bool | list[str]]:
    """Check that all required backlinks are present."""
    missing = []
    found = []

    for testid in REQUIRED_BACKLINKS:
        pattern = rf'data-testid=["\']{testid}["\']'
        if re.search(pattern, content):
            found.append(testid)
        else:
            missing.append(testid)

    return {
        "all_backlinks_present": len(missing) == 0,
        "missing_backlinks": missing,
        "found_backlinks": found,
    }


def check_links_resolve() -> dict[str, bool | list[str]]:
    """Check that key links resolve to existing files."""
    if not BROWSER_FILE.exists():
        return {
            "links_ok": False,
            "errors": ["Browser file does not exist"],
        }

    content = BROWSER_FILE.read_text()
    errors = []

    # Check relative links from browser directory
    browser_dir = BROWSER_FILE.parent

    # Extract href attributes
    href_pattern = r'href=["\']([^"\']+)["\']'
    hrefs = re.findall(href_pattern, content)

    for href in hrefs:
        # Skip external links and anchors
        if href.startswith("http") or href.startswith("#") or href.startswith("mailto:"):
            continue

        # Skip app routes (absolute paths)
        if href.startswith("/"):
            continue

        # Resolve relative path
        target = (browser_dir / href).resolve()

        # Check if it's within the repo
        try:
            target.relative_to(REPO)
        except ValueError:
            continue

        # Check if file exists (for files, not directories)
        if not target.exists() and not target.is_dir():
            # Allow JSON files in share/ to be missing (they're generated)
            if "share/atlas/control_plane" in str(target) and target.suffix == ".json":
                continue
            # Allow evidence directory
            if "evidence" in str(target):
                continue
            errors.append(f"Broken link: {href} -> {target}")

    return {
        "links_ok": len(errors) == 0,
        "errors": errors,
    }


def main() -> int:
    """Run guard checks."""
    parser = argparse.ArgumentParser(description="Guard for E89 Violation Browser")
    parser.add_argument(
        "--write-evidence",
        type=str,
        help="Write evidence JSON to this file",
    )
    args = parser.parse_args()

    verdict = {
        "guard": "guard_atlas_violation_browser",
        "episode": "E89",
        "overall_ok": True,
        "checks": {},
    }

    # Check file exists
    file_check = check_file_exists()
    verdict["checks"]["file_exists"] = file_check
    if not file_check["exists"]:
        verdict["overall_ok"] = False
        print(f"[guard_atlas_violation_browser] FAIL: {file_check.get('error', 'File missing')}", file=sys.stderr)
        if args.write_evidence:
            EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
            evidence_file = EVIDENCE_DIR / args.write_evidence
            evidence_file.write_text(json.dumps(verdict, indent=2))
        return 1

    # Read file content
    content = BROWSER_FILE.read_text()

    # Check HTML structure
    structure_check = check_html_structure(content)
    verdict["checks"]["html_structure"] = structure_check
    if not structure_check["structure_ok"]:
        verdict["overall_ok"] = False
        print(
            f"[guard_atlas_violation_browser] Structure issues: {structure_check['issues']}",
            file=sys.stderr,
        )

    # Check backlinks
    backlinks_check = check_backlinks(content)
    verdict["checks"]["backlinks"] = backlinks_check
    if not backlinks_check["all_backlinks_present"]:
        verdict["overall_ok"] = False
        print(
            f"[guard_atlas_violation_browser] Missing backlinks: {backlinks_check['missing_backlinks']}",
            file=sys.stderr,
        )

    # Check links resolve
    links_check = check_links_resolve()
    verdict["checks"]["links_resolve"] = links_check
    if not links_check["links_ok"]:
        verdict["overall_ok"] = False
        print(
            f"[guard_atlas_violation_browser] Broken links: {links_check['errors']}",
            file=sys.stderr,
        )

    # Print verdict
    if verdict["overall_ok"]:
        print("[guard_atlas_violation_browser] Verdict: PASS")
    else:
        print("[guard_atlas_violation_browser] Verdict: FAIL", file=sys.stderr)

    # Write evidence if requested
    if args.write_evidence:
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        # Handle both relative and absolute paths
        if Path(args.write_evidence).is_absolute():
            evidence_file = Path(args.write_evidence)
        else:
            evidence_file = EVIDENCE_DIR / args.write_evidence
        evidence_file.parent.mkdir(parents=True, exist_ok=True)
        evidence_file.write_text(json.dumps(verdict, indent=2))
        print(f"[guard_atlas_violation_browser] Evidence: {evidence_file}")

    return 0 if verdict["overall_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
