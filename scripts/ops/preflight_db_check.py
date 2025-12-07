#!/usr/bin/env python3
"""
Pre-flight DB Check - Mandatory before any DMS query.

This script enforces the evidence-first protocol (Rule 050):
- Check DB status BEFORE querying
- Fail-fast if DB is required but offline
- Emit clear error messages pointing to the fix

Usage:
    python scripts/ops/preflight_db_check.py [--mode hint|strict]

Exit codes:
    0: DB is available (or not required in hint mode)
    1: DB is required but offline
    2: DB check failed (error)
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.config.env import get_rw_dsn
from scripts.guards.guard_db_health import check_db_health


def main() -> int:
    """Check DB availability before proceeding."""
    parser = argparse.ArgumentParser(description="Pre-flight DB check")
    parser.add_argument(
        "--mode",
        choices=["hint", "strict"],
        default="strict",
        help="Mode: hint (tolerate db_off) or strict (fail if db_off)",
    )
    args = parser.parse_args()

    # Check if DSN is configured
    dsn = get_rw_dsn()
    if not dsn:
        if args.mode == "strict":
            print("❌ CRITICAL: GEMATRIA_DSN not configured", file=sys.stderr)
            print("   DB is SSOT - cannot proceed without DSN", file=sys.stderr)
            print("   See: docs/SSOT/GEMATRIA_DSN_GOVERNANCE.md", file=sys.stderr)
            return 1
        # Hint mode: tolerate missing DSN
        print("⚠️  WARNING: GEMATRIA_DSN not configured (hint mode - continuing)", file=sys.stderr)
        return 0

    # Check DB health
    try:
        health = check_db_health()
        ok = health.get("ok", False)
        mode = health.get("mode", "unknown")

        if not ok or mode != "ready":
            if args.mode == "strict":
                print("❌ CRITICAL: Database is unreachable (db_off)", file=sys.stderr)
                print(f"   DB health mode: {mode}", file=sys.stderr)
                if health.get("details", {}).get("errors"):
                    print(f"   Errors: {health['details']['errors'][0]}", file=sys.stderr)
                print("\n   Required actions:", file=sys.stderr)
                print("   1. Check PostgreSQL status: systemctl status postgresql", file=sys.stderr)
                print("   2. Start PostgreSQL: sudo systemctl start postgresql", file=sys.stderr)
                print("   3. Enable auto-start: sudo systemctl enable postgresql", file=sys.stderr)
                print("   4. Verify connection: pg_isready", file=sys.stderr)
                print("\n   See: docs/hints/HINT-DB-002-postgres-not-running.md", file=sys.stderr)
                return 1
            # Hint mode: warn but continue
            print(
                f"⚠️  WARNING: Database is unreachable (mode: {mode}) - continuing in hint mode",
                file=sys.stderr,
            )
            return 0

        # DB is ready
        print("✅ DB connectivity verified (SSOT requirement)", file=sys.stderr)
        return 0

    except Exception as e:
        print(f"❌ CRITICAL: Failed to check DB health: {e}", file=sys.stderr)
        print("   DB is SSOT - cannot proceed without DB connectivity check", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
