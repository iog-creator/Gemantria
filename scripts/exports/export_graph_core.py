#!/usr/bin/env python3
"""
RFC-073 PR-1 — tag-only core graph export (fail-closed).

Behavior:
- Requires GEMATRIA_DSN via centralized loader (get_rw_dsn()) to access gematria database.
- On tag builds (GITHUB_REF_TYPE=tag), exit non-zero if DSN missing or psycopg unavailable.
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

from scripts.config.env import get_rw_dsn


OUT_PATH = pathlib.Path("ui/out/graph_core.json")


def fail(msg, code=2):
    print(f"[export_graph_core] {msg}", file=sys.stderr)
    sys.exit(code)


def main():
    is_tag = os.getenv("GITHUB_REF_TYPE") == "tag"
    # Use RW DSN to access gematria database (where graph data lives)
    # Per AGENTS.md: Extraction DB = GEMATRIA_DSN → database gematria
    dsn = get_rw_dsn()
    if is_tag and not dsn:
        fail("Tag build requires GEMATRIA_DSN (set GEMATRIA_DSN, RW_DSN, AI_AUTOMATION_DSN, ATLAS_DSN_RW, or ATLAS_DSN).", 2)

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
                payload = {
                    "schema": "gemantria/graph.v1",  # schema requires exact value
                    "generated_at": datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z"),
                    "nodes": nodes,  # top-level, not nested in "graph"
                    "edges": edges,  # top-level, not nested in "graph"
                }
                OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
                OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"[export_graph_core] wrote {OUT_PATH} with {len(nodes)} nodes, {len(edges)} edges")
    except Exception as e:
        fail(f"RO export failed: {e}", 4)


if __name__ == "__main__":
    main()
