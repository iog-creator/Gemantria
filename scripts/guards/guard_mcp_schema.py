#!/usr/bin/env python3
"""
Guard: Knowledge MCP Schema Validation (PLAN-073 M1 E01)

Validates that the Knowledge MCP schema, tables, and view exist in the database.
- HINT mode (default): Tolerates missing DB/schema, emits hints
- STRICT mode: Requires schema/tables/view to exist, fails if missing

Rule References: RFC-078 (Postgres Knowledge MCP), Rule 050 (OPS Contract),
Rule 039 (Execution Contract)

Usage:
    python scripts/guards/guard_mcp_schema.py
    make guard.mcp.schema
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, UTC
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

try:
    import psycopg
    from scripts.config.env import get_ro_dsn, get_rw_dsn
except ImportError:
    print(json.dumps({"ok": False, "error": "psycopg or scripts.config.env not available"}))
    sys.exit(1)

EVIDENCE_DIR = ROOT / "evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
EVIDENCE_FILE = EVIDENCE_DIR / "guard_mcp_schema.json"


def _is_strict_mode() -> bool:
    """Determine if running in STRICT mode."""
    return os.getenv("STRICT_MODE", "0") == "1" or os.getenv("CI") == "true"


def check_schema_exists(conn) -> dict:
    """Check if mcp schema exists."""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = 'mcp')")
            exists = cur.fetchone()[0]
            return {"exists": bool(exists), "error": None}
    except Exception as e:
        return {"exists": False, "error": str(e)}


def check_tables_exist(conn) -> dict:
    """Check if required tables exist: mcp.tools, mcp.endpoints, mcp.logs."""
    required_tables = ["tools", "endpoints", "logs"]
    results = {}
    all_exist = True

    try:
        with conn.cursor() as cur:
            for table in required_tables:
                cur.execute(
                    """
                    SELECT EXISTS(
                        SELECT 1 FROM information_schema.tables
                        WHERE table_schema = 'mcp' AND table_name = %s
                    )
                    """,
                    (table,),
                )
                exists = cur.fetchone()[0]
                results[table] = bool(exists)
                if not exists:
                    all_exist = False
        return {"all_exist": all_exist, "tables": results, "error": None}
    except Exception as e:
        return {"all_exist": False, "tables": {}, "error": str(e)}


def check_view_exists(conn) -> dict:
    """Check if mcp.v_catalog view exists."""
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.views
                    WHERE table_schema = 'mcp' AND table_name = 'v_catalog'
                )
                """
            )
            exists = cur.fetchone()[0]
            return {"exists": bool(exists), "error": None}
    except Exception as e:
        return {"exists": False, "error": str(e)}


def main() -> int:
    """Main guard logic."""
    strict_mode = _is_strict_mode()
    mode_str = "STRICT" if strict_mode else "HINT"

    # Try RO DSN first, fallback to RW
    dsn = get_ro_dsn() or get_rw_dsn()

    verdict = {
        "ok": True,
        "mode": mode_str,
        "schema_exists": False,
        "tables_present": False,
        "view_exists": False,
        "details": {},
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }

    if not dsn:
        verdict["ok"] = False
        verdict["details"]["error"] = "No DSN available (RO or RW)"
        verdict["details"]["notes"] = ["DSN not found in environment"]
        if strict_mode:
            print(json.dumps(verdict, indent=2), file=sys.stderr)
            EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
            return 1
        else:
            print("[guard_mcp_schema] HINT: No DSN available (HINT mode)", file=sys.stderr)
            print(json.dumps(verdict, indent=2))
            EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
            return 0

    try:
        with psycopg.connect(dsn) as conn:
            # Check schema
            schema_check = check_schema_exists(conn)
            verdict["schema_exists"] = schema_check["exists"]
            verdict["details"]["schema"] = schema_check

            if not schema_check["exists"]:
                verdict["ok"] = False
                verdict["details"]["notes"] = verdict["details"].get("notes", [])
                verdict["details"]["notes"].append("mcp schema missing")
                if strict_mode:
                    print(json.dumps(verdict, indent=2), file=sys.stderr)
                    EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
                    return 1
                else:
                    print("[guard_mcp_schema] HINT: mcp schema missing (HINT mode)", file=sys.stderr)
                    print(json.dumps(verdict, indent=2))
                    EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
                    return 0

            # Check tables
            tables_check = check_tables_exist(conn)
            verdict["tables_present"] = tables_check["all_exist"]
            verdict["details"]["tables"] = tables_check

            if not tables_check["all_exist"]:
                verdict["ok"] = False
                missing = [t for t, exists in tables_check["tables"].items() if not exists]
                verdict["details"]["notes"] = verdict["details"].get("notes", [])
                verdict["details"]["notes"].append(f"Missing tables: {', '.join(missing)}")
                if strict_mode:
                    print(json.dumps(verdict, indent=2), file=sys.stderr)
                    EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
                    return 1
                else:
                    print(
                        f"[guard_mcp_schema] HINT: Missing tables: {', '.join(missing)} (HINT mode)",
                        file=sys.stderr,
                    )
                    print(json.dumps(verdict, indent=2))
                    EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
                    return 0

            # Check view
            view_check = check_view_exists(conn)
            verdict["view_exists"] = view_check["exists"]
            verdict["details"]["view"] = view_check

            if not view_check["exists"]:
                verdict["ok"] = False
                verdict["details"]["notes"] = verdict["details"].get("notes", [])
                verdict["details"]["notes"].append("mcp.v_catalog view missing")
                if strict_mode:
                    print(json.dumps(verdict, indent=2), file=sys.stderr)
                    EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
                    return 1
                else:
                    print(
                        "[guard_mcp_schema] HINT: mcp.v_catalog view missing (HINT mode)",
                        file=sys.stderr,
                    )
                    print(json.dumps(verdict, indent=2))
                    EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
                    return 0

    except psycopg.Error as e:
        verdict["ok"] = False
        verdict["details"]["error"] = f"Database connection error: {e}"
        verdict["details"]["notes"] = [f"Failed to connect to database: {e}"]
        if strict_mode:
            print(json.dumps(verdict, indent=2), file=sys.stderr)
            EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
            return 1
        else:
            print(f"[guard_mcp_schema] HINT: Database connection failed: {e} (HINT mode)", file=sys.stderr)
            print(json.dumps(verdict, indent=2))
            EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
            return 0
    except Exception as e:
        verdict["ok"] = False
        verdict["details"]["error"] = f"Unexpected error: {e}"
        verdict["details"]["notes"] = [f"Unexpected error: {e}"]
        if strict_mode:
            print(json.dumps(verdict, indent=2), file=sys.stderr)
            EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
            return 1
        else:
            print(f"[guard_mcp_schema] HINT: Unexpected error: {e} (HINT mode)", file=sys.stderr)
            print(json.dumps(verdict, indent=2))
            EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
            return 0

    # All checks passed
    verdict["details"]["notes"] = ["All schema components present"]
    print(json.dumps(verdict, indent=2))
    EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
