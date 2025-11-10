#!/usr/bin/env python3
from __future__ import annotations

import psycopg

from scripts.config.env import get_rw_dsn

REQUIRED = {
    ("gematria", "nodes"): {"node_id", "surface", "class"},
    ("gematria", "edges"): {"edge_id", "src_node_id", "dst_node_id", "edge_type"},
    ("gematria", "ai_embeddings"): {"node_id", "embedding"},
}

FORBIDDEN = {
    ("gematria", "nodes"): {"kind", "meta"},
}


def main() -> int:
    dsn = get_rw_dsn()
    if not dsn:
        print("HINT: RW DSN missing; skipping schema contract check")
        return 0
    ok = True
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        for (schema, table), need in REQUIRED.items():
            cur.execute(
                """SELECT column_name FROM information_schema.columns
                           WHERE table_schema=%s AND table_name=%s""",
                (schema, table),
            )
            cols = {r[0] for r in cur.fetchall()}
            missing = need - cols
            if missing:
                ok = False
                print(f"FAIL: {schema}.{table} missing columns: {sorted(missing)}")
        for (schema, table), ban in FORBIDDEN.items():
            cur.execute(
                """SELECT column_name FROM information_schema.columns
                           WHERE table_schema=%s AND table_name=%s""",
                (schema, table),
            )
            cols = {r[0] for r in cur.fetchall()}
            present = ban & cols
            if present:
                ok = False
                print(f"FAIL: {schema}.{table} has forbidden columns: {sorted(present)}")
    if ok:
        print("ok: schema contract satisfied")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
