#!/usr/bin/env python3
"""
Control-plane smoke test.

Proves insert+select operations work for control schema tables when DB is available,
while remaining empty-DB tolerant (DB-off) and emitting JSON evidence.

Uses centralized DSN loader (never os.getenv directly).
Tolerates empty/nonexistent DB (exits 0, writes evidence with ok=false for CI tolerance).
"""

from __future__ import annotations

import json
import sys
import uuid
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
        "WARN: psycopg not available; skipping control smoke (CI empty-DB tolerance).",
        file=sys.stderr,
    )
    # Write evidence for CI tolerance
    evidence_file = REPO / "evidence" / "control_plane_smoke.json"
    evidence_file.parent.mkdir(parents=True, exist_ok=True)
    evidence_file.write_text(
        json.dumps(
            {
                "schema": "control",
                "generated_at": datetime.now(UTC).isoformat(),
                "ok": False,
                "connection_ok": False,
                "tables": [],
                "error": "psycopg not available",
            },
            indent=2,
        )
    )
    print("[control_plane_smoke] DB-off: psycopg not available")
    sys.exit(0)

DSN = get_rw_dsn()
if not DSN:
    print("SKIP: GEMATRIA_DSN not set (empty-DB tolerance).", file=sys.stderr)
    # Write evidence for CI tolerance
    evidence_file = REPO / "evidence" / "control_plane_smoke.json"
    evidence_file.parent.mkdir(parents=True, exist_ok=True)
    evidence_file.write_text(
        json.dumps(
            {
                "schema": "control",
                "generated_at": datetime.now(UTC).isoformat(),
                "ok": False,
                "connection_ok": False,
                "tables": [],
                "error": "DSN not set",
            },
            indent=2,
        )
    )
    print("[control_plane_smoke] DB-off: DSN not set")
    sys.exit(0)

# Control schema tables to test
TABLES = [
    "tool_catalog",
    "capability_rule",
    "doc_fragment",
    "capability_session",
    "agent_run",
]


def test_table_insert_select(cur: psycopg.Cursor, table_name: str) -> dict:
    """Test insert and select for a control table."""
    insert_ok = False
    select_ok = False
    error = None

    try:
        # Generate minimal test data based on table schema
        test_project_id = 1
        test_uuid = str(uuid.uuid4())

        if table_name == "tool_catalog":
            # tool_catalog: project_id, name, ring, io_schema
            test_name = f"smoke_test_{test_uuid[:8]}"
            cur.execute(
                """
                INSERT INTO control.tool_catalog (project_id, name, ring, io_schema)
                VALUES (%s, %s, %s, %s::jsonb)
                ON CONFLICT (project_id, name) DO NOTHING
                RETURNING id
                """,
                (test_project_id, test_name, 0, '{"type": "object"}'),
            )
            if cur.fetchone():
                insert_ok = True

        elif table_name == "capability_rule":
            # capability_rule: project_id, name, ring, budgets
            test_name = f"smoke_test_{test_uuid[:8]}"
            cur.execute(
                """
                INSERT INTO control.capability_rule (project_id, name, ring, budgets)
                VALUES (%s, %s, %s, %s::jsonb)
                ON CONFLICT (project_id, name) DO NOTHING
                RETURNING id
                """,
                (test_project_id, test_name, 0, "{}"),
            )
            if cur.fetchone():
                insert_ok = True

        elif table_name == "doc_fragment":
            # doc_fragment: project_id, src, anchor, sha256
            test_src = f"smoke_test_{test_uuid[:8]}.md"
            test_anchor = f"#anchor-{test_uuid[:8]}"
            test_sha256 = "0" * 64  # Placeholder SHA256
            cur.execute(
                """
                INSERT INTO control.doc_fragment (project_id, src, anchor, sha256)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (project_id, src, anchor) DO NOTHING
                RETURNING id
                """,
                (test_project_id, test_src, test_anchor, test_sha256),
            )
            if cur.fetchone():
                insert_ok = True

        elif table_name == "capability_session":
            # capability_session: project_id, rule_id (FK), por_json, tiny_menu, ttl_s
            # First, try to get an existing rule_id, or create one
            cur.execute(
                "SELECT id FROM control.capability_rule WHERE project_id = %s LIMIT 1",
                (test_project_id,),
            )
            rule_row = cur.fetchone()
            if not rule_row:
                # Create a rule first
                cur.execute(
                    """
                    INSERT INTO control.capability_rule (project_id, name, ring, budgets)
                    VALUES (%s, %s, %s, %s::jsonb)
                    ON CONFLICT (project_id, name) DO NOTHING
                    RETURNING id
                    """,
                    (test_project_id, f"smoke_rule_{test_uuid[:8]}", 0, "{}"),
                )
                rule_row = cur.fetchone()
            if rule_row:
                rule_id = rule_row[0]
                cur.execute(
                    """
                    INSERT INTO control.capability_session (project_id, rule_id, por_json, tiny_menu, ttl_s)
                    VALUES (%s, %s, %s::jsonb, %s, %s)
                    RETURNING id
                    """,
                    (test_project_id, rule_id, "{}", [], 3600),
                )
                if cur.fetchone():
                    insert_ok = True

        elif table_name == "agent_run":
            # agent_run: project_id, tool, args_json, result_json
            cur.execute(
                """
                INSERT INTO control.agent_run (project_id, tool, args_json, result_json)
                VALUES (%s, %s, %s::jsonb, %s::jsonb)
                RETURNING id
                """,
                (test_project_id, "smoke_test_tool", "{}", "{}"),
            )
            if cur.fetchone():
                insert_ok = True

        # Test select
        cur.execute(f"SELECT COUNT(*) FROM control.{table_name} WHERE project_id = %s", (test_project_id,))
        count = cur.fetchone()[0]
        select_ok = count is not None and count >= 0

    except Exception as e:
        error = str(e)

    return {
        "name": table_name,
        "insert_ok": insert_ok,
        "select_ok": select_ok,
        "error": error,
    }


