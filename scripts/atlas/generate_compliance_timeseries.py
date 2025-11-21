#!/usr/bin/env python3
"""
Generate compliance_timeseries.json for E87 Violation Time-Series & Heatmaps.

Aggregates data from existing compliance exports for time-series analysis:
- top_violations_7d.json
- top_violations_30d.json
- agent_runs_7d.json (if available)
- compliance.head.json

Generates metrics for:
- Time-series by violation code
- Time-series by tool
- Heatmap data (tool x violation code)
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, UTC
from pathlib import Path
from collections import defaultdict

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

OUTPUT_DIR = REPO / "share" / "atlas" / "control_plane"
CONTROL_PLANE_DIR = OUTPUT_DIR


def load_json_file(filepath: Path) -> dict | None:
    """Load JSON file, return None if missing or invalid."""
    if not filepath.exists():
        return None
    try:
        with filepath.open() as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def extract_violations_by_code(violations_data: dict | None) -> dict[str, int]:
    """Extract violations grouped by code from violations data."""
    violations = violations_data.get("violations", []) if violations_data else []
    by_code = defaultdict(int)

    for item in violations:
        if isinstance(item, dict):
            code = item.get("violation_code", "unknown")
            count = item.get("count", 0)
        else:
            # Handle case where violations is a dict mapping code -> count
            code = str(item) if not isinstance(item, dict) else item.get("violation_code", "unknown")
            count = violations_data["violations"].get(item, 0) if isinstance(violations_data["violations"], dict) else 0

        by_code[code] += count

    return dict(by_code)


def extract_tool_from_code(violation_code: str) -> str:
    """Extract tool name from violation code (heuristic)."""
    if "." not in violation_code:
        return "unknown"
    parts = violation_code.split(".")
    if len(parts) >= 2:
        return parts[1]  # Second part is usually the tool
    return "unknown"


def create_timeseries_by_code(violations_7d: dict | None, violations_30d: dict | None) -> list[dict]:
    """Create time-series data by violation code."""
    codes = set()

    # Collect all unique codes
    if violations_7d:
        codes.update(extract_violations_by_code(violations_7d).keys())
    if violations_30d:
        codes.update(extract_violations_by_code(violations_30d).keys())

    series = []
    for code in sorted(codes):
        # Get counts for each window
        count_7d = extract_violations_by_code(violations_7d).get(code, 0)
        count_30d = extract_violations_by_code(violations_30d).get(code, 0)

        # Estimate daily breakdown (simplified)
        series.append(
            {
                "code": code,
                "data_points": [
                    {"period": "7d", "count": count_7d},
                    {"period": "30d", "count": count_30d},
                ],
            }
        )

    return series


def create_timeseries_by_tool(violations_7d: dict | None, violations_30d: dict | None) -> list[dict]:
    """Create time-series data by tool."""
    tools = set()

    # Collect all unique tools
    for violations_data in [violations_7d, violations_30d]:
        if violations_data:
            codes = extract_violations_by_code(violations_data)
            for code in codes:
                tools.add(extract_tool_from_code(code))

    series = []
    for tool in sorted(tools):
        # Aggregate counts for this tool across all violation codes
        count_7d = 0
        count_30d = 0

        for violations_data, window in [(violations_7d, "7d"), (violations_30d, "30d")]:
            if violations_data:
                codes = extract_violations_by_code(violations_data)
                for code, count in codes.items():
                    if extract_tool_from_code(code) == tool:
                        if window == "7d":
                            count_7d += count
                        else:
                            count_30d += count

        series.append(
            {
                "tool": tool,
                "data_points": [
                    {"period": "7d", "count": count_7d},
                    {"period": "30d", "count": count_30d},
                ],
            }
        )

    return series


def create_heatmap_tool_by_code(violations_7d: dict | None, violations_30d: dict | None) -> dict:
    """Create heatmap data (tool x violation code) with counts."""
    heatmap = defaultdict(lambda: defaultdict(int))

    for violations_data, weight in [(violations_7d, 1.0), (violations_30d, 0.3)]:  # Weight 30d less
        if violations_data:
            codes = extract_violations_by_code(violations_data)
            for code, count in codes.items():
                tool = extract_tool_from_code(code)
                heatmap[tool][code] += int(count * weight)

    # Convert to list format for JSON
    heatmap_list = []
    for tool in sorted(heatmap.keys()):
        for code in sorted(heatmap[tool].keys()):
            heatmap_list.append({"tool": tool, "code": code, "count": heatmap[tool][code]})

    return {"entries": heatmap_list}


def generate_compliance_timeseries() -> dict:
    """Generate compliance timeseries JSON from existing exports."""
    # Load existing exports
    violations_7d = load_json_file(CONTROL_PLANE_DIR / "top_violations_7d.json")
    violations_30d = load_json_file(CONTROL_PLANE_DIR / "top_violations_30d.json")
    agent_runs_7d = load_json_file(CONTROL_PLANE_DIR / "agent_runs_7d.json")
    head_data = load_json_file(CONTROL_PLANE_DIR / "compliance.head.json")

    # Generate time-series data
    series_by_code = create_timeseries_by_code(violations_7d, violations_30d)
    series_by_tool = create_timeseries_by_tool(violations_7d, violations_30d)
    heatmap_tool_by_code = create_heatmap_tool_by_code(violations_7d, violations_30d)

    # Build timeseries export
    timeseries = {
        "episode": "E87",
        "schema": "compliance_timeseries_v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "series_by_code": series_by_code,
        "series_by_tool": series_by_tool,
        "heatmap_tool_by_code": heatmap_tool_by_code,
        "source_exports": {
            "top_violations_7d.json": violations_7d is not None,
            "top_violations_30d.json": violations_30d is not None,
            "agent_runs_7d.json": agent_runs_7d is not None,
            "compliance.head.json": head_data is not None,
        },
        "metadata": {
            "total_codes": len(series_by_code),
            "total_tools": len(series_by_tool),
            "heatmap_entries": len(heatmap_tool_by_code["entries"]),
        },
    }

    return timeseries


def main() -> int:
    """Generate compliance_timeseries.json."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        timeseries = generate_compliance_timeseries()
        output_path = OUTPUT_DIR / "compliance_timeseries.json"

        with output_path.open("w") as f:
            json.dump(timeseries, f, indent=2)

        print(f"[generate_compliance_timeseries] Wrote {output_path}")
        return 0
    except Exception as e:
        print(f"ERROR: Failed to generate compliance timeseries: {e}", file=sys.stderr)
        # Write error export for CI tolerance
        error_timeseries = {
            "episode": "E87",
            "schema": "compliance_timeseries_v1",
            "generated_at": datetime.now(UTC).isoformat(),
            "ok": False,
            "error": str(e),
            "series_by_code": [],
            "series_by_tool": [],
            "heatmap_tool_by_code": {"entries": []},
        }
        output_path = OUTPUT_DIR / "compliance_timeseries.json"
        with output_path.open("w") as f:
            json.dump(error_timeseries, f, indent=2)
        return 0  # Exit 0 for CI tolerance


if __name__ == "__main__":
    sys.exit(main())
