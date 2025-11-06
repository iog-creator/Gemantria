#!/usr/bin/env python3

import os, sys

try:
    import psycopg
except Exception:
    print("psycopg not available; SKIP"); sys.exit(0)

if os.getenv("CHECKPOINTER","memory").lower() != "postgres":
    print("checkpointer not postgres; SKIP"); sys.exit(0)

dsn = os.getenv("GEMATRIA_DSN")
if not dsn:
    print("GEMATRIA_DSN missing; SKIP"); sys.exit(0)

with psycopg.connect(dsn) as c, c.cursor() as cur:
    cur.execute("SELECT count(*) FROM gematria.checkpoints WHERE created_at > NOW() - INTERVAL '2 hours'")
    n = cur.fetchone()[0]

    if n == 0:
        print("ERROR: no recent checkpoints found; saver did not snapshot.", file=sys.stderr); sys.exit(2)

print("OK: recent checkpoints present.")
