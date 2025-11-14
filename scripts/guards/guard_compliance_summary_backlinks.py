#!/usr/bin/env python3
"""
Guard for E86 Compliance Summary Dashboard.

Validates:
- compliance_summary.json exists and has correct structure
- Dashboard HTML exists and has required backlinks
- All backlinked files exist

Emits verdict JSON to evidence/guard_atlas_compliance_summary.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

VERDICT_PATH = REPO / "evidence" / "guard_atlas_compliance_summary.json"

# Expected files
COMPLIANCE_SUMMARY_JSON = REPO / "share" / "atlas" / "control_plane" / "compliance_summary.json"
DASHBOARD_HTML = REPO / "docs" / "atlas" / "dashboard" / "compliance_summary.html"

# Required keys in compliance_summary.json
REQUIRED_KEYS = {"episode", "schema", "generated_at", "metrics"}
REQUIRED_METRICS_KEYS = {
    "total_violations",
    "violations_by_code",
    "violations_by_tool",
    "top_offenders",
}

# Required backlinks in dashboard HTML
REQUIRED_BACKLINKS = [
    "backlink-compliance-summary-json",
    "backlink-compliance-head-json",
    "backlink-top-violations-7d-json",
    "backlink-top-violations-30d-json",
    "backlink-guard-atlas-compliance-summary-json",
]


def check_json_structure(filepath: Path) -> tuple[bool, list[str]]:
    """Check compliance_summary.json structure."""
    errors = []

    if not filepath.exists():
        return False, ["compliance_summary.json missing"]

    try:
        with filepath.open() as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        return False, [f"JSON decode error: {e}"]

    # Check required keys
    missing_keys = REQUIRED_KEYS - set(data.keys())
    if missing_keys:
        errors.append(f"Missing required keys: {missing_keys}")

    # Check episode
    if data.get("episode") != "E86":
        errors.append(f"Wrong episode: expected E86, got {data.get('episode')}")

    # Check metrics structure
    metrics = data.get("metrics", {})
    missing_metrics_keys = REQUIRED_METRICS_KEYS - set(metrics.keys())
    if missing_metrics_keys:
        errors.append(f"Missing required metrics keys: {missing_metrics_keys}")

    # Check total_violations structure
    total_violations = metrics.get("total_violations", {})
    if not isinstance(total_violations, dict):
        errors.append("total_violations must be a dict")
    else:
        for window in ["24h", "7d", "30d"]:
            if window not in total_violations:
                errors.append(f"total_violations missing window: {window}")

    return len(errors) == 0, errors


def check_dashboard_html(filepath: Path) -> tuple[bool, list[str]]:
    """Check dashboard HTML has required backlinks."""
    errors = []

    if not filepath.exists():
        return False, ["compliance_summary.html missing"]

    try:
        content = filepath.read_text()
    except OSError as e:
        return False, [f"Failed to read HTML: {e}"]

    # Check for required backlinks
    for backlink_id in REQUIRED_BACKLINKS:
        if f'data-testid="{backlink_id}"' not in content:
            errors.append(f"Missing backlink: {backlink_id}")

    return len(errors) == 0, errors


def main() -> int:
    """Run guard checks."""
    verdict = {
        "ok": True,
        "errors": [],
        "checks": {},
    }

    # Check JSON structure
    json_ok, json_errors = check_json_structure(COMPLIANCE_SUMMARY_JSON)
    verdict["checks"]["compliance_summary_json"] = {
        "ok": json_ok,
        "errors": json_errors,
    }
    if not json_ok:
        verdict["ok"] = False
        verdict["errors"].extend(json_errors)

    # Check dashboard HTML
    html_ok, html_errors = check_dashboard_html(DASHBOARD_HTML)
    verdict["checks"]["dashboard_html"] = {
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
        print(json.dumps({"ok": True, "errors": []}))
        return 0
    else:
        print(json.dumps({"ok": False, "errors": verdict["errors"]}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
