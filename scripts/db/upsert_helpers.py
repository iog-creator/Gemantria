#!/usr/bin/env python3
# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
from __future__ import annotations

import json

from psycopg.rows import dict_row

from .pool import get_pool

# NOTE: schema columns use node_id/surface; keep helpers generic/small.


def upsert_node(surface: str, kind: str = "concept", meta: dict | None = None) -> str:
    """Upsert a node. Note: 'kind' maps to 'class' column; 'meta' is stored in evidence if needed."""
    with get_pool().connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        # Ensure a uniqueness surface index exists (idempotent)
        cur.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_nodes_surface ON gematria.nodes(surface);"
        )
        # Schema uses 'class' not 'kind'; no 'meta' column, so we ignore it or could store in a future JSONB column
        cur.execute(
            """
            INSERT INTO gematria.nodes(surface, class)
            VALUES (%(s)s, %(k)s)
            ON CONFLICT (surface) DO UPDATE SET class=EXCLUDED.class
            RETURNING node_id;
            """,
            {"s": surface, "k": kind},
        )
        node_id = cur.fetchone()["node_id"]
        conn.commit()
        return str(node_id)


def upsert_edge(
    src_id: str, dst_id: str, kind: str, weight: float | None = None, meta: dict | None = None
) -> str:
    meta = meta or {}
    # Store weight in evidence if provided, or use edge_strength column if weight is set
    if weight is not None:
        meta["weight"] = weight
    with get_pool().connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            INSERT INTO gematria.edges(src_node_id, dst_node_id, edge_type, edge_strength, evidence)
            VALUES (%(s)s, %(d)s, %(k)s, %(w)s, %(m)s)
            RETURNING edge_id;
            """,
            {"s": src_id, "d": dst_id, "k": kind, "w": weight, "m": json.dumps(meta)},
        )
        edge_id = cur.fetchone()["edge_id"]
        conn.commit()
        return str(edge_id)


def upsert_embedding(
    node_id: str, embedding: list[float], model_name: str = "text-embedding-bge-m3"
) -> None:
    # Cast JSON array to pgvector with ::vector for correctness/portability.
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_aiemb_node ON gematria.ai_embeddings(node_id);"
        )
        cur.execute(
            """
            INSERT INTO gematria.ai_embeddings(node_id, embedding, model_name)
            VALUES (%(id)s, %(vec)s::vector, %(model)s)
            ON CONFLICT (node_id) DO UPDATE SET embedding=EXCLUDED.embedding, model_name=EXCLUDED.model_name;
            """,
            {"id": node_id, "vec": json.dumps(embedding), "model": model_name},
        )
        conn.commit()


# Optional: batch pipeline insert (future use)
def upsert_embeddings_pipeline(
    rows: list[tuple[str, list[float]]], model_name: str = "text-embedding-bge-m3"
) -> None:
    if not rows:
        return
    with get_pool().connection() as conn:
        with conn.pipeline():
            with conn.cursor() as cur:
                for nid, emb in rows:
                    cur.execute(
                        """
                        INSERT INTO gematria.ai_embeddings(node_id, embedding, model_name)
                        VALUES (%(id)s, %(vec)s::vector, %(model)s)
                        ON CONFLICT (node_id) DO UPDATE SET embedding=EXCLUDED.embedding, model_name=EXCLUDED.model_name;
                        """,
                        {"id": nid, "vec": json.dumps(emb), "model": model_name},
                    )
        conn.commit()
