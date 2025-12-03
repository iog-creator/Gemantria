#!/usr/bin/env python3
"""
Control Plane Status Check

Phase-3B Feature #6: Check control-plane database posture and table row counts.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

from pmagent.db.loader import DbDriverMissingError, DbUnavailableError, get_control_engine
from scripts.guards.guard_db_health import check_db_health


# Target control-plane tables to inspect
CONTROL_TABLES = [
    ("public", "ai_interactions"),
    ("public", "governance_artifacts"),
    ("control", "agent_run"),
    ("control", "agent_run_cli"),
    ("control", "kb_document"),
    ("control", "doc_registry"),
    ("control", "doc_version"),
    ("control", "tool_catalog"),
    ("gematria", "graph_stats_snapshots"),
]


def compute_control_status() -> dict[str, Any]:
    """
    Compute control-plane status with table row counts.

    Returns:
        Dictionary with status:
        {
            "ok": bool,
            "mode": "ready" | "db_off" | "partial",
            "reason": str | None,
            "tables": {
                "<schema>.<table>": {
                    "present": bool,
                    "row_count": int | None,
                    "latest_created_at": str | None,
                },
                ...
            },
        }
    """
    result: dict[str, Any] = {
        "ok": False,
        "mode": "db_off",
        "reason": None,
        "tables": {},
    }

    # First check DB health
    db_health = check_db_health()
    if not db_health.get("ok") or db_health.get("mode") != "ready":
        mode = db_health.get("mode", "db_off")
        errors = db_health.get("details", {}).get("errors", [])
        reason = errors[0] if errors else f"Database not ready (mode={mode})"
        result["mode"] = mode
        result["reason"] = reason
        # Initialize all tables as missing
        for schema, table in CONTROL_TABLES:
            table_key = f"{schema}.{table}"
            result["tables"][table_key] = {
                "present": False,
                "row_count": None,
                "latest_created_at": None,
            }
        return result

    # DB is ready, inspect tables
    result["ok"] = True
    result["mode"] = "ready"
    result["reason"] = None

    try:
        engine = get_control_engine()
    except (DbDriverMissingError, DbUnavailableError) as e:
        result["ok"] = False
        result["mode"] = "db_off"
        result["reason"] = str(e)
        # Initialize all tables as missing
        for schema, table in CONTROL_TABLES:
            table_key = f"{schema}.{table}"
            result["tables"][table_key] = {
                "present": False,
                "row_count": None,
                "latest_created_at": None,
            }
        return result

    # Query each table
    for schema, table in CONTROL_TABLES:
        table_key = f"{schema}.{table}"
        table_info: dict[str, Any] = {
            "present": False,
            "row_count": None,
            "latest_created_at": None,
        }

        try:
            with engine.connect() as conn:
                # Check if table exists and get row count
                count_query = text(f'SELECT COUNT(*) FROM "{schema}"."{table}"')
                count_result = conn.execute(count_query)
                row_count = count_result.scalar()
                table_info["present"] = True
                table_info["row_count"] = int(row_count) if row_count is not None else 0

                # Try to get latest created_at if the table has that column
                try:
                    latest_query = text(
                        f'SELECT MAX(created_at) FROM "{schema}"."{table}" WHERE created_at IS NOT NULL'
                    )
                    latest_result = conn.execute(latest_query)
                    latest_ts = latest_result.scalar()
                    if latest_ts:
                        # Convert to ISO 8601 string
                        if isinstance(latest_ts, datetime):
                            table_info["latest_created_at"] = latest_ts.isoformat()
                        else:
                            table_info["latest_created_at"] = str(latest_ts)
                except (ProgrammingError, OperationalError):
                    # Table doesn't have created_at column, that's fine
                    pass

        except ProgrammingError as e:
            # Table doesn't exist
            if "does not exist" in str(e) or "relation" in str(e).lower():
                table_info["present"] = False
            else:
                # Other schema error - mark as present but with error
                table_info["present"] = True
                table_info["row_count"] = None
        except OperationalError as e:
            # Connection error - should not happen if DB health passed, but handle gracefully
            result["ok"] = False
            result["mode"] = "db_off"
            result["reason"] = f"Connection error: {e}"
            table_info["present"] = False
        except Exception as e:
            # Unexpected error - mark table as present but with error
            table_info["present"] = True
            table_info["row_count"] = None

        result["tables"][table_key] = table_info

    return result


def print_human_summary(status: dict[str, Any]) -> str:
    """
    Print human-readable summary of control status.

    Args:
        status: Control status dictionary from compute_control_status().

    Returns:
        Human-readable summary string.
    """
    mode = status.get("mode", "unknown")
    reason = status.get("reason", "ok")

    if mode != "ready":
        return f"CONTROL_STATUS: mode={mode} ({reason[:50]})"

    # Build table summary
    table_parts = []
    tables = status.get("tables", {})
    for table_key, info in tables.items():
        if info.get("present"):
            count = info.get("row_count", 0)
            # Shorten table name for display (just table name, not schema.table)
            table_name = table_key.split(".")[-1]
            table_parts.append(f"{table_name}({count})")

    tables_str = ",".join(table_parts) if table_parts else "none"
    return f"CONTROL_STATUS: mode=ready tables={tables_str}"
