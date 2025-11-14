#!/usr/bin/env python3
"""
Export graph compliance metrics for E90.

Combines control-plane compliance data with graph stats to produce
metrics per node, pattern, tool, and extraction batch.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, UTC
from pathlib import Path

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


def get_graph_stats() -> dict | None:
    """Load graph stats if available."""
    # Try multiple possible locations
    possible_paths = [
        REPO / "exports" / "graph_stats.json",
        REPO / "share" / "exports" / "graph_stats.json",
        CONTROL_PLANE_DIR / "graph_stats.json",
    ]
    for path in possible_paths:
        data = load_json_file(path)
        if data:
            return data
    return None


def generate_graph_compliance_metrics() -> dict:
    """Generate graph compliance metrics combining control-plane and graph data."""
    # Load compliance exports
    compliance_summary = load_json_file(CONTROL_PLANE_DIR / "compliance_summary.json")
    violations_7d = load_json_file(CONTROL_PLANE_DIR / "top_violations_7d.json")
    violations_30d = load_json_file(CONTROL_PLANE_DIR / "top_violations_30d.json")

    # Load graph stats
    graph_stats = get_graph_stats()

    # Initialize summary
    summary = {
        "nodes": 0,
        "patterns": 0,
        "tools": 0,
        "batches": 0,
    }

    # Extract node count from graph stats
    if graph_stats:
        if isinstance(graph_stats, dict):
            # Try various possible keys
            summary["nodes"] = (
                graph_stats.get("total_nodes", 0)
                or graph_stats.get("nodes", 0)
                or graph_stats.get("node_count", 0)
                or len(graph_stats.get("nodes", []))
            )
            summary["patterns"] = (
                graph_stats.get("total_patterns", 0)
                or graph_stats.get("patterns", 0)
                or graph_stats.get("pattern_count", 0)
                or len(graph_stats.get("patterns", []))
            )

    # Extract tool counts from compliance data
    if compliance_summary and compliance_summary.get("metrics"):
        violations_by_tool = compliance_summary["metrics"].get("violations_by_tool", {})
        if isinstance(violations_by_tool, dict):
            summary["tools"] = len(violations_by_tool)

    # Extract batch info (placeholder - would need actual batch tracking)
    # For now, use violation counts as proxy
    if violations_7d and violations_7d.get("violations"):
        violations = violations_7d["violations"]
        if isinstance(violations, list):
            summary["batches"] = len(violations)
        elif isinstance(violations, dict):
            summary["batches"] = len(violations)

    # Build details (placeholder structure for future expansion)
    details = []

    # Build export
    export_data = {
        "episode": "E90",
        "schema": "graph_compliance_v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "summary": summary,
        "details": details,
        "source_exports": {
            "compliance_summary.json": compliance_summary is not None,
            "top_violations_7d.json": violations_7d is not None,
            "top_violations_30d.json": violations_30d is not None,
            "graph_stats.json": graph_stats is not None,
        },
    }

    return export_data


def main() -> int:
    """Generate graph_compliance.json."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        export_data = generate_graph_compliance_metrics()
        output_path = OUTPUT_DIR / "graph_compliance.json"

        with output_path.open("w") as f:
            json.dump(export_data, f, indent=2)

        print(f"[control_graph_compliance_metrics_export] Wrote {output_path}")
        print(
            f"[control_graph_compliance_metrics_export] Summary: nodes={export_data['summary']['nodes']}, "
            f"patterns={export_data['summary']['patterns']}, tools={export_data['summary']['tools']}, "
            f"batches={export_data['summary']['batches']}"
        )
        return 0
    except Exception as e:
        print(f"ERROR: Failed to generate graph compliance metrics: {e}", file=sys.stderr)
        error_summary = {
            "episode": "E90",
            "schema": "graph_compliance_v1",
            "generated_at": datetime.now(UTC).isoformat(),
            "ok": False,
            "error": str(e),
            "summary": {"nodes": 0, "patterns": 0, "tools": 0, "batches": 0},
            "details": [],
        }
        output_path = OUTPUT_DIR / "graph_compliance.json"
        with output_path.open("w") as f:
            json.dump(error_summary, f, indent=2)
        return 1


if __name__ == "__main__":
    sys.exit(main())
