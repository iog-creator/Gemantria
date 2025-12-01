#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

p = Path("exports/graph_latest.json")
if not p.exists():
    print("[analytics.verify] missing exports/graph_latest.json", file=sys.stderr)
    sys.exit(2)

doc = json.loads(p.read_text(encoding="utf-8"))
ts = doc.get("generated_at", "")
ok_ts = bool(re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z$", ts))
nodes = doc.get("nodes", [])
edges = doc.get("edges", [])
print(f"[analytics.verify] generated_at RFC3339: {'OK' if ok_ts else 'FAIL'}; nodes={len(nodes)} edges={len(edges)}")
sys.exit(0 if ok_ts else 3)
