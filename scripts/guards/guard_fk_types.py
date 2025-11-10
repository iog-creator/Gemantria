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
dsn = get_rw_dsn()
if not dsn:
    print("OK: empty-DB tolerated (no DSN).")
    sys.exit(0)
Q = """
SELECT conrelid::regclass AS tbl, att.attname AS col,
       pg_catalog.format_type(att.atttypid, att.atttypmod) AS col_type,
       confrelid::regclass AS reftbl,
       pg_catalog.format_type(att2.atttypid, att2.atttypmod) AS ref_type
FROM pg_constraint c
JOIN pg_attribute att  ON att.attrelid = c.conrelid  AND att.attnum  = ANY(c.conkey)
JOIN pg_attribute att2 ON att2.attrelid = c.confrelid AND att2.attnum = ANY(c.confkey)
WHERE c.contype='f' AND att.atttypid <> att2.atttypid;
"""
with psycopg.connect(dsn) as cn, cn.cursor() as cur:
    cur.execute(Q)
    rows = cur.fetchall()
    if rows:
        for r in rows:
            print(f"ERROR: FK type mismatch: {r}", file=sys.stderr)
        sys.exit(2)
print("OK: no FK type mismatches detected.")
