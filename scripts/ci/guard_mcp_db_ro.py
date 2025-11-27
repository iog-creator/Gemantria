#!/usr/bin/env python3
"""
Guard: MCP DB RO DSN + Redaction Proof (PLAN-073 M1 E02)

Validates RO DSN connectivity, mcp.v_catalog accessibility, and DSN redaction.
- HINT mode (default): Tolerates missing DB/DSN, emits hints, exits 0
- STRICT mode: Requires RO DSN + mcp.v_catalog, fails if missing

Rule References: RFC-078 (Postgres Knowledge MCP), Rule 050 (OPS Contract),
Rule 039 (Execution Contract)

Usage:
    python scripts/ci/guard_mcp_db_ro.py
    make guard.mcp.db.ro
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
    from scripts.config.env import get_ro_dsn, redact, env
except ImportError:
    print(json.dumps({"ok": False, "error": "psycopg or scripts.config.env import failed"}))
    sys.exit(1)

EVIDENCE_FILE = ROOT / "evidence" / "guard_mcp_db_ro_redaction.json"


def check_view_exists(dsn: str) -> dict:
    """Check if mcp.v_catalog view exists."""
    try:
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT EXISTS(SELECT 1 FROM information_schema.views "
                    "WHERE table_schema='mcp' AND table_name='v_catalog')"
                )
                exists = cur.fetchone()[0]
                return {"exists": bool(exists), "error": None}
    except Exception as e:
        return {"exists": False, "error": str(e)}


def check_ro_access(dsn: str) -> dict:
    """Check if DSN provides read-only access (attempt SELECT, deny writes)."""
    try:
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                # Test read access
                cur.execute("SELECT 1")
                read_ok = cur.fetchone()[0] == 1

                # Test write denial (should fail for RO DSN)
                write_denied = False
                try:
                    cur.execute("CREATE TEMP TABLE test_write (id INT)")
                    conn.commit()
                    # If we get here, writes are allowed (not RO)
                    cur.execute("DROP TABLE test_write")
                except Exception:
                    write_denied = True

                return {"read_ok": read_ok, "write_denied": write_denied, "error": None}
    except Exception as e:
        return {"read_ok": False, "write_denied": False, "error": str(e)}


def verify_dsn_redaction(dsn: str, redacted: str | None) -> bool:
    """Verify DSN is properly redacted (no credentials visible)."""
    if not redacted:
        return False
    # Check that redacted version doesn't contain password patterns
    # (should have <REDACTED> or *** instead of actual credentials)
    if "://" in redacted and "@" in redacted:
        # Extract the part between :// and @
        parts = redacted.split("://", 1)[1].split("@", 1)
        if len(parts) == 2:
            creds = parts[0]
            # Should be <REDACTED> or ***, not actual credentials
            if creds not in ("<REDACTED>", "***") and ":" in creds:
                # Check if it looks like actual credentials (has colon, not redacted)
                return False
    return True


def main() -> int:
    """Main guard logic."""
    strict_mode = os.getenv("STRICT_MODE", "0") == "1" or os.getenv("STRICT_DB_PROBE", "0") == "1"

    dsn = get_ro_dsn()
    dsn_redacted = redact(dsn) if dsn else None

    verdict = {
        "ok": True,
        "mode": "STRICT" if strict_mode else "HINT",
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "dsn_present": bool(dsn),
        "dsn_redacted": verify_dsn_redaction(dsn, dsn_redacted) if dsn else None,
        "ro_access": None,
        "view_accessible": None,
        "details": {},
    }

    # Determine DSN source
    if dsn:
        if env("GEMATRIA_RO_DSN"):
            verdict["details"]["dsn_source"] = "GEMATRIA_RO_DSN"
        elif env("ATLAS_DSN_RO"):
            verdict["details"]["dsn_source"] = "ATLAS_DSN_RO"
        elif env("ATLAS_DSN"):
            verdict["details"]["dsn_source"] = "ATLAS_DSN"
        elif env("GEMATRIA_DSN"):
            verdict["details"]["dsn_source"] = "GEMATRIA_DSN (fallback to RW)"
        else:
            verdict["details"]["dsn_source"] = "unknown"

    if not dsn:
        verdict["ok"] = False
        verdict["details"]["error"] = "No RO DSN available"
        if strict_mode:
            print(json.dumps(verdict, indent=2))
            EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
            return 1
        else:
            print("[guard_mcp_db_ro] HINT: No RO DSN available (HINT mode)", file=sys.stderr)
            print(json.dumps(verdict, indent=2))
            EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
            return 0

    # Verify DSN redaction
    if not verify_dsn_redaction(dsn, dsn_redacted):
        verdict["ok"] = False
        verdict["dsn_redacted"] = False
        verdict["details"]["redaction_error"] = "DSN not properly redacted"
        if strict_mode:
            print(json.dumps(verdict, indent=2))
            EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
            return 1
        else:
            print("[guard_mcp_db_ro] HINT: DSN redaction check failed (HINT mode)", file=sys.stderr)
            print(json.dumps(verdict, indent=2))
            EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
            return 0

    verdict["dsn_redacted"] = True

    # Check RO access
    ro_check = check_ro_access(dsn)
    verdict["ro_access"] = ro_check.get("read_ok", False) and ro_check.get("write_denied", False)
    verdict["details"]["ro_check"] = ro_check

    if ro_check.get("error"):
        verdict["ok"] = False
        verdict["details"]["error"] = ro_check["error"]
        if strict_mode:
            print(json.dumps(verdict, indent=2))
            EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
            return 1
        else:
            print("[guard_mcp_db_ro] HINT: RO access check failed (HINT mode)", file=sys.stderr)
            print(json.dumps(verdict, indent=2))
            EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
            return 0

    # Check view accessibility
    view_check = check_view_exists(dsn)
    verdict["view_accessible"] = view_check.get("exists", False)
    verdict["details"]["view_check"] = view_check

    if view_check.get("error"):
        verdict["ok"] = False
        verdict["details"]["error"] = view_check["error"]
        if strict_mode:
            print(json.dumps(verdict, indent=2))
            EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
            return 1
        else:
            print("[guard_mcp_db_ro] HINT: View check failed (HINT mode)", file=sys.stderr)
            print(json.dumps(verdict, indent=2))
            EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
            return 0

    if not verdict["view_accessible"]:
        verdict["ok"] = False
        verdict["details"]["error"] = "mcp.v_catalog view missing"
        if strict_mode:
            print(json.dumps(verdict, indent=2))
            EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
            return 1
        else:
            print("[guard_mcp_db_ro] HINT: mcp.v_catalog view missing (HINT mode)", file=sys.stderr)
            print(json.dumps(verdict, indent=2))
            EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
            return 0

    # All checks passed
    verdict["ok"] = True
    print(json.dumps(verdict, indent=2))
    EVIDENCE_FILE.write_text(json.dumps(verdict, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
