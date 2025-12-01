from scripts.config.env import get_rw_dsn
# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
Guard: Control Plane Health Check (Option C - DB is SSOT)
- If GEMATRIA_DSN is unset -> exit 0 (tolerate environments without DB configured).
- If set but DB unreachable -> exit 1 (FAIL: DB is SSOT, broken state).
- If set and reachable -> ensure control schema and tables exist, check shapes, refresh MVs.
- For live gates: DB-down is always a failure (Option C).
"""

import os
import sys

try:
    import psycopg

except Exception:
    strict_mode = os.environ.get("STRICT_MODE", "HINT")
    if strict_mode == "STRICT":
        print("ERROR: psycopg not installed; required in STRICT mode.", file=sys.stderr)
        sys.exit(1)
    print(
        "SKIP: psycopg not installed; treating as empty-DB tolerated (HINT mode).", file=sys.stderr
    )
    sys.exit(0)

DSN = get_rw_dsn()
strict_mode = os.environ.get("STRICT_MODE", "HINT")

if not DSN:
    if strict_mode == "STRICT":
        print("ERROR: GEMATRIA_DSN not set; required in STRICT mode.", file=sys.stderr)
        sys.exit(1)
    print("OK: empty-DB tolerated (no DSN, HINT mode).")
    sys.exit(0)

try:
    with psycopg.connect(DSN) as conn, conn.cursor() as cur:
        # Check control schema exists
        cur.execute("SELECT 1 FROM information_schema.schemata WHERE schema_name='control'")
        if cur.fetchone() is None:
            if strict_mode == "STRICT":
                print("ERROR: control schema missing; run make db.control.migrate", file=sys.stderr)
                sys.exit(1)
            print("HINT: control schema absent; run make db.control.migrate")
            sys.exit(0)

        # Check all required tables exist
        required_tables = [
            "tool_catalog",
            "capability_rule",
            "doc_fragment",
            "capability_session",
            "agent_run",
        ]
        missing_tables = []
        for table in required_tables:
            cur.execute(
                "SELECT 1 FROM information_schema.tables WHERE table_schema='control' AND table_name=%s",
                (table,),
            )
            if cur.fetchone() is None:
                missing_tables.append(table)

        if missing_tables:
            if strict_mode == "STRICT":
                print(
                    f"ERROR: Missing tables in control schema: {', '.join(missing_tables)}",
                    file=sys.stderr,
                )
                sys.exit(1)
            print(f"HINT: Missing tables in control schema: {', '.join(missing_tables)}")
            sys.exit(0)

        # Check table shapes (key columns)
        shape_checks = {
            "tool_catalog": [
                "id",
                "project_id",
                "name",
                "ring",
                "io_schema",
                "enabled",
                "created_at",
            ],
            "capability_rule": [
                "id",
                "project_id",
                "name",
                "ring",
                "allowlist",
                "denylist",
                "budgets",
                "created_at",
            ],
            "doc_fragment": ["id", "project_id", "src", "anchor", "sha256", "created_at"],
            "capability_session": [
                "id",
                "project_id",
                "rule_id",
                "por_json",
                "tiny_menu",
                "ttl_s",
                "created_at",
            ],
            "agent_run": [
                "id",
                "project_id",
                "session_id",
                "tool",
                "args_json",
                "result_json",
                "violations_json",
                "created_at",
            ],
        }

        shape_errors = []
        for table, required_cols in shape_checks.items():
            cur.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema='control' AND table_name=%s
                """,
                (table,),
            )
            existing_cols = {row[0] for row in cur.fetchall()}
            missing_cols = set(required_cols) - existing_cols
            if missing_cols:
                shape_errors.append(f"{table}: missing columns {', '.join(missing_cols)}")

        if shape_errors:
            if strict_mode == "STRICT":
                print("ERROR: Table shape issues:\n" + "\n".join(shape_errors), file=sys.stderr)
                sys.exit(1)
            print("HINT: Table shape issues:\n" + "\n".join(shape_errors))
            sys.exit(0)

        # Check materialized views exist
        cur.execute(
            "SELECT 1 FROM pg_matviews WHERE schemaname='control' AND matviewname='mv_compliance_7d'"
        )
        if cur.fetchone() is None:
            if strict_mode == "STRICT":
                print("ERROR: mv_compliance_7d missing", file=sys.stderr)
                sys.exit(1)
            print("HINT: mv_compliance_7d missing")
            sys.exit(0)

        cur.execute(
            "SELECT 1 FROM pg_matviews WHERE schemaname='control' AND matviewname='mv_compliance_30d'"
        )
        if cur.fetchone() is None:
            if strict_mode == "STRICT":
                print("ERROR: mv_compliance_30d missing", file=sys.stderr)
                sys.exit(1)
            print("HINT: mv_compliance_30d missing")
            sys.exit(0)

        # Check refresh function exists
        cur.execute(
            """
            SELECT 1 FROM pg_proc p
            JOIN pg_namespace n ON p.pronamespace = n.oid
            WHERE n.nspname = 'control' AND p.proname = 'refresh_compliance'
            """
        )
        if cur.fetchone() is None:
            if strict_mode == "STRICT":
                print("ERROR: control.refresh_compliance function missing", file=sys.stderr)
                sys.exit(1)
            print("HINT: control.refresh_compliance function missing")
            sys.exit(0)

        # MV refresh smoke test (tolerate zero rows)
        try:
            cur.execute("SELECT control.refresh_compliance('7d')")
            cur.execute("SELECT control.refresh_compliance('30d')")
        except Exception as e:
            if strict_mode == "STRICT":
                print(f"ERROR: MV refresh failed: {e}", file=sys.stderr)
                sys.exit(1)
            print(f"HINT: MV refresh failed: {e}")
            sys.exit(0)

        # Zero-row tolerance check (empty DB is OK)
        cur.execute("SELECT COUNT(*) FROM control.agent_run")
        run_count = cur.fetchone()[0]
        if run_count == 0:
            print("OK: Control plane healthy (zero rows tolerated).")
        else:
            print(f"OK: Control plane healthy ({run_count} agent_run rows).")

        sys.exit(0)

except Exception as e:
    # Option C: DB is SSOT - DB-down is always a failure for live gates
    print(
        "❌ CRITICAL: Database is unreachable (db_off). DB is SSOT - broken state.", file=sys.stderr
    )
    print(f"   Error: {e}", file=sys.stderr)
    print(
        "   Ensure Postgres is running and GEMATRIA_DSN is correctly configured.", file=sys.stderr
    )
    sys.exit(1)
