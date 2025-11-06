#!/usr/bin/env python3
import os, sys

try:
    import psycopg
except Exception:
    print("SKIP: psycopg not installed; tolerated.", file=sys.stderr)
    sys.exit(0)
DSN = os.getenv("GEMATRIA_DSN")
RUN_ID = os.getenv("RUN_ID", "ledger-smoke")
if not DSN:
    print("OK: empty-DB tolerated (no DSN).")
    sys.exit(0)
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
