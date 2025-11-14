#!/usr/bin/env python3
"""
Control Plane Tables Listing

Phase-3B Feature #7: List all schema-qualified tables with row counts.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

from agentpm.db.loader import DbDriverMissingError, DbUnavailableError, get_control_engine
from scripts.guards.guard_db_health import check_db_health


def compute_control_tables() -> dict[str, Any]:
    """
    List all schema-qualified tables with row counts.

    Returns:
        Dictionary with tables listing:
        {
            "ok": bool,
            "mode": "db_on" | "db_off",
            "error": str | None,
            "tables": {
                "<schema>.<table>": int | None,  # row_count or None if query failed
                ...
            },
        }
    """
    result: dict[str, Any] = {
        "ok": False,
        "mode": "db_off",
        "error": None,
        "tables": {},
    }

    # First check DB health
    db_health = check_db_health()
    if not db_health.get("ok") or db_health.get("mode") != "ready":
        mode = db_health.get("mode", "db_off")
        errors = db_health.get("details", {}).get("errors", [])
        error_msg = errors[0] if errors else f"Database not ready (mode={mode})"
        result["mode"] = mode
        result["error"] = error_msg
        return result

    # DB is ready, query all tables
    result["ok"] = True
    result["mode"] = "db_on"
    result["error"] = None

    try:
        engine = get_control_engine()
    except (DbDriverMissingError, DbUnavailableError) as e:
        result["ok"] = False
        result["mode"] = "db_off"
        result["error"] = str(e)
        return result

    try:
        with engine.connect() as conn:
            # Query all base tables from information_schema
            query = text(
                """
                SELECT table_schema, table_name
                FROM information_schema.tables
                WHERE table_type = 'BASE TABLE'
                AND table_schema NOT IN ('pg_catalog', 'information_schema')
                ORDER BY table_schema, table_name
                """
            )
            result_set = conn.execute(query)
            rows = result_set.fetchall()

            # For each table, get row count
            for schema, table in rows:
                table_key = f"{schema}.{table}"
                try:
                    # Use parameterized query with quoted identifiers
                    count_query = text(f'SELECT COUNT(*) FROM "{schema}"."{table}"')
                    count_result = conn.execute(count_query)
                    row_count = count_result.scalar()
                    result["tables"][table_key] = int(row_count) if row_count is not None else 0
                except (ProgrammingError, OperationalError) as e:
                    # Table might not be accessible or query failed
                    result["tables"][table_key] = None
                except Exception as e:
                    # Unexpected error
                    result["tables"][table_key] = None

    except OperationalError as e:
        result["ok"] = False
        result["mode"] = "db_off"
        result["error"] = f"Connection error: {e}"
    except Exception as e:
        result["ok"] = False
        result["mode"] = "db_off"
        result["error"] = f"Unexpected error: {e}"

    return result


def print_human_summary(tables: dict[str, Any]) -> str:
    """
    Print human-readable summary of control tables.

    Args:
        tables: Control tables dictionary from compute_control_tables().

    Returns:
        Human-readable summary string.
    """
    mode = tables.get("mode", "unknown")
    error = tables.get("error")

    if mode != "db_on":
        error_msg = f" ({error[:50]})" if error else ""
        return f"CONTROL_TABLES: mode={mode}{error_msg}"

    # Count tables by schema
    table_data = tables.get("tables", {})
    schema_counts: dict[str, int] = {}
    total_tables = 0

    for table_key in table_data:
        schema = table_key.split(".")[0]
        schema_counts[schema] = schema_counts.get(schema, 0) + 1
        total_tables += 1

    schema_parts = [f"{schema}({count})" for schema, count in sorted(schema_counts.items())]
    schemas_str = ",".join(schema_parts) if schema_parts else "none"

    return f"CONTROL_TABLES: mode=db_on tables={total_tables} schemas={schemas_str}"
