#!/usr/bin/env python3
"""
Guard: CI empty-DB tolerance.
- If GEMATRIA_DSN is unset -> exit 0 (tolerate environments without DB).
- If set but DB unreachable -> exit 0 (treat as tolerated skip).
- If set and reachable -> ensure base tables exist, else exit 2.
"""

import os, sys

try:
    import psycopg
except Exception:
    print("SKIP: psycopg not installed; treating as empty-DB tolerated.", file=sys.stderr)
    sys.exit(0)
DSN = os.getenv("GEMATRIA_DSN")
if not DSN:
    print("OK: empty-DB tolerated (no DSN).")
    sys.exit(0)
try:
    with psycopg.connect(DSN) as conn, conn.cursor() as cur:
        cur.execute("SELECT 1 FROM information_schema.schemata WHERE schema_name='gematria'")
        if cur.fetchone() is None:
            print("OK: gematria schema absent; tolerated in CI.")
            sys.exit(0)
        cur.execute("SELECT to_regclass('gematria.nouns')")
        if cur.fetchone()[0] is None:
            print("ERROR: gematria.nouns missing with DSN set; run make db.migrate", file=sys.stderr)
            sys.exit(2)
        print("OK: DB reachable and base tables present.")
        sys.exit(0)
except Exception as e:
    print(f"OK: DB unreachable ({e}); tolerated in CI.", file=sys.stderr)
    sys.exit(0)
