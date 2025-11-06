#!/usr/bin/env python3
import os, sys

try:
    import psycopg
except Exception:
    print("SKIP: psycopg not installed; tolerated.", file=sys.stderr)
    sys.exit(0)
dsn = os.getenv("GEMATRIA_DSN")
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
