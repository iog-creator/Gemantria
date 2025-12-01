#!/usr/bin/env python3
"""
Guard for E87 Compliance Time-Series & Heatmaps.

Validates:
- compliance_timeseries.json exists and has required structure
- compliance_timeseries.html exists and contains required backlinks
- compliance_heatmap.html exists and contains required backlinks
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

CONTROL_PLANE_DIR = REPO / "share" / "atlas" / "control_plane"
DASHBOARD_DIR = REPO / "docs" / "atlas" / "dashboard"
EVIDENCE_DIR = REPO / "evidence"


def check_json_structure() -> dict[str, bool]:
    """Check compliance_timeseries.json structure."""
    json_path = CONTROL_PLANE_DIR / "compliance_timeseries.json"

    if not json_path.exists():
        return {"json_exists": False, "json_structure": False}

    try:
        with json_path.open() as f:
            data = json.load(f)

        # Check required top-level fields
        required_fields = [
            "episode",
            "schema",
            "generated_at",
            "series_by_code",
            "series_by_tool",
            "heatmap_tool_by_code",
        ]
        has_fields = all(field in data for field in required_fields)

        # Check episode and schema
        episode_ok = data.get("episode") == "E87"
        schema_ok = data.get("schema") == "compliance_timeseries_v1"

        # Check array structures
        series_by_code_ok = isinstance(data.get("series_by_code"), list)
        series_by_tool_ok = isinstance(data.get("series_by_tool"), list)
        heatmap_ok = isinstance(data.get("heatmap_tool_by_code"), dict) and "entries" in data["heatmap_tool_by_code"]

        structure_ok = (
            has_fields and episode_ok and schema_ok and series_by_code_ok and series_by_tool_ok and heatmap_ok
        )

        return {
            "json_exists": True,
            "json_structure": structure_ok,
            "episode_correct": episode_ok,
            "schema_correct": schema_ok,
            "arrays_valid": series_by_code_ok and series_by_tool_ok,
            "heatmap_valid": heatmap_ok,
        }

    except (OSError, json.JSONDecodeError):
        return {"json_exists": True, "json_structure": False}


def check_html_backlinks() -> dict[str, bool]:
    """Check HTML files exist and contain required backlinks."""
    timeseries_html = DASHBOARD_DIR / "compliance_timeseries.html"
    heatmap_html = DASHBOARD_DIR / "compliance_heatmap.html"

    results = {
        "timeseries_html_exists": timeseries_html.exists(),
        "heatmap_html_exists": heatmap_html.exists(),
        "timeseries_backlinks": False,
        "heatmap_backlinks": False,
    }

    # Check timeseries HTML backlinks
    if timeseries_html.exists():
        try:
            content = timeseries_html.read_text()
            required_backlinks = [
                'data-testid="backlink-compliance-timeseries-json"',
                'data-testid="backlink-top-violations-7d-json"',
                'data-testid="backlink-guard-atlas-compliance-timeseries-json"',
            ]
            results["timeseries_backlinks"] = all(link in content for link in required_backlinks)
        except OSError:
            results["timeseries_backlinks"] = False

    # Check heatmap HTML backlinks
    if heatmap_html.exists():
        try:
            content = heatmap_html.read_text()
            required_backlinks = [
                'data-testid="backlink-compliance-timeseries-json"',
                'data-testid="backlink-guard-atlas-compliance-timeseries-json"',
            ]
            results["heatmap_backlinks"] = all(link in content for link in required_backlinks)
        except OSError:
            results["heatmap_backlinks"] = False

    return results


def main() -> int:
    """Run the compliance timeseries guard."""
    json_checks = check_json_structure()
    html_checks = check_html_backlinks()

    # Overall assessment
    json_ok = json_checks.get("json_exists", False) and json_checks.get("json_structure", False)
    html_ok = (
        html_checks.get("timeseries_html_exists", False)
        and html_checks.get("heatmap_html_exists", False)
        and html_checks.get("timeseries_backlinks", False)
        and html_checks.get("heatmap_backlinks", False)
    )

    overall_ok = json_ok and html_ok

    verdict = {
        "episode": "E87",
        "guard": "guard_atlas_compliance_timeseries",
        "ok": overall_ok,
        "checks": {
            "json": json_checks,
            "html": html_checks,
        },
        "summary": {
            "json_ok": json_ok,
            "html_ok": html_ok,
            "overall_ok": overall_ok,
        },
    }

    # Write evidence
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    evidence_path = EVIDENCE_DIR / "guard_atlas_compliance_timeseries.json"

    with evidence_path.open("w") as f:
        json.dump(verdict, f, indent=2)

    print(f"[guard_atlas_compliance_timeseries] Verdict: {'PASS' if overall_ok else 'FAIL'}")
    print(f"[guard_atlas_compliance_timeseries] Evidence: {evidence_path}")

    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
