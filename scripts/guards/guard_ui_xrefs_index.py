#!/usr/bin/env python3
"""Guard for UI xrefs index integrity.

Validates that the UI index correctly reflects enriched noun data.
Checks node counts and total xref counts match between export and index.

Environment variables:
- None (always HINT mode for UI artifacts)

Exit codes:
- 0: Always (HINT mode - non-blocking)
"""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import sys

enriched = pathlib.Path("exports/ai_nouns.enriched.json")
index = pathlib.Path("ui/derived/xrefs_index.v1.json")

out = {
    "ok": True,
    "mode": "HINT",
    "ts": dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z"),
}

if not enriched.exists() or not index.exists():
    out.update(note="artifact(s) missing; skip")
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(0)

export_data = json.loads(enriched.read_text())
index_data = json.loads(index.read_text())

en = export_data.get("nodes", [])
inodes = index_data.get("nodes", [])

ok = len(en) == len(inodes)

# spot-check total xref counts match
sumE = sum(len(n.get("xrefs") or []) for n in en)
sumI = sum(int(n.get("xref_count", 0)) for n in inodes)

ok = ok and (sumE == sumI)

out.update(
    total_nodes=len(en),
    index_nodes=len(inodes),
    xrefs_sum_export=sumE,
    xrefs_sum_index=sumI,
    ok=ok,
)

print(json.dumps(out, ensure_ascii=False))
sys.exit(0)
