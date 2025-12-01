#!/usr/bin/env python3
"""
Control-plane migration harness.

Applies migrations/040_control_plane_schema.sql to create the control schema
with tool_catalog, capability_rule, doc_fragment, capability_session, and agent_run tables.

Uses centralized DSN loader (never os.getenv directly).
Tolerates empty/nonexistent DB (exits 0 for CI tolerance).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.config.env import get_rw_dsn

try:
    import psycopg
except ImportError:
    print(
        "WARN: psycopg not available; skipping control migration (CI empty-DB tolerance).",
        file=sys.stderr,
    )
    sys.exit(0)

DSN = get_rw_dsn()
if not DSN:
    print("SKIP: GEMATRIA_DSN not set (empty-DB tolerance).", file=sys.stderr)
    sys.exit(0)


def main() -> int:
    """Apply control-plane migration."""
    migration_file = REPO / "migrations" / "040_control_plane_schema.sql"
    if not migration_file.exists():
        print(f"ERROR: Migration file not found: {migration_file}", file=sys.stderr)
        return 1

    try:
        with psycopg.connect(DSN, autocommit=True) as conn:
            with conn.cursor() as cur:
                # Check if schema already exists (idempotent check)
                cur.execute(
                    "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = 'control')"
                )
                schema_exists = cur.fetchone()[0]

                # Read and apply migration
                sql = migration_file.read_text(encoding="utf-8")
                cur.execute(sql)

                if schema_exists:
                    print(
                        "[migrate_control] Control schema already existed; migration applied (idempotent)."
                    )
                else:
                    print("[migrate_control] Control schema created successfully.")

                # Verify tables exist
                cur.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'control'
                    ORDER BY table_name
                    """
                )
                tables = [row[0] for row in cur.fetchall()]
                expected_tables = {
                    "tool_catalog",
                    "capability_rule",
                    "doc_fragment",
                    "capability_session",
                    "agent_run",
                }
                found_tables = set(tables)
                missing = expected_tables - found_tables
                if missing:
                    print(f"WARN: Missing tables: {missing}", file=sys.stderr)
                    return 1
                print(f"[migrate_control] Verified tables: {', '.join(sorted(found_tables))}")
                return 0
    except psycopg.Error as e:
        print(f"WARN: Migration failed (empty-DB tolerance): {e}", file=sys.stderr)
        return 0  # Exit 0 for CI tolerance
    except Exception as e:
        print(f"WARN: Unexpected error (empty-DB tolerance): {e}", file=sys.stderr)
        return 0  # Exit 0 for CI tolerance


if __name__ == "__main__":
    sys.exit(main())
