#!/usr/bin/env python3
# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`

import json
import os

import psycopg2

DSN = os.environ.get("ATLAS_DSN_RW") or os.environ.get("GEMATRIA_DSN")


def _conn():
    return psycopg2.connect(DSN)


def upsert_node(name: str, kind: str = "concept", meta: dict | None = None) -> int:
    meta = meta or {}
    with _conn() as c, c.cursor() as cur:
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_nodes_name ON gematria.nodes(name);")
        cur.execute(
            """INSERT INTO gematria.nodes(name,kind,meta)
                       VALUES (%s,%s,%s)
                       ON CONFLICT (name) DO UPDATE SET kind=EXCLUDED.kind
                       RETURNING id;""",
            (name, kind, json.dumps(meta)),
        )
        return cur.fetchone()[0]


def upsert_edge(src_id: int, dst_id: int, kind: str, weight: float | None = None, meta: dict | None = None) -> int:
    meta = meta or {}
    with _conn() as c, c.cursor() as cur:
        cur.execute(
            """INSERT INTO gematria.edges(src_id,dst_id,kind,weight,meta)
                       VALUES (%s,%s,%s,%s,%s)
                       RETURNING id;""",
            (src_id, dst_id, kind, weight, json.dumps(meta)),
        )
        return cur.fetchone()[0]


def upsert_embedding(node_id: int, embedding: list[float]) -> None:
    with _conn() as c, c.cursor() as cur:
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_aiemb_node ON gematria.ai_embeddings(node_id);")
        cur.execute(
            """INSERT INTO gematria.ai_embeddings(node_id,embedding)
                       VALUES (%s,%s)
                       ON CONFLICT (node_id) DO UPDATE SET embedding=EXCLUDED.embedding;""",
            (node_id, json.dumps(embedding)),
        )
