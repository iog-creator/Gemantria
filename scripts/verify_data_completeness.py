#!/usr/bin/env python3
import os, sys
from typing import List, Tuple

# REQUIRED across scripts: load .env before any getenv/DB access
# (prevents DSN/connection issues)
from src.infra.env_loader import ensure_env_loaded  # type: ignore
ensure_env_loaded()  # mandatory per AGENTS governance

try:
    import psycopg  # psycopg3
except Exception as e:
    print("[data.verify] psycopg (v3) is required. pip install 'psycopg[binary]'", file=sys.stderr)
    sys.exit(2)

DB_DSN = os.getenv("GEMATRIA_DSN") or os.getenv("DB_DSN") or "postgresql://localhost/gematria"

TABLE_QUERIES: List[Tuple[str, str]] = [
    ("concepts", "SELECT 1 FROM concepts LIMIT 1"),
    ("concept_network", "SELECT 1 FROM concept_network LIMIT 1"),
    ("concept_relations", "SELECT 1 FROM concept_relations LIMIT 1"),
]

JOIN_QUERIES: List[Tuple[str, str]] = [
    ("network→concepts",
     "SELECT cn.id, c.id FROM concept_network cn JOIN concepts c ON cn.concept_id = c.id LIMIT 1"),
    ("relations→concepts",
     "SELECT cr.id, c.id FROM concept_relations cr JOIN concepts c ON cr.source_id = c.id LIMIT 1"),
]

def main() -> int:
    try:
        with psycopg.connect(DB_DSN) as conn, conn.cursor() as cur:
            failures = []

            # Check tables exist and have data
            for table_name, query in TABLE_QUERIES:
                try:
                    cur.execute(query)
                    if cur.fetchone() is None:
                        failures.append(f"table:{table_name} (empty)")
                    else:
                        print(f"[data.verify] OK table: {table_name}")
                except Exception as e:
                    failures.append(f"table:{table_name} ({e})")

            # Check joins work
            for join_name, query in JOIN_QUERIES:
                try:
                    cur.execute(query)
                    if cur.fetchone() is None:
                        failures.append(f"join:{join_name} (no rows)")
                    else:
                        print(f"[data.verify] OK join: {join_name}")
                except Exception as e:
                    failures.append(f"join:{join_name} ({e})")

            if failures:
                print("[data.verify] FAILURES:", "; ".join(failures), file=sys.stderr)
                return 1
            else:
                print("[data.verify] SUMMARY: all checks green")
                return 0

    except Exception as e:
        print(f"[data.verify] Connection failed: {e}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())
