#!/usr/bin/env python3
"""
DMS Table Exports for PM Share Package

Exports full table dumps (all columns, all rows) for DMS tables:
- control.doc_registry
- control.doc_version
- control.doc_sync_state
- control.hint_registry

Uses centralized DSN loader (never os.getenv directly).
Tolerates empty/nonexistent DB (exits 0, writes empty exports for CI tolerance).
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.config.env import get_rw_dsn

try:
    import psycopg
except ImportError:
    psycopg = None

OUT_DIR = REPO / "share"

TABLES = [
    "control.doc_registry",
    "control.doc_version",
    "control.doc_sync_state",
    "control.hint_registry",
]


def now_iso() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now(UTC).isoformat()


def db_off_export(table_name: str, error: str) -> dict[str, Any]:
    """Generate empty export for DB-off scenarios."""
    return {
        "schema": f"{table_name}.v1",
        "generated_at": now_iso(),
        "table": table_name,
        "rows": [],
        "row_count": 0,
        "db_off": True,
        "error": error,
    }


def export_table(conn: psycopg.Connection, table_name: str) -> dict[str, Any]:
    """Export a single table as full dump (all columns, all rows)."""
    try:
        with conn.cursor() as cur:
            # Get all rows
            cur.execute(f"SELECT * FROM {table_name} ORDER BY 1")
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

            # Convert rows to dicts
            rows_dict = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    # Convert datetime/timestamp to ISO strings
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    # Convert UUID to string
                    elif hasattr(value, "hex"):  # UUID-like
                        value = str(value)
                    # Convert JSONB to dict
                    elif isinstance(value, dict):
                        value = value
                    row_dict[col] = value
                rows_dict.append(row_dict)

            return {
                "schema": f"{table_name}.v1",
                "generated_at": now_iso(),
                "table": table_name,
                "rows": rows_dict,
                "row_count": len(rows_dict),
                "db_off": False,
            }
    except Exception as exc:
        return db_off_export(table_name, f"database error: {exc!s}")


def main() -> int:
    """Main entrypoint."""
    # Ensure output directory exists
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if psycopg is None:
        print(
            "WARN: psycopg not available; writing empty exports (CI empty-DB tolerance).",
            file=sys.stderr,
        )
        for table_name in TABLES:
            output_file = OUT_DIR / f"{table_name.split('.')[-1]}.json"
            export_data = db_off_export(table_name, "psycopg not available")
            output_file.write_text(
                json.dumps(export_data, indent=2, default=str),
                encoding="utf-8",
            )
        return 0

    dsn = get_rw_dsn()
    if not dsn:
        print("SKIP: GEMATRIA_DSN not set (empty-DB tolerance).", file=sys.stderr)
        for table_name in TABLES:
            output_file = OUT_DIR / f"{table_name.split('.')[-1]}.json"
            export_data = db_off_export(table_name, "DSN not set")
            output_file.write_text(
                json.dumps(export_data, indent=2, default=str),
                encoding="utf-8",
            )
        return 0

    try:
        with psycopg.connect(dsn) as conn:
            for table_name in TABLES:
                export_data = export_table(conn, table_name)
                # Flat output: share/<table_name>.json
                output_file = OUT_DIR / f"{table_name.split('.')[-1]}.json"
                output_file.write_text(
                    json.dumps(export_data, indent=2, default=str),
                    encoding="utf-8",
                )
                print(f"✅ Exported {table_name}: {export_data['row_count']} rows")
    except Exception as exc:
        print(f"ERROR: Failed to export DMS tables: {exc}", file=sys.stderr)
        # Write empty exports for CI tolerance
        for table_name in TABLES:
            output_file = OUT_DIR / f"{table_name.split('.')[-1]}.json"
            export_data = db_off_export(table_name, f"connection error: {exc!s}")
            output_file.write_text(
                json.dumps(export_data, indent=2, default=str),
                encoding="utf-8",
            )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
