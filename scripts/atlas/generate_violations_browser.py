#!/usr/bin/env python3
"""
Generate unified violations browser export for E89.

Aggregates violation data from compliance exports into a unified browser-friendly format
with search, filter, and sort capabilities.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, UTC
from pathlib import Path
from urllib.parse import quote

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

OUTPUT_DIR = REPO / "share" / "atlas" / "control_plane"
CONTROL_PLANE_DIR = REPO / "share" / "atlas" / "control_plane"


def load_json_file(filepath: Path) -> dict | None:
    """Load JSON file, return None if missing or invalid."""
    if not filepath.exists():
        return None
    try:
        with filepath.open() as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def extract_all_violations() -> list[dict]:
    """Extract all violations from compliance exports with unified structure."""
    violations_map: dict[str, dict] = {}

    # Load compliance exports
    violations_7d = load_json_file(CONTROL_PLANE_DIR / "top_violations_7d.json")
    violations_30d = load_json_file(CONTROL_PLANE_DIR / "top_violations_30d.json")
    compliance_summary = load_json_file(CONTROL_PLANE_DIR / "compliance_summary.json")

    # Process 7d violations
    if violations_7d and violations_7d.get("violations"):
        violations = violations_7d["violations"]
        if isinstance(violations, list):
            for item in violations:
                if isinstance(item, dict) and "violation_code" in item:
                    code = item["violation_code"]
                    if code not in violations_map:
                        violations_map[code] = {
                            "violation_code": code,
                            "count_7d": 0,
                            "count_30d": 0,
                            "tool": code.split(".")[1] if "." in code else "unknown",
                            "ring": code.split(".")[0] if "." in code else "unknown",
                        }
                    violations_map[code]["count_7d"] = item.get("count", 0)
        elif isinstance(violations, dict):
            for code, count in violations.items():
                if code not in violations_map:
                    violations_map[code] = {
                        "violation_code": code,
                        "count_7d": 0,
                        "count_30d": 0,
                        "tool": code.split(".")[1] if "." in code else "unknown",
                        "ring": code.split(".")[0] if "." in code else "unknown",
                    }
                violations_map[code]["count_7d"] = count

    # Process 30d violations
    if violations_30d and violations_30d.get("violations"):
        violations = violations_30d["violations"]
        if isinstance(violations, list):
            for item in violations:
                if isinstance(item, dict) and "violation_code" in item:
                    code = item["violation_code"]
                    if code not in violations_map:
                        violations_map[code] = {
                            "violation_code": code,
                            "count_7d": 0,
                            "count_30d": 0,
                            "tool": code.split(".")[1] if "." in code else "unknown",
                            "ring": code.split(".")[0] if "." in code else "unknown",
                        }
                    violations_map[code]["count_30d"] = item.get("count", 0)
        elif isinstance(violations, dict):
            for code, count in violations.items():
                if code not in violations_map:
                    violations_map[code] = {
                        "violation_code": code,
                        "count_7d": 0,
                        "count_30d": 0,
                        "tool": code.split(".")[1] if "." in code else "unknown",
                        "ring": code.split(".")[0] if "." in code else "unknown",
                    }
                violations_map[code]["count_30d"] = count

    # Add drilldown page URL
    for violation in violations_map.values():
        code = violation["violation_code"]
        encoded_code = quote(code, safe="")
        violation["drilldown_url"] = f"../webproof/violations/{encoded_code}.html"

    # Convert to list and sort by total count (7d + 30d)
    violations_list = list(violations_map.values())
    violations_list.sort(key=lambda x: x["count_7d"] + x["count_30d"], reverse=True)

    return violations_list


def generate_violations_browser() -> dict:
    """Generate unified violations browser JSON."""
    violations = extract_all_violations()

    # Extract unique tools and rings for filter options
    tools = sorted(set(v["tool"] for v in violations if v["tool"] != "unknown"))
    rings = sorted(set(v["ring"] for v in violations if v["ring"] != "unknown"))

    browser_data = {
        "episode": "E89",
        "schema": "violations_browser_v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "violations": violations,
        "filters": {
            "tools": tools,
            "rings": rings,
        },
        "stats": {
            "total_violations": len(violations),
            "total_count_7d": sum(v["count_7d"] for v in violations),
            "total_count_30d": sum(v["count_30d"] for v in violations),
        },
        "source_exports": {
            "compliance_summary.json": load_json_file(CONTROL_PLANE_DIR / "compliance_summary.json") is not None,
            "top_violations_7d.json": load_json_file(CONTROL_PLANE_DIR / "top_violations_7d.json") is not None,
            "top_violations_30d.json": load_json_file(CONTROL_PLANE_DIR / "top_violations_30d.json") is not None,
        },
    }

    return browser_data


def main() -> int:
    """Generate violations_browser.json."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        browser_data = generate_violations_browser()
        output_path = OUTPUT_DIR / "violations_browser.json"

        with output_path.open("w") as f:
            json.dump(browser_data, f, indent=2)

        print(f"[generate_violations_browser] Wrote {output_path}")
        print(f"[generate_violations_browser] {len(browser_data['violations'])} violations")
        return 0
    except Exception as e:
        print(f"ERROR: Failed to generate violations browser: {e}", file=sys.stderr)
        error_summary = {
            "episode": "E89",
            "schema": "violations_browser_v1",
            "generated_at": datetime.now(UTC).isoformat(),
            "ok": False,
            "error": str(e),
            "violations": [],
            "filters": {"tools": [], "rings": []},
            "stats": {"total_violations": 0, "total_count_7d": 0, "total_count_30d": 0},
        }
        output_path = OUTPUT_DIR / "violations_browser.json"
        with output_path.open("w") as f:
            json.dump(error_summary, f, indent=2)
        return 1


if __name__ == "__main__":
    sys.exit(main())
