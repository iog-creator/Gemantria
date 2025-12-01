#!/usr/bin/env python3
# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`

import json
import os
from uuid import uuid4

from openai import OpenAI

from scripts.ai.lmstudio_resolver import base_url
from scripts.db.upsert_helpers import upsert_edge, upsert_embedding, upsert_node

run_id = f"writers-smoke-{uuid4()}"
client = OpenAI(base_url=base_url())
emb = (
    client.embeddings.create(
        model=os.environ.get("LM_EMBED_MODEL", "text-embedding-3-small"), input=["covenant"]
    )
    .data[0]
    .embedding
)
n1 = upsert_node("covenant", "concept")
upsert_embedding(n1, emb)
n2 = upsert_node("wisdom", "concept")
upsert_edge(n1, n2, "related_to", 0.8, {"source": "writers_smoke"})
print(json.dumps({"ok": True, "run_id": run_id, "nodes": [n1, n2]}))
