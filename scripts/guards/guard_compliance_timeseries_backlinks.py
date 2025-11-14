#!/usr/bin/env python3
"""
Guard for E87 Compliance Time-Series + Heatmaps.

Validates:
- compliance_timeseries.json exists and has correct structure
- Dashboard HTML files exist and have required backlinks
- All backlinked files exist
- Charts are present in HTML (Chart.js usage)

Emits verdict JSON to evidence/guard_atlas_compliance_timeseries.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

VERDICT_PATH = REPO / "evidence" / "guard_atlas_compliance_timeseries.json"

# Expected files
COMPLIANCE_TIMESERIES_JSON = REPO / "share" / "atlas" / "control_plane" / "compliance_timeseries.json"
DASHBOARD_HTML_TS = REPO / "docs" / "atlas" / "dashboard" / "compliance_timeseries.html"
DASHBOARD_HTML_HM = REPO / "docs" / "atlas" / "dashboard" / "compliance_heatmap.html"

# Required keys in compliance_timeseries.json
REQUIRED_KEYS = {"episode", "schema", "generated_at", "series_by_code", "series_by_tool", "heatmap"}
REQUIRED_SCHEMA = "compliance_timeseries_v1"

# Required backlinks in dashboard HTML
REQUIRED_BACKLINKS_TS = [
    "backlink-compliance-timeseries-json",
    "backlink-compliance-head-json",
    "backlink-top-violations-7d-json",
    "backlink-top-violations-30d-json",
    "backlink-guard-atlas-compliance-timeseries-json",
]

REQUIRED_BACKLINKS_HM = [
    "backlink-compliance-timeseries-json",
    "backlink-compliance-head-json",
    "backlink-top-violations-7d-json",
    "backlink-top-violations-30d-json",
    "backlink-guard-atlas-compliance-timeseries-json",
]


def check_json_structure(filepath: Path) -> tuple[bool, list[str]]:
    """Check compliance_timeseries.json structure."""
    errors = []

    if not filepath.exists():
        return False, ["compliance_timeseries.json missing"]

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
    if data.get("episode") != "E87":
        errors.append(f"Wrong episode: expected E87, got {data.get('episode')}")

    # Check schema
    if data.get("schema") != REQUIRED_SCHEMA:
        errors.append(f"Wrong schema: expected {REQUIRED_SCHEMA}, got {data.get('schema')}")

    # Check series_by_code structure
    series_by_code = data.get("series_by_code", [])
    if not isinstance(series_by_code, list):
        errors.append("series_by_code must be a list")
    else:
        for item in series_by_code[:5]:  # Check first 5 items
            if not isinstance(item, dict):
                errors.append("series_by_code items must be dicts")
            elif "code" not in item or "series" not in item:
                errors.append("series_by_code items must have 'code' and 'series' keys")

    # Check series_by_tool structure
    series_by_tool = data.get("series_by_tool", [])
    if not isinstance(series_by_tool, list):
        errors.append("series_by_tool must be a list")
    else:
        for item in series_by_tool[:5]:  # Check first 5 items
            if not isinstance(item, dict):
                errors.append("series_by_tool items must be dicts")
            elif "tool" not in item or "series" not in item:
                errors.append("series_by_tool items must have 'tool' and 'series' keys")

    # Check heatmap structure
    heatmap = data.get("heatmap", [])
    if not isinstance(heatmap, list):
        errors.append("heatmap must be a list")
    else:
        for item in heatmap[:5]:  # Check first 5 items
            if not isinstance(item, dict):
                errors.append("heatmap items must be dicts")
            elif not all(k in item for k in ["tool", "code", "count"]):
                errors.append("heatmap items must have 'tool', 'code', and 'count' keys")

    return len(errors) == 0, errors


def check_dashboard_html(filepath: Path, required_backlinks: list[str]) -> tuple[bool, list[str]]:
    """Check dashboard HTML has required backlinks and Chart.js."""
    errors = []

    if not filepath.exists():
        return False, [f"{filepath.name} missing"]

    try:
        content = filepath.read_text()
    except OSError as e:
        return False, [f"Failed to read HTML: {e}"]

    # Check for required backlinks
    for backlink_id in required_backlinks:
        if f'data-testid="{backlink_id}"' not in content:
            errors.append(f"Missing backlink: {backlink_id}")

    # Check for Chart.js (required for charts)
    if "chart.js" not in content.lower() and "chart.umd" not in content.lower():
        errors.append("Missing Chart.js library reference")

    # Check for canvas elements (required for charts)
    if "<canvas" not in content:
        errors.append("Missing canvas elements for charts")

    return len(errors) == 0, errors


def main() -> int:
    """Run guard checks."""
    verdict = {
        "ok": True,
        "errors": [],
        "checks": {},
    }

    # Check JSON structure
    json_ok, json_errors = check_json_structure(COMPLIANCE_TIMESERIES_JSON)
    verdict["checks"]["compliance_timeseries_json"] = {
        "ok": json_ok,
        "errors": json_errors,
    }
    if not json_ok:
        verdict["ok"] = False
        verdict["errors"].extend(json_errors)

    # Check timeseries dashboard HTML
    html_ts_ok, html_ts_errors = check_dashboard_html(DASHBOARD_HTML_TS, REQUIRED_BACKLINKS_TS)
    verdict["checks"]["dashboard_html_timeseries"] = {
        "ok": html_ts_ok,
        "errors": html_ts_errors,
    }
    if not html_ts_ok:
        verdict["ok"] = False
        verdict["errors"].extend(html_ts_errors)

    # Check heatmap dashboard HTML
    html_hm_ok, html_hm_errors = check_dashboard_html(DASHBOARD_HTML_HM, REQUIRED_BACKLINKS_HM)
    verdict["checks"]["dashboard_html_heatmap"] = {
        "ok": html_hm_ok,
        "errors": html_hm_errors,
    }
    if not html_hm_ok:
        verdict["ok"] = False
        verdict["errors"].extend(html_hm_errors)

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