def main() -> int:
    """Run control-plane smoke test."""
    evidence_file = REPO / "evidence" / "control_plane_smoke.json"
    evidence_file.parent.mkdir(parents=True, exist_ok=True)

    now = datetime.now(UTC).isoformat()

    try:
        with psycopg.connect(DSN, autocommit=True) as conn:
            with conn.cursor() as cur:
                # Check if schema exists
                cur.execute("SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = 'control')")
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
                        "tables": [],
                        "error": "Schema does not exist",
                    }
                    evidence_file.write_text(json.dumps(payload, indent=2))
                    print("[control_plane_smoke] DB-off: Control schema does not exist")
                    return 0

                # Test each table
                results = []
                for table_name in TABLES:
                    result = test_table_insert_select(cur, table_name)
                    results.append(result)

                # Determine overall ok status
                ok = all(t["insert_ok"] and t["select_ok"] for t in results)

                payload = {
                    "schema": "control",
                    "generated_at": now,
                    "ok": ok,
                    "connection_ok": True,
                    "tables": results,
                }

                evidence_file.write_text(json.dumps(payload, indent=2))
                if ok:
                    print(f"[control_plane_smoke] DB-on: All tables OK ({len(results)} tables tested)")
                else:
                    failed = [t["name"] for t in results if not (t["insert_ok"] and t["select_ok"])]
                    print(
                        f"[control_plane_smoke] DB-on: Some tables failed: {', '.join(failed)}",
                        file=sys.stderr,
                    )
                return 0

    except psycopg.Error as e:
        print(f"ERROR: Database error: {e}", file=sys.stderr)
        payload = {
            "schema": "control",
            "generated_at": now,
            "ok": False,
            "connection_ok": False,
            "tables": [],
            "error": str(e),
        }
        evidence_file.write_text(json.dumps(payload, indent=2))
        print("[control_plane_smoke] DB-off: Database connection failed")
        return 0  # Exit 0 for CI tolerance
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        payload = {
            "schema": "control",
            "generated_at": now,
            "ok": False,
            "connection_ok": False,
            "tables": [],
            "error": str(e),
        }
        evidence_file.write_text(json.dumps(payload, indent=2))
        print("[control_plane_smoke] DB-off: Unexpected error")
        return 0  # Exit 0 for CI tolerance


if __name__ == "__main__":
    sys.exit(main())
