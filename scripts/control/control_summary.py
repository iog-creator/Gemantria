#!/usr/bin/env python3
"""
Control Plane Summary

Phase-3B Consolidation: Aggregated control-plane summary combining status, tables, schema, and pipeline-status.
"""

from __future__ import annotations

from datetime import datetime, UTC
from typing import Any

from scripts.control.control_pipeline_status import compute_control_pipeline_status
from scripts.control.control_schema import compute_control_schema
from scripts.control.control_status import compute_control_status
from scripts.control.control_tables import compute_control_tables


def compute_control_summary() -> dict[str, Any]:
    """
    Compute aggregated control-plane summary from all control components.

    Returns:
        Dictionary with aggregated summary:
        {
            "ok": bool,  # true only if all subcomponents that reached db_on are ok
            "generated_at": str,  # RFC3339 timestamp
            "components": {
                "status": dict,  # from control status helper
                "tables": dict,  # from control tables helper
                "schema": dict,  # from control schema helper
                "pipeline_status": dict,  # from control pipeline-status helper
            },
        }
    """
    result: dict[str, Any] = {
        "ok": False,
        "generated_at": datetime.now(UTC).isoformat(),
        "components": {},
    }

    # Collect all component results
    components: dict[str, Any] = {}

    # 1. Control status
    try:
        status_result = compute_control_status()
        components["status"] = status_result
    except Exception as e:
        components["status"] = {
            "ok": False,
            "mode": "error",
            "reason": f"Exception: {e}",
            "tables": {},
        }

    # 2. Control tables
    try:
        tables_result = compute_control_tables()
        components["tables"] = tables_result
    except Exception as e:
        components["tables"] = {
            "ok": False,
            "mode": "error",
            "error": f"Exception: {e}",
            "tables": {},
        }

    # 3. Control schema
    try:
        schema_result = compute_control_schema()
        components["schema"] = schema_result
    except Exception as e:
        components["schema"] = {
            "ok": False,
            "mode": "error",
            "reason": f"Exception: {e}",
            "tables": {},
        }

    # 4. Control pipeline status
    try:
        pipeline_result = compute_control_pipeline_status()
        components["pipeline_status"] = pipeline_result
    except Exception as e:
        components["pipeline_status"] = {
            "ok": False,
            "mode": "error",
            "reason": f"Exception: {e}",
            "window_hours": 24,
            "summary": {
                "total_runs": 0,
                "pipelines": {},
            },
        }

    result["components"] = components

    # Determine overall "ok" status conservatively:
    # - ok=true only if all components that have an "ok" field return ok=true
    # - Components in db_off mode are acceptable (they return ok=false but mode=db_off)
    # - Components with mode="error" indicate exceptions and should make overall ok=false
    all_ok = True
    has_db_on_component = False

    for component_name, component_data in components.items():
        if not isinstance(component_data, dict):
            all_ok = False
            continue

        component_ok = component_data.get("ok", False)
        component_mode = component_data.get("mode", "unknown")

        # If component reached db_on, it must be ok
        if component_mode == "db_on":
            has_db_on_component = True
            if not component_ok:
                all_ok = False

        # If component had an error (exception), overall is not ok
        if component_mode == "error":
            all_ok = False

    # If we have db_on components, all must be ok
    # If all are db_off, that's acceptable (hermetic behavior)
    if has_db_on_component:
        result["ok"] = all_ok
    else:
        # All components are db_off or error - acceptable for hermetic behavior
        # but overall ok=false if any had errors
        result["ok"] = not any(
            comp.get("mode") == "error" for comp in components.values() if isinstance(comp, dict)
        )

    return result


def print_human_summary(summary: dict[str, Any]) -> str:
    """
    Print human-readable summary of control summary.

    Args:
        summary: Control summary dictionary from compute_control_summary().

    Returns:
        Human-readable summary string.
    """
    ok = summary.get("ok", False)
    return f"CONTROL_SUMMARY: ok={str(ok).lower()}"
