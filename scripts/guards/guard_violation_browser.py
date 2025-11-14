#!/usr/bin/env python3
"""
Guard for E89 Unified Violation Browser.

Validates:
- violations_browser.json exists and has correct structure
- violations.html exists and has required backlinks
- All required fields present in JSON export
- Backlinks to E86/E87/E88 dashboards present

Emits verdict JSON to evidence/guard_atlas_violation_browser.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

VERDICT_PATH = REPO / "evidence" / "guard_atlas_violation_browser.json"

BROWSER_JSON = REPO / "share" / "atlas" / "control_plane" / "violations_browser.json"
BROWSER_HTML = REPO / "docs" / "atlas" / "browser" / "violations.html"

# Required backlinks in browser HTML
REQUIRED_BACKLINKS = [
    "backlink-compliance-summary",
    "backlink-compliance-timeseries",
    "backlink-compliance-heatmap",
    "backlink-violations-browser-json",
    "backlink-guard-violation-browser-json",
]


def check_json_structure(filepath: Path) -> tuple[bool, list[str]]:
    """Check violations_browser.json structure."""
    errors = []

    if not filepath.exists():
        return False, ["violations_browser.json missing"]

    try:
        with filepath.open() as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        return False, [f"JSON decode error: {e}"]

    # Check episode
    if data.get("episode") != "E89":
        errors.append(f"Wrong episode: expected E89, got {data.get('episode')}")

    # Check schema
    if data.get("schema") != "violations_browser_v1":
        errors.append(f"Wrong schema: expected violations_browser_v1, got {data.get('schema')}")

    # Check required top-level keys
    required_keys = {"episode", "schema", "generated_at", "violations", "filters", "stats"}
    missing_keys = required_keys - set(data.keys())
    if missing_keys:
        errors.append(f"Missing required keys: {missing_keys}")

    # Check violations is a list
    if not isinstance(data.get("violations"), list):
        errors.append("violations must be a list")

    # Check filters structure
    filters = data.get("filters", {})
    if not isinstance(filters, dict):
        errors.append("filters must be a dict")
    else:
        if "tools" not in filters:
            errors.append("filters missing 'tools'")
        if "rings" not in filters:
            errors.append("filters missing 'rings'")

    # Check stats structure
    stats = data.get("stats", {})
    if not isinstance(stats, dict):
        errors.append("stats must be a dict")
    else:
        required_stats = {"total_violations", "total_count_7d", "total_count_30d"}
        missing_stats = required_stats - set(stats.keys())
        if missing_stats:
            errors.append(f"stats missing keys: {missing_stats}")

    return len(errors) == 0, errors


def check_html_backlinks(filepath: Path) -> tuple[bool, list[str]]:
    """Check violations.html has required backlinks."""
    errors = []

    if not filepath.exists():
        return False, ["violations.html missing"]

    try:
        content = filepath.read_text()
    except OSError as e:
        return False, [f"Failed to read HTML: {e}"]

    # Check for required backlinks
    for backlink_id in REQUIRED_BACKLINKS:
        if f'data-testid="{backlink_id}"' not in content:
            errors.append(f"Missing backlink: {backlink_id}")

    # Check for E89 badge
    if 'class="badge">E89' not in content and 'badge">E89' not in content:
        errors.append("Missing E89 badge")

    return len(errors) == 0, errors


def main() -> int:
    """Run guard checks."""
    verdict = {
        "ok": True,
        "errors": [],
        "checks": {},
    }

    # Check JSON structure
    json_ok, json_errors = check_json_structure(BROWSER_JSON)
    verdict["checks"]["json_structure"] = {
        "ok": json_ok,
        "errors": json_errors,
    }
    if not json_ok:
        verdict["ok"] = False
        verdict["errors"].extend(json_errors)

    # Check HTML backlinks
    html_ok, html_errors = check_html_backlinks(BROWSER_HTML)
    verdict["checks"]["html_backlinks"] = {
        "ok": html_ok,
        "errors": html_errors,
    }
    if not html_ok:
        verdict["ok"] = False
        verdict["errors"].extend(html_errors)

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
                    "checks": {k: v["ok"] for k, v in verdict["checks"].items()},
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
                    "checks": {k: v["ok"] for k, v in verdict["checks"].items()},
                }
            )
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
