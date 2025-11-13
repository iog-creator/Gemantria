#!/usr/bin/env python3
"""
Control-plane materialized views schema snapshot generator.

Introspects the control schema materialized views (mv_compliance_7d, mv_compliance_30d)
and emits a JSON snapshot to share/atlas/control_plane/mv_schema.json.

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
        "WARN: psycopg not available; skipping MV schema snapshot (CI empty-DB tolerance).",
        file=sys.stderr,
    )
    # Write empty snapshot for CI tolerance
    output_file = REPO / "share" / "atlas" / "control_plane" / "mv_schema.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        json.dumps(
            {
                "schema": "control",
                "generated_at": datetime.now(UTC).isoformat(),
                "ok": False,
                "connection_ok": False,
                "materialized_views": [],
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
    output_file = REPO / "share" / "atlas" / "control_plane" / "mv_schema.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        json.dumps(
            {
                "schema": "control",
                "generated_at": datetime.now(UTC).isoformat(),
                "ok": False,
                "connection_ok": False,
                "materialized_views": [],
                "error": "DSN not set",
            },
            indent=2,
        )
    )
    sys.exit(0)


def get_mv_info(cur: psycopg.Cursor, mv_name: str) -> dict:
    """Get materialized view schema information."""
    # Get columns
    cur.execute(
        """
        SELECT
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'control' AND table_name = %s
        ORDER BY ordinal_position
        """,
        (mv_name,),
    )
    columns = [
        {
            "name": row[0],
            "type": row[1],
            "nullable": row[2] == "YES",
        }
        for row in cur.fetchall()
    ]

    return {
        "name": mv_name,
        "columns": columns,
    }


def main() -> int:
    """Generate MV schema snapshot."""
    output_file = REPO / "share" / "atlas" / "control_plane" / "mv_schema.json"
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
                        "ok": False,
                        "connection_ok": True,
                        "materialized_views": [],
                        "error": "Schema does not exist",
                    }
                    output_file.write_text(json.dumps(snapshot, indent=2))
                    return 0

                # Get all materialized views in control schema
                cur.execute(
                    """
                    SELECT matviewname
                    FROM pg_matviews
                    WHERE schemaname = 'control'
                    ORDER BY matviewname
                    """
                )
                mv_names = [row[0] for row in cur.fetchall()]

                # Filter to only the compliance MVs we care about
                target_mvs = ["mv_compliance_7d", "mv_compliance_30d"]
                mv_names = [name for name in mv_names if name in target_mvs]

                # Get info for each MV
                materialized_views = []
                for mv_name in mv_names:
                    try:
                        mv_info = get_mv_info(cur, mv_name)
                        materialized_views.append(mv_info)
                    except Exception as e:
                        print(f"WARN: Failed to introspect MV {mv_name}: {e}", file=sys.stderr)
                        materialized_views.append({"name": mv_name, "error": str(e)})

                snapshot = {
                    "schema": "control",
                    "generated_at": datetime.now(UTC).isoformat(),
                    "ok": len(materialized_views) == len(target_mvs),
                    "connection_ok": True,
                    "materialized_views": materialized_views,
                }

                output_file.write_text(json.dumps(snapshot, indent=2))
                print(f"[control_mvs_snapshot] Wrote snapshot to {output_file}")
                print(
                    f"[control_mvs_snapshot] Found {len(materialized_views)} MVs: {', '.join(mv['name'] for mv in materialized_views)}"
                )
                return 0

    except psycopg.Error as e:
        print(f"ERROR: Database error: {e}", file=sys.stderr)
        # Write error snapshot for CI tolerance
        snapshot = {
            "schema": "control",
            "generated_at": datetime.now(UTC).isoformat(),
            "ok": False,
            "connection_ok": False,
            "materialized_views": [],
            "error": str(e),
        }
        output_file.write_text(json.dumps(snapshot, indent=2))
        return 0  # Exit 0 for CI tolerance
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        snapshot = {
            "schema": "control",
            "generated_at": datetime.now(UTC).isoformat(),
            "ok": False,
            "connection_ok": False,
            "materialized_views": [],
            "error": str(e),
        }
        output_file.write_text(json.dumps(snapshot, indent=2))
        return 0  # Exit 0 for CI tolerance


if __name__ == "__main__":
    sys.exit(main())
