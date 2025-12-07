# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
from __future__ import annotations

import sys

# REQUIRED across scripts: load .env before any getenv/DB access
# (prevents DSN/connection issues)
from src.infra.env_loader import ensure_env_loaded

ensure_env_loaded()  # mandatory per AGENTS governance

try:
    import psycopg  # psycopg3
except Exception:
    print(
        "[data.verify] psycopg (v3) is required. pip install 'psycopg[binary]'",
        file=sys.stderr,
    )
    sys.exit(2)

from gemantria.dsn import dsn_rw

DB_DSN = dsn_rw()

TABLE_QUERIES: list[tuple[str, str]] = [
    ("concepts", "SELECT 1 FROM concepts LIMIT 1"),
    ("concept_network", "SELECT 1 FROM concept_network LIMIT 1"),
    ("concept_relations", "SELECT 1 FROM concept_relations LIMIT 1"),
]

JOIN_QUERIES: list[tuple[str, str]] = [
    (
        "network→concepts",
        (
            "SELECT cn.id, c.id AS concept_id "
            "FROM concept_network cn "
            "LEFT JOIN concept_metadata cm ON cm.concept_id = cn.concept_id "
            "LEFT JOIN concepts c ON cm.source = 'bible_db:concept_id:' || c.id::text "
            "WHERE cn.id IS NOT NULL LIMIT 10"
        ),
    ),
    (
        "relations→concepts",
        (
            "SELECT cr.id, cs.id AS src_cid, ct.id AS tgt_cid "
            "FROM concept_relations cr "
            "LEFT JOIN concept_metadata cms ON cms.concept_id = cr.source_id "
            "LEFT JOIN concepts cs ON cms.source = 'bible_db:concept_id:' || cs.id::text "
            "LEFT JOIN concept_metadata cmt ON cmt.concept_id = cr.target_id "
            "LEFT JOIN concepts ct ON cmt.source = 'bible_db:concept_id:' || ct.id::text "
            "WHERE cr.id IS NOT NULL LIMIT 10"
        ),
    ),
]


def run_query(cur: psycopg.Cursor, label: str, q: str) -> int:
    try:
        cur.execute(q)
        rows = cur.fetchall()
        if not rows:
            print(f"[data.verify] FAIL {label}: no rows", file=sys.stderr)
            return 1
        print(f"[data.verify] OK {label} ({len(rows)} rows)")
        return 0
    except Exception as e:
        print(f"[data.verify] FAIL {label}: {e}", file=sys.stderr)
        return 1


def main() -> int:
    try:
        with psycopg.connect(DB_DSN) as conn, conn.cursor() as cur:
            failures = 0
            # Tables (presence/population)
            for label, q in TABLE_QUERIES:
                try:
                    cur.execute(q)
                    _ = cur.fetchone()
                    print(f"[data.verify] OK table: {label}")
                except Exception as e:
                    print(f"[data.verify] FAIL table: {label} → {e}", file=sys.stderr)
                    failures += 1
            # Joins
            for label, q in JOIN_QUERIES:
                failures += run_query(cur, f"join: {label}", q)
    except Exception as e:
        print(f"[data.verify] DB connection failed: {e}", file=sys.stderr)
        return 2

    if failures:
        print(f"[data.verify] SUMMARY: {failures} failure(s)", file=sys.stderr)
        return 1
    print("[data.verify] SUMMARY: all checks green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
