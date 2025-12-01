#!/usr/bin/env python3
"""
Control-plane schema snapshot generator.

Introspects the control schema tables and emits a JSON snapshot to
share/schema_snapshot.json.

Uses centralized DSN loader (never os.getenv directly).
Tolerates empty/nonexistent DB (exits 0, writes empty snapshot for CI tolerance).
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, UTC
from pathlib import Path

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.config.env import get_rw_dsn

try:
    import psycopg
except ImportError:
    print(
        "WARN: psycopg not available; skipping schema snapshot (CI empty-DB tolerance).",
        file=sys.stderr,
    )
    # Write empty snapshot for CI tolerance
    output_file = REPO / "share" / "schema_snapshot.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        json.dumps(
            {
                "schema": "control",
                "generated_at": datetime.now(UTC).isoformat(),
                "tables": [],
                "error": "psycopg not available",
            },
            indent=2,
        )
    )
    sys.exit(0)

DSN = get_rw_dsn()
if not DSN:
    print("SKIP: GEMATRIA_DSN not set (empty-DB tolerance).", file=sys.stderr)
    # Write empty snapshot for CI tolerance
    output_file = REPO / "share" / "schema_snapshot.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        json.dumps(
            {
                "schema": "control",
                "generated_at": datetime.now(UTC).isoformat(),
                "tables": [],
                "error": "DSN not set",
            },
            indent=2,
        )
    )
    sys.exit(0)


def get_table_info(cur: psycopg.Cursor, table_name: str) -> dict:
    """Get table schema information."""
    # Get columns
    cur.execute(
        """
        SELECT
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = 'control' AND table_name = %s
        ORDER BY ordinal_position
        """,
        (table_name,),
    )
    columns = [
        {
            "name": row[0],
            "type": row[1],
            "nullable": row[2] == "YES",
            "default": row[3],
        }
        for row in cur.fetchall()
    ]

    # Get primary key
    cur.execute(
        """
        SELECT a.attname
        FROM pg_index i
        JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
        WHERE i.indrelid = ('control.' || %s)::regclass
          AND i.indisprimary
        ORDER BY a.attnum
        """,
        (table_name,),
    )
    primary_key = [row[0] for row in cur.fetchall()]

    # Get indexes (non-primary)
    cur.execute(
        """
        SELECT
            i.relname AS index_name,
            array_agg(a.attname ORDER BY a.attnum) AS columns
        FROM pg_index idx
        JOIN pg_class i ON i.oid = idx.indexrelid
        JOIN pg_class t ON t.oid = idx.indrelid
        JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(idx.indkey)
        WHERE t.relname = %s
          AND t.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'control')
          AND NOT idx.indisprimary
        GROUP BY i.relname
        ORDER BY i.relname
        """,
        (table_name,),
    )
    indexes = [{"name": row[0], "columns": row[1]} for row in cur.fetchall()]

    # Get foreign keys
    cur.execute(
        """
        SELECT
            tc.constraint_name,
            kcu.column_name,
            ccu.table_schema || '.' || ccu.table_name AS foreign_table,
            ccu.column_name AS foreign_column
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
          AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
          ON ccu.constraint_name = tc.constraint_name
          AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_schema = 'control'
          AND tc.table_name = %s
        """,
        (table_name,),
    )
    foreign_keys = [
        {
            "constraint": row[0],
            "column": row[1],
            "references": row[2],
            "referenced_column": row[3],
        }
        for row in cur.fetchall()
    ]

    return {
        "name": table_name,
        "columns": columns,
        "primary_key": primary_key,
        "indexes": indexes,
        "foreign_keys": foreign_keys,
    }


def main() -> int:
    """Generate schema snapshot."""
    output_file = REPO / "share" / "schema_snapshot.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        with psycopg.connect(DSN, autocommit=True) as conn:
            with conn.cursor() as cur:
                # Check if schema exists
                cur.execute("SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = 'control')")
                schema_exists = cur.fetchone()[0]

                if not schema_exists:
                    print(
                        "WARN: Control schema does not exist; writing empty snapshot.",
                        file=sys.stderr,
                    )
                    snapshot = {
                        "schema": "control",
                        "generated_at": datetime.now(UTC).isoformat(),
                        "tables": [],
                        "error": "Schema does not exist",
                    }
                    output_file.write_text(json.dumps(snapshot, indent=2))
                    return 0

                # Get all tables in control schema
                cur.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'control'
                      AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                    """
                )
                table_names = [row[0] for row in cur.fetchall()]

                # Get info for each table
                tables = []
                for table_name in table_names:
                    try:
                        table_info = get_table_info(cur, table_name)
                        tables.append(table_info)
                    except Exception as e:
                        print(f"WARN: Failed to introspect table {table_name}: {e}", file=sys.stderr)
                        tables.append({"name": table_name, "error": str(e)})

                snapshot = {
                    "schema": "control",
                    "generated_at": datetime.now(UTC).isoformat(),
                    "tables": tables,
                }

                output_file.write_text(json.dumps(snapshot, indent=2))
                print(f"[control_schema_snapshot] Wrote snapshot to {output_file}")
                print(f"[control_schema_snapshot] Found {len(tables)} tables: {', '.join(t['name'] for t in tables)}")
                return 0

    except psycopg.Error as e:
        print(f"ERROR: Database error: {e}", file=sys.stderr)
        # Write error snapshot for CI tolerance
        snapshot = {
            "schema": "control",
            "generated_at": datetime.now(UTC).isoformat(),
            "tables": [],
            "error": str(e),
        }
        output_file.write_text(json.dumps(snapshot, indent=2))
        return 0  # Exit 0 for CI tolerance
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        snapshot = {
            "schema": "control",
            "generated_at": datetime.now(UTC).isoformat(),
            "tables": [],
            "error": str(e),
        }
        output_file.write_text(json.dumps(snapshot, indent=2))
        return 0  # Exit 0 for CI tolerance


if __name__ == "__main__":
    sys.exit(main())
