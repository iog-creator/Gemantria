#!/usr/bin/env python3
"""
MCP catalog stub evidence generator.

Queries control.mcp_tool_catalog view and emits JSON evidence to
evidence/mcp_catalog_stub.json.

Uses centralized DSN loader (never os.getenv directly).
Tolerates empty/nonexistent DB (exits 0, writes empty evidence for CI tolerance).
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
        "WARN: psycopg not available; skipping MCP catalog stub (CI empty-DB tolerance).",
        file=sys.stderr,
    )
    # Write empty evidence for CI tolerance
    evidence_file = REPO / "evidence" / "mcp_catalog_stub.json"
    evidence_file.parent.mkdir(parents=True, exist_ok=True)
    evidence_file.write_text(
        json.dumps(
            {
                "schema": "control",
                "generated_at": datetime.now(UTC).isoformat(),
                "ok": False,
                "connection_ok": False,
                "tools": [],
                "error": "psycopg not available",
            },
            indent=2,
        )
    )
    sys.exit(0)

DSN = get_rw_dsn()
if not DSN:
    print("SKIP: GEMATRIA_DSN not set (empty-DB tolerance).", file=sys.stderr)
    # Write empty evidence for CI tolerance
    evidence_file = REPO / "evidence" / "mcp_catalog_stub.json"
    evidence_file.parent.mkdir(parents=True, exist_ok=True)
    evidence_file.write_text(
        json.dumps(
            {
                "schema": "control",
                "generated_at": datetime.now(UTC).isoformat(),
                "ok": False,
                "connection_ok": False,
                "tools": [],
                "error": "DSN not set",
            },
            indent=2,
        )
    )
    sys.exit(0)


def main() -> int:
    """Generate MCP catalog stub evidence."""
    evidence_file = REPO / "evidence" / "mcp_catalog_stub.json"
    evidence_file.parent.mkdir(parents=True, exist_ok=True)

    now = datetime.now(UTC).isoformat()

    try:
        with psycopg.connect(DSN, autocommit=True) as conn:
            with conn.cursor() as cur:
                # Check if schema exists
                cur.execute(
                    "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = 'control')"
                )
                schema_exists = cur.fetchone()[0]

                if not schema_exists:
                    print(
                        "WARN: Control schema does not exist; writing DB-off evidence.",
                        file=sys.stderr,
                    )
                    payload = {
                        "schema": "control",
                        "generated_at": now,
                        "ok": False,
                        "connection_ok": True,
                        "tools": [],
                        "error": "Schema does not exist",
                    }
                    evidence_file.write_text(json.dumps(payload, indent=2))
                    print("[mcp_catalog_stub] DB-off: Control schema does not exist")
                    return 0

                # Check if view exists
                cur.execute(
                    "SELECT EXISTS(SELECT 1 FROM information_schema.views WHERE table_schema = 'control' AND table_name = 'mcp_tool_catalog')"
                )
                view_exists = cur.fetchone()[0]

                if not view_exists:
                    print(
                        "WARN: control.mcp_tool_catalog view does not exist; writing DB-off evidence.",
                        file=sys.stderr,
                    )
                    payload = {
                        "schema": "control",
                        "generated_at": now,
                        "ok": False,
                        "connection_ok": True,
                        "tools": [],
                        "error": "View mcp_tool_catalog does not exist",
                    }
                    evidence_file.write_text(json.dumps(payload, indent=2))
                    print("[mcp_catalog_stub] DB-off: View mcp_tool_catalog does not exist")
                    return 0

                # Query the view
                cur.execute(
                    "SELECT tool_name, input_schema_ref, output_schema_ref, ring, read_only FROM control.mcp_tool_catalog ORDER BY tool_name"
                )
                rows = cur.fetchall()

                tools = []
                for row in rows:
                    tools.append(
                        {
                            "tool_name": row[0],
                            "input_schema_ref": row[1],
                            "output_schema_ref": row[2],
                            "ring": row[3],
                            "read_only": row[4],
                        }
                    )

                payload = {
                    "schema": "control",
                    "generated_at": now,
                    "ok": True,
                    "connection_ok": True,
                    "tools": tools,
                }

                evidence_file.write_text(json.dumps(payload, indent=2))
                print(f"[mcp_catalog_stub] DB-on: Found {len(tools)} tools in catalog")
                return 0

    except psycopg.Error as e:
        print(f"ERROR: Database error: {e}", file=sys.stderr)
        payload = {
            "schema": "control",
            "generated_at": now,
            "ok": False,
            "connection_ok": False,
            "tools": [],
            "error": str(e),
        }
        evidence_file.write_text(json.dumps(payload, indent=2))
        print("[mcp_catalog_stub] DB-off: Database connection failed")
        return 0  # Exit 0 for CI tolerance
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        payload = {
            "schema": "control",
            "generated_at": now,
            "ok": False,
            "connection_ok": False,
            "tools": [],
            "error": str(e),
        }
        evidence_file.write_text(json.dumps(payload, indent=2))
        print("[mcp_catalog_stub] DB-off: Unexpected error")
        return 0  # Exit 0 for CI tolerance


if __name__ == "__main__":
    sys.exit(main())
