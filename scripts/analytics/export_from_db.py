#!/usr/bin/env python3
import os
import sys
import json
import datetime
from pathlib import Path

# Load .env if present
env_file = Path(".env")
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            if key and value:
                os.environ.setdefault(key, value)

RFC3339 = "%Y-%m-%dT%H:%M:%S.%fZ"


def rfc3339_now() -> str:
    return datetime.datetime.now(datetime.UTC).strftime(RFC3339)


def _dsn() -> str | None:
    return os.getenv("GEMATRIA_DSN") or os.getenv("AI_AUTOMATION_DSN")


def _try_import_psycopg():
    try:
        import psycopg

        return psycopg
    except Exception as e:
        print(f"[export_from_db] psycopg not available: {e}", file=sys.stderr)
        return None


def _first_existing_table(cur, candidates) -> str | None:
    for schema_table in candidates:
        schema, table = schema_table.split(".", 1)
        cur.execute(
            """
            select 1
            from information_schema.tables
            where table_schema=%s and table_name=%s
            limit 1
        """,
            (schema, table),
        )
        if cur.fetchone():
            return schema_table
    return None


def export() -> int:
    dsn = _dsn()
    out_path = os.path.join("exports", "graph_latest.json")
    os.makedirs("exports", exist_ok=True)

    if not dsn:
        # Fallback: leave a clear stub if no DB configured
        stub = {
            "schema": "gemantria/graph.v1",
            "generated_at": rfc3339_now(),
            "note": "No DSN configured; exporter produced stub only.",
            "nodes": [],
            "edges": [],
        }
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(stub, f, ensure_ascii=False, indent=2)
        print("[export_from_db] No DSN set; wrote stub exports/graph_latest.json")
        return 0

    psycopg = _try_import_psycopg()
    if not psycopg:
        print("[export_from_db] psycopg missing; cannot export from DB", file=sys.stderr)
        return 1

    node_tables = [
        "gematria.concepts",
        "gematria.nouns",
        "gematria.nodes",
        "gematria.graph_nodes",
    ]
    edge_tables = [
        "gematria.concept_relations",
        "gematria.edges",
        "gematria.graph_edges",
    ]

    with psycopg.connect(dsn) as conn, conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
        nt = _first_existing_table(cur, node_tables)
        et = _first_existing_table(cur, edge_tables)
        if not nt or not et:
            print(
                f"[export_from_db] No known node/edge tables; nodes={nt}, edges={et}",
                file=sys.stderr,
            )
            return 2

        cur.execute(f"select * from {nt}")
        nodes = list(cur.fetchall())
        cur.execute(f"select * from {et}")
        edges = list(cur.fetchall())

    doc = {
        "schema": "gemantria/graph.v1",
        "generated_at": rfc3339_now(),
        "nodes": nodes,
        "edges": edges,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    print(f"[export_from_db] Wrote {out_path} with {len(nodes)} nodes / {len(edges)} edges")
    return 0


if __name__ == "__main__":
    sys.exit(export())
