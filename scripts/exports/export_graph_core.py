#!/usr/bin/env python3
"""
RFC-073 PR-1 — tag-only core graph export (fail-closed).

Behavior:
- Requires **read-only** DSN on tag builds (GEMATRIA_RO_DSN or ATLAS_DSN_RO preferred).
- Dev/non-tag prefers RO and may fall back to RW (GEMATRIA_DSN) for read-only queries.
- On tag builds (GITHUB_REF_TYPE=tag), exit non-zero if RO DSN missing or psycopg unavailable.
- Produces ui/out/graph_core.json conforming to graph.schema.json (core only).
- Per AGENTS.md: Extraction DB = GEMATRIA_DSN → database gematria (where graph data lives).
"""

import json
import os
import sys
import datetime
import pathlib

# Add project root to path for imports
REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.config.env import get_rw_dsn, get_ro_dsn, get_bible_db_dsn, env


OUT_PATH = pathlib.Path("ui/out/graph_core.json")


def fail(msg, code=2):
    print(f"[export_graph_core] {msg}", file=sys.stderr)
    sys.exit(code)


def main():
    is_tag = os.getenv("GITHUB_REF_TYPE") == "tag"
    # RFC-073: RO-on-tag policy (prefer GEMATRIA_RO_DSN/ATLAS_DSN_RO; dev may fall back to RW)
    dsn = None
    if is_tag:
        # Tag builds: require read-only DSN
        # Try GEMATRIA_RO_DSN or ATLAS_DSN_RO first (preferred for gematria DB)
        dsn = env("GEMATRIA_RO_DSN") or env("ATLAS_DSN_RO")
        if not dsn:
            # Fallback to other RO sources
            dsn = get_ro_dsn() or get_bible_db_dsn()
        if not dsn:
            fail(
                "Tag build requires read-only DSN (set GEMATRIA_RO_DSN or ATLAS_DSN_RO).",
                2,
            )
    else:
        # Dev/non-tag: prefer RO, fall back to RW for read-only queries
        dsn = env("GEMATRIA_RO_DSN") or env("ATLAS_DSN_RO") or get_ro_dsn() or get_bible_db_dsn()
        if not dsn:
            dsn = get_rw_dsn()  # Fallback to RW for dev
        if not dsn:
            print("[export_graph_core] No DSN available; skipping (non-tag).")
            return

    try:
        import psycopg  # psycopg3
    except Exception:
        if is_tag:
            fail("psycopg not available; cannot perform RO export on tag build.", 3)
        else:
            # Non-tag dry-runs: allow graceful noop (no file written).
            print("[export_graph_core] psycopg missing; skipping export (non-tag).")
            return

    # Attempt RO connection and extract nodes/edges (read-only queries only).
    try:
        with psycopg.connect(dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                # Test connection
                cur.execute("SELECT 1")
                _ = cur.fetchone()

                # Try to find node/edge tables (check common schemas)
                node_tables = [
                    "gematria.concept_network",
                    "gematria.concepts",
                    "gematria.nouns",
                    "public.concept_network",
                    "public.concepts",
                ]
                edge_tables = [
                    "gematria.concept_relations",
                    "gematria.edges",
                    "public.concept_relations",
                    "public.edges",
                ]

                # Find first existing node table
                nodes = []
                node_table = None
                for table in node_tables:
                    try:
                        cur.execute(f"SELECT 1 FROM {table} LIMIT 1")
                        node_table = table
                        break
                    except Exception:
                        continue

                if node_table:
                    # Extract nodes (minimal fields for core graph)
                    cur.execute(
                        f"""
                        SELECT DISTINCT
                            COALESCE(n.concept_id::text, n.id::text) as id,
                            COALESCE(n.label, n.name, n.surface, n.concept_id::text) as label,
                            n.hebrew_text,
                            n.gematria_value,
                            n.book,
                            n.chapter,
                            n.primary_verse
                        FROM {node_table} n
                        LIMIT 10000
                        """
                    )
                    nodes = [
                        {
                            "id": str(row[0]),
                            "surface": row[1] or str(row[0]),  # schema requires "surface"
                            "hebrew_text": row[2],
                            "gematria_value": row[3],
                            "book": row[4],
                            "chapter": row[5],
                            "verse": row[6],
                        }
                        for row in cur.fetchall()
                    ]

                # Find first existing edge table
                edges = []
                edge_table = None
                for table in edge_tables:
                    try:
                        cur.execute(f"SELECT 1 FROM {table} LIMIT 1")
                        edge_table = table
                        break
                    except Exception:
                        continue

                if edge_table:
                    # Extract edges (minimal fields for core graph)
                    # Try to match source/target to node IDs
                    try:
                        cur.execute(
                            f"""
                            SELECT DISTINCT
                                COALESCE(r.src_concept_id::text, r.source_id::text, r.from_id::text) as source,
                                COALESCE(r.dst_concept_id::text, r.target_id::text, r.to_id::text) as target,
                                COALESCE(r.weight, r.cosine, r.similarity, 0.0) as weight
                            FROM {edge_table} r
                            LIMIT 50000
                            """
                        )
                        edges = [
                            {
                                "src": str(row[0]),  # schema requires "src"
                                "dst": str(row[1]),  # schema requires "dst"
                                "type": "semantic",  # schema requires "type"
                                "weight": float(row[2] or 0.0),
                            }
                            for row in cur.fetchall()
                        ]
                    except Exception as e:
                        # If column names don't match, try generic approach
                        cur.execute(f"SELECT * FROM {edge_table} LIMIT 10")
                        cols = [desc[0] for desc in cur.description]
                        print(f"[export_graph_core] Edge table {edge_table} has columns: {cols}", file=sys.stderr)

                # Build payload conforming to graph.schema.json
                # Extract book from first node if available (for root-level book property)
                root_book = None
                if nodes and nodes[0].get("book"):
                    root_book = nodes[0]["book"]

                payload = {
                    "schema": "gemantria/graph.v1",  # schema requires exact value
                    "generated_at": datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z"),
                    "nodes": nodes,  # top-level, not nested in "graph"
                    "edges": edges,  # top-level, not nested in "graph"
                }
                if root_book:
                    payload["book"] = root_book
                OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
                OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"[export_graph_core] wrote {OUT_PATH} with {len(nodes)} nodes, {len(edges)} edges")
    except Exception as e:
        fail(f"RO export failed: {e}", 4)


if __name__ == "__main__":
    main()
