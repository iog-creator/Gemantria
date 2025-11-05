#!/usr/bin/env python3
"""Guard script to validate relations before database insertion."""

import sys
import json
from pathlib import Path

p = Path("exports/graph_latest.normalized.json")

if not p.exists():
    print("ERROR: exports/graph_latest.normalized.json not found", file=sys.stderr)
    sys.exit(1)

d = json.loads(p.read_text())
rels = d.get("relations", [])

bad = [r for r in rels if not r.get("src_concept_id") or not r.get("dst_concept_id")]

if bad:
    print(f"FAIL: {len(bad)} relations missing endpoints")
    for b in bad[:5]:  # Show first 5 examples
        print(f"  Bad relation: {b}")
    sys.exit(2)

# Check for reasonable weight values
invalid_weights = [r for r in rels if not (0 <= r.get("weight", 0) <= 1)]
if invalid_weights:
    print(f"FAIL: {len(invalid_weights)} relations with invalid weights")
    sys.exit(2)

print("RELATIONS_INSERT_GUARD_OK")
