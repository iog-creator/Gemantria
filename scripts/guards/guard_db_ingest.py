#!/usr/bin/env python3
import json, sys, pathlib

path = sys.argv[1] if len(sys.argv) > 1 else "exports/ai_nouns.db_morph.json"

if not pathlib.Path(path).exists():
    print(f"guard_db_ingest: file not found: {path} — quarantined (OK)", file=sys.stderr)
    sys.exit(0)

with open(path, encoding="utf-8") as f:
    env = json.load(f)

assert env.get("schema", "").startswith("gemantria/ai-nouns.v"), "Bad schema"
nodes = env.get("nodes", [])
assert isinstance(nodes, list) and len(nodes) > 0, "No nouns ingested"

req = {"surface", "class", "analysis", "sources"}
miss = [i for i, x in enumerate(nodes) if req - x.keys()]
assert not miss, f"Missing required fields in {len(miss)} nodes"

print(f"OK: {len(nodes)} nouns; envelope valid.")
