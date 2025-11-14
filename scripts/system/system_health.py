#!/usr/bin/env python3
"""
Phase-3B Feature #3: System health aggregate.

Aggregates DB health, LM health, and graph overview into a single JSON + human-readable summary.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def _run_component(command: list[str], component_name: str) -> dict:
    """
    Run a component health check and parse JSON output.

    Args:
        command: Command to run (list of strings)
        component_name: Name of component (for error messages)

    Returns:
        Dictionary with component health status, or fallback dict if parsing fails
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,  # Don't raise on non-zero exit
        )

        # Try to parse JSON from stdout
        if result.stdout:
            try:
                data = json.loads(result.stdout)
                return data
            except json.JSONDecodeError:
                # Malformed JSON - return fallback
                return {
                    "ok": False,
                    "mode": "unknown",
                    "details": {
                        "errors": [f"malformed or missing JSON from {component_name}"],
                    },
                }

        # No stdout - return fallback
        return {
            "ok": False,
            "mode": "unknown",
            "details": {
                "errors": [f"no output from {component_name}"],
            },
        }

    except Exception as e:
        # Unexpected error - return fallback
        return {
            "ok": False,
            "mode": "unknown",
            "details": {
                "errors": [f"error running {component_name}: {e}"],
            },
        }


def _extract_reason(component_json: dict) -> str:
    """
    Extract a short reason string from component JSON.

    Args:
        component_json: Component health JSON

    Returns:
        Short reason string
    """
    mode = component_json.get("mode", "unknown")
    ok = component_json.get("ok", False)

    if ok and mode in ("ready", "lm_ready", "db_on"):
        return "ok"

    # Try to get first error
    errors = component_json.get("details", {}).get("errors", [])
    if errors:
        first_error = errors[0]
        # Extract error type (before colon) or use first 50 chars
        if ":" in first_error:
            error_type = first_error.split(":")[0]
            # Make it more readable
            error_type = error_type.replace("_", " ")
            return error_type[:50]
        return first_error[:50]

    # Fallback to mode or reason
    reason = component_json.get("reason")
    if reason:
        return reason[:50]

    return mode


def compute_system_health() -> dict:
    """
    Compute system health by aggregating DB, LM, and graph health.

    Returns:
        Dictionary with aggregated health status:
        {
            "ok": bool,  # true only if all components are ok/ready
            "components": {
                "db": <db_json>,
                "lm": <lm_json>,
                "graph": <graph_json>
            }
        }
    """
    # Run all three components
    db_health = _run_component(
        ["python", "-m", "scripts.guards.guard_db_health"],
        "db_health",
    )
    lm_health = _run_component(
        ["python", "-m", "scripts.guards.guard_lm_health"],
        "lm_health",
    )
    graph_overview = _run_component(
        ["python", "-m", "scripts.graph.graph_overview"],
        "graph_overview",
    )

    # Determine overall health
    # All components must be healthy/ready for system to be ok
    db_ok = db_health.get("ok", False) and db_health.get("mode") == "ready"
    lm_ok = lm_health.get("ok", False) and lm_health.get("mode") == "lm_ready"
    graph_ok = graph_overview.get("ok", False) and graph_overview.get("mode") == "db_on"

    system_ok = db_ok and lm_ok and graph_ok

    return {
        "ok": system_ok,
        "components": {
            "db": db_health,
            "lm": lm_health,
            "graph": graph_overview,
        },
    }


def print_human_summary(health: dict) -> str:
    """
    Generate human-readable summary from system health JSON.

    Args:
        health: Dictionary from compute_system_health()

    Returns:
        Multi-line summary string
    """
    components = health.get("components", {})
    db = components.get("db", {})
    lm = components.get("lm", {})
    graph = components.get("graph", {})

    db_mode = db.get("mode", "unknown")
    db_reason = _extract_reason(db)

    lm_mode = lm.get("mode", "unknown")
    lm_reason = _extract_reason(lm)

    graph_mode = graph.get("mode", "unknown")
    graph_reason = _extract_reason(graph)

    lines = [
        "SYSTEM_HEALTH:",
        f"  DB_HEALTH:   mode={db_mode} ({db_reason})",
        f"  LM_HEALTH:   mode={lm_mode} ({lm_reason})",
        f"  GRAPH_OVERVIEW: mode={graph_mode} ({graph_reason})",
    ]

    return "\n".join(lines)


def main() -> int:
    """Main entry point."""
    health = compute_system_health()

    # Print JSON to stdout
    print(json.dumps(health, indent=2))

    # Print human-readable summary to stderr (so JSON can be piped)
    summary = print_human_summary(health)
    print(summary, file=sys.stderr)

    # Always exit 0 (hermetic, safe when DB and LM are both off)
    return 0


if __name__ == "__main__":
    sys.exit(main())
