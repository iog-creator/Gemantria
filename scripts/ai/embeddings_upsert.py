#!/usr/bin/env python3
# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`

import os
import sys
import json

from openai import OpenAI
import psycopg

from scripts.ai.lmstudio_resolver import base_url
from scripts.config.env import get_rw_dsn

embed_model = os.environ.get("LM_EMBED_MODEL")
dsn = get_rw_dsn()

if not embed_model:
    print("NO-GO: LM_EMBED_MODEL not set", file=sys.stderr)
    sys.exit(2)

if not dsn:
    print("NO-GO: ATLAS_DSN_RW (or GEMATRIA_DSN) not set", file=sys.stderr)
    sys.exit(2)

client = OpenAI(base_url=base_url())  # OpenAI-compatible (LM Studio)

texts = sys.argv[1:] or ["Covenant", "Prophecy", "Wisdom"]

# 1) get embeddings
resp = client.embeddings.create(model=embed_model, input=texts)
vectors = [e.embedding for e in resp.data]

# 2) upsert nodes + embeddings
conn = psycopg.connect(dsn)
cur = conn.cursor()

cur.execute("""CREATE UNIQUE INDEX IF NOT EXISTS uq_nodes_name ON gematria.nodes(name);""")
cur.execute("""CREATE UNIQUE INDEX IF NOT EXISTS uq_aiemb_node ON gematria.ai_embeddings(node_id);""")
conn.commit()

for text, vec in zip(texts, vectors):
    # insert-or-get node
    cur.execute(
        """INSERT INTO gematria.nodes(name,kind) VALUES (%s,'concept')
                   ON CONFLICT (name) DO UPDATE SET name=EXCLUDED.name
                   RETURNING id;""",
        (text,),
    )
    node_id = cur.fetchone()[0]

    # upsert embedding
    cur.execute(
        """INSERT INTO gematria.ai_embeddings(node_id, embedding)
                   VALUES (%s, %s)
                   ON CONFLICT (node_id) DO UPDATE SET embedding=EXCLUDED.embedding;""",
        (node_id, json.dumps(vec)),
    )

conn.commit()
cur.close()
conn.close()

print(json.dumps({"ok": True, "count": len(texts)}))
