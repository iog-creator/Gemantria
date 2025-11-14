#!/usr/bin/env python3
"""
Control Plane Schema Introspection

Phase-3B Feature #8: DDL/schema introspection for control-plane tables.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

from agentpm.db.loader import DbDriverMissingError, DbUnavailableError, get_control_engine
from scripts.guards.guard_db_health import check_db_health


# Target control-plane tables to inspect
CONTROL_TABLES = [
    ("control", "agent_run"),
    ("control", "tool_catalog"),
    ("control", "capability_rule"),
    ("control", "doc_fragment"),
    ("control", "capability_session"),
    ("public", "ai_interactions"),
    ("public", "governance_artifacts"),
]


def compute_control_schema() -> dict[str, Any]:
    """
    Introspect control-plane table schemas (DDL).

    Returns:
        Dictionary with schema information:
        {
            "ok": bool,
            "mode": "db_on" | "db_off",
            "reason": str | None,
            "tables": {
                "<schema>.<table>": {
                    "columns": [
                        {
                            "name": str,
                            "data_type": str,
                            "is_nullable": bool,
                            "default": str | None,
                        },
                        ...
                    ],
                    "primary_key": [str, ...],  # column names
                    "indexes": [
                        {
                            "name": str,
                            "columns": [str, ...],
                            "unique": bool,
                        },
                        ...
                    ],
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
        return result

    # DB is ready, introspect tables
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
            # Introspect each table
            for schema, table in CONTROL_TABLES:
                table_key = f"{schema}.{table}"
                table_info: dict[str, Any] = {
                    "columns": [],
                    "primary_key": [],
                    "indexes": [],
                }

                try:
                    # Check if table exists first
                    exists_query = text(
                        """
                        SELECT EXISTS (
                            SELECT 1
                            FROM information_schema.tables
                            WHERE table_schema = :schema
                            AND table_name = :table
                        )
                        """
                    )
                    exists_result = conn.execute(exists_query, {"schema": schema, "table": table})
                    if not exists_result.scalar():
                        # Table doesn't exist, skip it
                        continue

                    # Get columns
                    columns_query = text(
                        """
                        SELECT
                            column_name,
                            data_type,
                            is_nullable,
                            column_default
                        FROM information_schema.columns
                        WHERE table_schema = :schema
                        AND table_name = :table
                        ORDER BY ordinal_position
                        """
                    )
                    columns_result = conn.execute(columns_query, {"schema": schema, "table": table})
                    for col_name, data_type, is_nullable, col_default in columns_result:
                        table_info["columns"].append(
                            {
                                "name": col_name,
                                "data_type": data_type,
                                "is_nullable": is_nullable == "YES",
                                "default": str(col_default) if col_default else None,
                            }
                        )

                    # Get primary key columns
                    pk_query = text(
                        """
                        SELECT
                            a.attname
                        FROM pg_index i
                        JOIN pg_class c ON c.oid = i.indrelid
                        JOIN pg_namespace n ON n.oid = c.relnamespace
                        JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
                        WHERE n.nspname = :schema
                        AND c.relname = :table
                        AND i.indisprimary
                        ORDER BY a.attnum
                        """
                    )
                    pk_result = conn.execute(pk_query, {"schema": schema, "table": table})
                    for (col_name,) in pk_result:
                        table_info["primary_key"].append(col_name)

                    # Get indexes (excluding primary key)
                    indexes_query = text(
                        """
                        SELECT
                            i.relname AS index_name,
                            a.attname AS column_name,
                            ix.indisunique AS is_unique
                        FROM pg_index ix
                        JOIN pg_class i ON i.oid = ix.indexrelid
                        JOIN pg_class t ON t.oid = ix.indrelid
                        JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
                        JOIN pg_namespace n ON n.oid = t.relnamespace
                        WHERE n.nspname = :schema
                        AND t.relname = :table
                        AND NOT ix.indisprimary
                        ORDER BY i.relname, a.attnum
                        """
                    )
                    indexes_result = conn.execute(indexes_query, {"schema": schema, "table": table})
                    # Group indexes by name
                    index_map: dict[str, dict[str, Any]] = {}
                    for index_name, column_name, is_unique in indexes_result:
                        if index_name not in index_map:
                            index_map[index_name] = {
                                "name": index_name,
                                "columns": [],
                                "unique": is_unique,
                            }
                        index_map[index_name]["columns"].append(column_name)
                    table_info["indexes"] = list(index_map.values())

                except ProgrammingError as e:
                    # Table doesn't exist or schema error - skip it
                    if "does not exist" in str(e) or "relation" in str(e).lower():
                        continue
                    # Other error - include table with empty schema
                    pass
                except Exception as e:
                    # Unexpected error - include table with empty schema
                    pass

                # Only add table if it exists (has columns)
                if table_info["columns"]:
                    result["tables"][table_key] = table_info

    except OperationalError as e:
        result["ok"] = False
        result["mode"] = "db_off"
        result["reason"] = f"Connection error: {e}"
    except Exception as e:
        result["ok"] = False
        result["mode"] = "db_off"
        result["reason"] = f"Unexpected error: {e}"

    return result


def print_human_summary(schema: dict[str, Any]) -> str:
    """
    Print human-readable summary of control schema.

    Args:
        schema: Control schema dictionary from compute_control_schema().

    Returns:
        Human-readable summary string.
    """
    mode = schema.get("mode", "unknown")
    reason = schema.get("reason")

    if mode != "db_on":
        error_msg = f" ({reason[:50]})" if reason else ""
        return f"CONTROL_SCHEMA: mode={mode}{error_msg}"

    # Count tables and columns
    tables = schema.get("tables", {})
    total_tables = len(tables)
    total_columns = sum(len(t.get("columns", [])) for t in tables.values())

    return f"CONTROL_SCHEMA: mode=db_on tables={total_tables} columns={total_columns}"
