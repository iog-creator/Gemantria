#!/usr/bin/env python3
# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`

import os
import sys
import json

from openai import OpenAI
import psycopg

from scripts.ai.lmstudio_resolver import base_url
from scripts.config.env import get_rw_dsn


def main():
    q = " ".join(sys.argv[1:]) or "wisdom covenant"
    model = os.environ.get("LM_EMBED_MODEL") or "text-embedding-3-small"
    k = int(os.environ.get("TOPK", "5"))
    dsn = get_rw_dsn()
    if not dsn:
        print("NO-GO: set ATLAS_DSN (RO) or ATLAS_DSN_RW for DB access", file=sys.stderr)
        sys.exit(2)
    client = OpenAI(base_url=base_url())
    emb = client.embeddings.create(model=model, input=[q]).data[0].embedding
    conn = psycopg.connect(dsn)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT n.node_id, n.surface
        FROM gematria.nodes n
        JOIN gematria.ai_embeddings e ON e.node_id = n.node_id
        ORDER BY e.embedding <-> %s
        LIMIT %s
    """,
        (json.dumps(emb), k),
    )
    rows = [{"node_id": str(r[0]), "surface": r[1]} for r in cur.fetchall()]
    cur.close()
    conn.close()
    print(json.dumps({"ok": True, "q": q, "topk": rows}, ensure_ascii=False))


if __name__ == "__main__":
    main()
