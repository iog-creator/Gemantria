# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
import os, sys

try:
    import psycopg
from scripts.config.env import get_rw_dsn, get_bible_db_dsn
except Exception:
    print("SKIP: psycopg not installed; tolerated.", file=sys.stderr)
    sys.exit(0)
DSN = get_rw_dsn()
RUN_ID = os.getenv("RUN_ID", "ledger-smoke")
if not DSN:
    print("ERROR: GEMATRIA_DSN not configured in environment.", file=sys.stderr)
    print("Please ensure:", file=sys.stderr)
    print("1. .env file exists (copy from env_example.txt)", file=sys.stderr)
    print("2. GEMATRIA_DSN is set in .env", file=sys.stderr)
    print("3. Virtual environment is active: source .venv/bin/activate", file=sys.stderr)
    print("4. Run environment validation: make env.validate", file=sys.stderr)
    sys.exit(2)
with psycopg.connect(DSN) as c, c.cursor() as cur:
    cur.execute("SELECT to_regclass('gematria.runs_ledger')")
    if cur.fetchone()[0] is None:
        print("ERROR: runs_ledger missing; run make db.migrate", file=sys.stderr)
        sys.exit(2)
    cur.execute(
        "INSERT INTO gematria.runs_ledger(run_id, book, notes, started_at) VALUES (%s,'Genesis','smoke', now()) ON CONFLICT DO NOTHING",
        (RUN_ID,),
    )
    cur.execute("UPDATE gematria.runs_ledger SET finished_at = now() WHERE run_id=%s", (RUN_ID,))
    cur.execute(
        "SELECT run_id, book, started_at IS NOT NULL, finished_at IS NOT NULL FROM gematria.runs_ledger WHERE run_id=%s",
        (RUN_ID,),
    )
    row = cur.fetchone()
    assert row and row[0] == RUN_ID and row[2] and row[3], "runs_ledger row not complete"
print("OK: runs_ledger write+finish verified.")
