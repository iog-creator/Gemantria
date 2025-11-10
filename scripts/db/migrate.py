# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
Tiny, deterministic SQL migrator for P1-DB.
Applies *.sql in migrations/ by filename order; tracks in gematria.schema_migrations.
Tolerates empty/nonexistent DB if GEMATRIA_DSN is unset (exits 0 for CI tolerance).
"""

import os, sys, glob

try:
    import psycopg
from scripts.config.env import get_rw_dsn, get_bible_db_dsn
except Exception:
    print("WARN: psycopg not available; skipping migrate (CI empty-DB tolerance).", file=sys.stderr)
    sys.exit(0)

DSN = get_rw_dsn()
if not DSN:
    print("SKIP: GEMATRIA_DSN not set (empty-DB tolerance).", file=sys.stderr)
    sys.exit(0)


def main():
    wl = "scripts/db/migrate_whitelist.txt"
    if os.path.exists(wl):
        with open(wl, encoding="utf-8") as fh:
            files = [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
    else:
        files = sorted(glob.glob("migrations/*.sql"))
    if not files:
        print("No migrations found; nothing to do.")
        return
    with psycopg.connect(DSN, autocommit=True) as conn, conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS gematria")
        cur.execute("""CREATE TABLE IF NOT EXISTS gematria.schema_migrations(
                           id TEXT PRIMARY KEY, applied_at TIMESTAMPTZ DEFAULT now())""")
        cur.execute("SELECT id FROM gematria.schema_migrations")
        done = {r[0] for r in cur.fetchall()}
        applied = 0
        for path in files:
            mid = os.path.basename(path)
            if mid in done:
                continue
            sql = open(path, encoding="utf-8").read()
            cur.execute(sql)
            cur.execute("INSERT INTO gematria.schema_migrations(id) VALUES (%s)", (mid,))
            applied += 1
            print(f"Applied {mid}")
        print(f"OK: migrations complete (applied={applied}, total={len(files)})")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: migrate failed: {e}", file=sys.stderr)
        sys.exit(2)
