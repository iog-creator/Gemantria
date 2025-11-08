# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
import json, sys

path = sys.argv[1] if len(sys.argv) > 1 else "exports/ai_nouns.db_morph.json"

with open(path, encoding="utf-8") as f:
    env = json.load(f)

assert env.get("schema", "").startswith("gemantria/ai-nouns.v"), "Bad schema"
nodes = env.get("nodes", [])
assert isinstance(nodes, list) and len(nodes) > 0, "No nouns ingested"

req = {"surface", "class", "analysis", "sources"}
miss = [i for i, x in enumerate(nodes) if req - x.keys()]
assert not miss, f"Missing required fields in {len(miss)} nodes"

print(f"OK: {len(nodes)} nouns; envelope valid.")
