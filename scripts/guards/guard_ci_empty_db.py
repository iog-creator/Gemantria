from scripts.config.env import get_rw_dsn
# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
Guard: DB connectivity check (Option C - DB is SSOT).
- If GEMATRIA_DSN is unset -> exit 0 (tolerate environments without DB configured).
- If set but DB unreachable -> exit 1 (FAIL: DB is SSOT, broken state).
- If set and reachable -> ensure base tables exist, else exit 2.
"""

import sys

try:
    import psycopg

except Exception:
    print("SKIP: psycopg not installed; treating as empty-DB tolerated.", file=sys.stderr)
    sys.exit(0)
DSN = get_rw_dsn()
if not DSN:
    print("OK: empty-DB tolerated (no DSN).")
    sys.exit(0)
try:
    with psycopg.connect(DSN) as conn, conn.cursor() as cur:
        cur.execute("SELECT 1 FROM information_schema.schemata WHERE schema_name='gematria'")
        if cur.fetchone() is None:
            print("ERROR: gematria schema absent; DB is SSOT - schema must exist.", file=sys.stderr)
            sys.exit(2)
        cur.execute("SELECT to_regclass('gematria.nouns')")
        if cur.fetchone()[0] is None:
            print("ERROR: gematria.nouns missing with DSN set; run make db.migrate", file=sys.stderr)
            sys.exit(2)
        print("OK: DB reachable and base tables present.")
        sys.exit(0)
except Exception as e:
    print("❌ CRITICAL: Database is unreachable (db_off). DB is SSOT - broken state.", file=sys.stderr)
    print(f"   Error: {e}", file=sys.stderr)
    print("   Ensure Postgres is running and GEMATRIA_DSN is correctly configured.", file=sys.stderr)
    sys.exit(1)
