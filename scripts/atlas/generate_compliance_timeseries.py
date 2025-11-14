#!/usr/bin/env python3
"""
Generate compliance_timeseries.json for E87 Violation Time-Series + Heatmaps.

Aggregates data from existing compliance exports:
- compliance.head.json
- top_violations_7d.json
- top_violations_30d.json

Generates time-series data for:
- Violations per code over time
- Violations per tool over time
- Heatmap data (tool x violation type)
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime, UTC, timedelta
from pathlib import Path

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


def extract_tool_from_code(code: str) -> str:
    """Extract tool name from violation code (e.g., 'guard.dsn.centralized' -> 'dsn')."""
    if "." in code:
        parts = code.split(".")
        if len(parts) >= 2:
            return parts[1]
    return "unknown"


def generate_timeseries_data(
    violations_7d: dict | None, violations_30d: dict | None
) -> tuple[list[dict], list[dict], dict[str, dict[str, int]]]:
    """
    Generate time-series data from violations.

    Returns:
        - series_by_code: List of time-series for each violation code
        - series_by_tool: List of time-series for each tool
        - heatmap_data: Dict mapping tool -> violation_code -> count
    """
    now = datetime.now(UTC)
    series_by_code: dict[str, list[dict]] = defaultdict(list)
    series_by_tool: dict[str, list[dict]] = defaultdict(list)
    heatmap_data: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    # Generate time points for last 30 days (daily buckets)
    time_points = []
    for i in range(30):
        date = now - timedelta(days=29 - i)
        time_points.append(date.isoformat())

    # Process 7d and 30d violations
    for window_name, violations_data, days_back in [
        ("7d", violations_7d, 7),
        ("30d", violations_30d, 30),
    ]:
        if not violations_data or not violations_data.get("violations"):
            continue

        violations = violations_data.get("violations", [])
        if isinstance(violations, dict):
            # Convert dict to list format
            violations = [{"violation_code": code, "count": count} for code, count in violations.items()]

        # Distribute violations across time points (simplified: assume uniform distribution)
        for item in violations:
            if isinstance(item, dict):
                code = item.get("violation_code", "unknown")
                count = item.get("count", 0)
            else:
                code = str(item)
                count = (
                    violations_data.get("violations", {}).get(code, 0)
                    if isinstance(violations_data.get("violations"), dict)
                    else 0
                )

            tool = extract_tool_from_code(code)

            # Add to heatmap
            heatmap_data[tool][code] += count

            # Distribute count across time points in window
            points_in_window = min(days_back, len(time_points))
            count_per_point = max(1, count // points_in_window) if points_in_window > 0 else 0
            remainder = count % points_in_window if points_in_window > 0 else 0

            # Add data points for this code
            for i, timestamp in enumerate(time_points[-points_in_window:]):
                value = count_per_point + (1 if i < remainder else 0)
                series_by_code[code].append({"timestamp": timestamp, "value": value})

            # Add data points for this tool
            for i, timestamp in enumerate(time_points[-points_in_window:]):
                value = count_per_point + (1 if i < remainder else 0)
                series_by_tool[tool].append({"timestamp": timestamp, "value": value})

    # Aggregate series by code
    aggregated_by_code = []
    for code, points in series_by_code.items():
        # Group by timestamp and sum values
        timestamp_values: dict[str, int] = defaultdict(int)
        for point in points:
            timestamp_values[point["timestamp"]] += point["value"]

        # Convert to sorted list
        aggregated_points = [{"timestamp": ts, "value": val} for ts, val in sorted(timestamp_values.items())]
        aggregated_by_code.append({"code": code, "series": aggregated_points})

    # Aggregate series by tool
    aggregated_by_tool = []
    for tool, points in series_by_tool.items():
        # Group by timestamp and sum values
        timestamp_values: dict[str, int] = defaultdict(int)
        for point in points:
            timestamp_values[point["timestamp"]] += point["value"]

        # Convert to sorted list
        aggregated_points = [{"timestamp": ts, "value": val} for ts, val in sorted(timestamp_values.items())]
        aggregated_by_tool.append({"tool": tool, "series": aggregated_points})

    # Convert heatmap to list format
    heatmap_list = []
    for tool, codes in heatmap_data.items():
        for code, count in codes.items():
            heatmap_list.append({"tool": tool, "code": code, "count": count})

    return aggregated_by_code, aggregated_by_tool, heatmap_list


def generate_compliance_timeseries() -> dict:
    """Generate compliance timeseries JSON from existing exports."""
    # Load existing exports
    head_data = load_json_file(CONTROL_PLANE_DIR / "compliance.head.json")
    violations_7d = load_json_file(CONTROL_PLANE_DIR / "top_violations_7d.json")
    violations_30d = load_json_file(CONTROL_PLANE_DIR / "top_violations_30d.json")

    # Generate time-series data
    series_by_code, series_by_tool, heatmap_data = generate_timeseries_data(violations_7d, violations_30d)

    # Build timeseries export
    timeseries = {
        "episode": "E87",
        "schema": "compliance_timeseries_v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "series_by_code": series_by_code,
        "series_by_tool": series_by_tool,
        "heatmap": heatmap_data,
        "source_exports": {
            "compliance.head.json": head_data is not None,
            "top_violations_7d.json": violations_7d is not None,
            "top_violations_30d.json": violations_30d is not None,
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
            "heatmap": [],
        }
        output_path = OUTPUT_DIR / "compliance_timeseries.json"
        with output_path.open("w") as f:
            json.dump(error_timeseries, f, indent=2)
        return 0  # Exit 0 for CI tolerance


if __name__ == "__main__":
    sys.exit(main())
