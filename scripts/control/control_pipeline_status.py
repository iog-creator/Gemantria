#!/usr/bin/env python3
"""
Control Plane Pipeline Status

Phase-3B Feature #9: Summarize recent pipeline runs from control.agent_run table.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

from agentpm.db.loader import DbDriverMissingError, DbUnavailableError, get_control_engine
from scripts.guards.guard_db_health import check_db_health


def compute_control_pipeline_status(window_hours: int = 24) -> dict[str, Any]:
    """
    Compute control-plane pipeline status summary from agent_run table.

    Args:
        window_hours: Time window in hours to query (default: 24).

    Returns:
        Dictionary with pipeline status:
        {
            "ok": bool,
            "mode": "db_on" | "db_off",
            "reason": str | None,
            "window_hours": int,
            "summary": {
                "total_runs": int,
                "pipelines": {
                    "<pipeline_name>": {
                        "total": int,
                        "by_status": {
                            "success": int,
                            "failed": int,
                            "running": int,
                            "other": int,
                        },
                        "last_run_started_at": str | None,  # RFC3339
                        "last_run_status": str | None,
                    },
                    ...
                },
            },
        }
    """
    result: dict[str, Any] = {
        "ok": False,
        "mode": "db_off",
        "reason": None,
        "window_hours": window_hours,
        "summary": {
            "total_runs": 0,
            "pipelines": {},
        },
    }

    # First check DB health
    db_health = check_db_health()
    if not db_health.get("ok") or db_health.get("mode") != "ready":
        mode = db_health.get("mode", "db_off")
        errors = db_health.get("details", {}).get("errors", [])
        reason = errors[0] if errors else f"Database not ready (mode={mode})"
        result["mode"] = mode
        result["reason"] = reason
        return result

    # DB is ready, query agent_run table
    result["ok"] = True
    result["mode"] = "db_on"
    result["reason"] = None

    try:
        engine = get_control_engine()
    except (DbDriverMissingError, DbUnavailableError) as e:
        result["ok"] = False
        result["mode"] = "db_off"
        result["reason"] = str(e)
        return result

    try:
        with engine.connect() as conn:
            # Query agent_run for the last N hours, grouped by tool (pipeline name)
            # Status determination:
            # - success: violations_json is empty array '[]' or null
            # - failed: violations_json is non-empty array
            # - running: result_json indicates running state (for now, treat as "other")
            # - other: everything else

            query = text(
                """
                SELECT
                    tool AS pipeline_name,
                    COUNT(*) AS total,
                    COUNT(*) FILTER (WHERE violations_json = '[]'::jsonb OR violations_json IS NULL) AS success_count,
                    COUNT(*) FILTER (WHERE violations_json != '[]'::jsonb AND violations_json IS NOT NULL) AS failed_count,
                    MAX(created_at) AS last_run_started_at
                FROM control.agent_run
                WHERE created_at >= NOW() - INTERVAL ':window_hours hours'
                GROUP BY tool
                ORDER BY tool
                """
            )

            result_set = conn.execute(query, {"window_hours": window_hours})
            rows = result_set.fetchall()

            total_runs = 0
            pipelines: dict[str, Any] = {}

            for pipeline_name, total, success_count, failed_count, last_run_started_at in rows:
                total_runs += total
                success = int(success_count) if success_count else 0
                failed = int(failed_count) if failed_count else 0
                other = total - success - failed  # For now, no "running" status detection

                # Get last run status
                last_status = None
                if last_run_started_at:
                    # Query the most recent run for this pipeline to get its status
                    status_query = text(
                        """
                        SELECT violations_json
                        FROM control.agent_run
                        WHERE tool = :pipeline_name
                        AND created_at = :last_run_started_at
                        ORDER BY created_at DESC
                        LIMIT 1
                        """
                    )
                    status_result = conn.execute(
                        status_query,
                        {
                            "pipeline_name": pipeline_name,
                            "last_run_started_at": last_run_started_at,
                        },
                    )
                    status_row = status_result.fetchone()
                    if status_row:
                        violations = status_row[0]
                        if violations is None or violations == []:
                            last_status = "success"
                        else:
                            last_status = "failed"

                # Format last_run_started_at as RFC3339
                last_run_iso = None
                if last_run_started_at:
                    if isinstance(last_run_started_at, datetime):
                        last_run_iso = last_run_started_at.isoformat()
                    else:
                        last_run_iso = str(last_run_started_at)

                pipelines[pipeline_name] = {
                    "total": int(total),
                    "by_status": {
                        "success": success,
                        "failed": failed,
                        "running": 0,  # Not yet implemented
                        "other": other,
                    },
                    "last_run_started_at": last_run_iso,
                    "last_run_status": last_status,
                }

            result["summary"]["total_runs"] = total_runs
            result["summary"]["pipelines"] = pipelines

    except ProgrammingError as e:
        # Table doesn't exist or query failed
        result["ok"] = False
        result["mode"] = "db_off"
        result["reason"] = f"Query failed: {e}"
    except OperationalError as e:
        # Connection error
        result["ok"] = False
        result["mode"] = "db_off"
        result["reason"] = f"Connection error: {e}"
    except Exception as e:
        # Unexpected error
        result["ok"] = False
        result["mode"] = "db_off"
        result["reason"] = f"Unexpected error: {e}"

    return result


def print_human_summary(status: dict[str, Any]) -> str:
    """
    Print human-readable summary of pipeline status.

    Args:
        status: Pipeline status dictionary from compute_control_pipeline_status().

    Returns:
        Human-readable summary string.
    """
    mode = status.get("mode", "unknown")
    reason = status.get("reason")
    window_hours = status.get("window_hours", 24)
    summary = status.get("summary", {})
    total_runs = summary.get("total_runs", 0)
    pipelines = summary.get("pipelines", {})

    if mode != "db_on":
        error_msg = f" ({reason[:50]})" if reason else ""
        return f"CONTROL_PIPELINE_STATUS: mode={mode} window_hours={window_hours}{error_msg}"

    # Build pipeline summary
    pipeline_parts = []
    for pipeline_name, info in pipelines.items():
        total = info.get("total", 0)
        by_status = info.get("by_status", {})
        success = by_status.get("success", 0)
        failed = by_status.get("failed", 0)
        pipeline_parts.append(f"{pipeline_name}({total}:{success}s/{failed}f)")

    pipelines_str = ",".join(pipeline_parts) if pipeline_parts else "none"
    return f"CONTROL_PIPELINE_STATUS: mode=db_on window_hours={window_hours} total_runs={total_runs} pipelines={pipelines_str}"
