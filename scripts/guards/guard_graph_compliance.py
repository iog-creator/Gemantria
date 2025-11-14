#!/usr/bin/env python3
"""
Guard for E90 Graph Compliance Metrics.

Validates:
- graph_compliance.json exists and has correct structure
- graph_compliance.html exists and has required backlinks
- All required fields present in JSON export

Emits verdict JSON to evidence/guard_control_graph_compliance.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

VERDICT_PATH = REPO / "evidence" / "guard_control_graph_compliance.json"

COMPLIANCE_JSON = REPO / "share" / "atlas" / "control_plane" / "graph_compliance.json"
COMPLIANCE_HTML = REPO / "docs" / "atlas" / "dashboard" / "graph_compliance.html"

# Required backlinks in HTML
REQUIRED_BACKLINKS = [
    "backlink-graph-compliance-json",
    "backlink-compliance-summary-json",
    "backlink-guard-graph-compliance-json",
    "backlink-compliance-summary-dashboard",
    "backlink-compliance-timeseries-dashboard",
]


def check_json_structure(filepath: Path) -> tuple[bool, list[str]]:
    """Check graph_compliance.json structure."""
    errors = []

    if not filepath.exists():
        return False, ["graph_compliance.json missing"]

    try:
        with filepath.open() as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        return False, [f"JSON decode error: {e}"]

    # Check episode
    if data.get("episode") != "E90":
        errors.append(f"Wrong episode: expected E90, got {data.get('episode')}")

    # Check schema
    if data.get("schema") != "graph_compliance_v1":
        errors.append(f"Wrong schema: expected graph_compliance_v1, got {data.get('schema')}")

    # Check required top-level keys
    required_keys = {"episode", "schema", "generated_at", "summary", "details"}
    missing_keys = required_keys - set(data.keys())
    if missing_keys:
        errors.append(f"Missing required keys: {missing_keys}")

    # Check summary structure
    summary = data.get("summary", {})
    if not isinstance(summary, dict):
        errors.append("summary must be a dict")
    else:
        required_summary_keys = {"nodes", "patterns", "tools", "batches"}
        missing_summary_keys = required_summary_keys - set(summary.keys())
        if missing_summary_keys:
            errors.append(f"summary missing keys: {missing_summary_keys}")

    # Check details is a list
    if not isinstance(data.get("details"), list):
        errors.append("details must be a list")

    return len(errors) == 0, errors


def check_html_backlinks(filepath: Path) -> tuple[bool, list[str]]:
    """Check graph_compliance.html has required backlinks."""
    errors = []

    if not filepath.exists():
        return False, ["graph_compliance.html missing"]

    try:
        content = filepath.read_text()
    except OSError as e:
        return False, [f"Failed to read HTML: {e}"]

    # Check for required backlinks
    for backlink_id in REQUIRED_BACKLINKS:
        if f'data-testid="{backlink_id}"' not in content:
            errors.append(f"Missing backlink: {backlink_id}")

    # Check for E90 badge
    if 'class="badge">E90' not in content and 'badge">E90' not in content:
        errors.append("Missing E90 badge")

    return len(errors) == 0, errors


def main() -> int:
    """Run guard checks."""
    verdict = {
        "ok": True,
        "errors": [],
        "checks": {},
    }

    # Check JSON structure
    json_ok, json_errors = check_json_structure(COMPLIANCE_JSON)
    verdict["checks"]["json_structure"] = {
        "ok": json_ok,
        "errors": json_errors,
    }
    if not json_ok:
        verdict["ok"] = False
        verdict["errors"].extend(json_errors)

    # Check HTML backlinks
    html_ok, html_errors = check_html_backlinks(COMPLIANCE_HTML)
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
