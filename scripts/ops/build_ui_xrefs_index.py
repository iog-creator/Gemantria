#!/usr/bin/env python3
"""Build UI-ready cross-reference index from enriched nouns.

Creates a lightweight index optimized for visualization components.
Extracts only essential fields: Hebrew text, gematria, xref counts, and xref arrays.

Usage:
    python3 scripts/ops/build_ui_xrefs_index.py

Reads:  exports/ai_nouns.enriched.json
Writes: ui/derived/xrefs_index.v1.json
Output: JSON summary to stdout
"""

from __future__ import annotations

import json
import pathlib
import sys

src = pathlib.Path("exports/ai_nouns.enriched.json")
dst = pathlib.Path("ui/derived/xrefs_index.v1.json")

if not src.exists():
    print(json.dumps({"ok": True, "note": "missing enriched export; skip"}))
    sys.exit(0)

data = json.loads(src.read_text())

out = {
    "schema": "ui-xrefs-index.v1",
    "generated_at": data.get("generated_at"),
    "total_nodes": len(data.get("nodes", [])),
    "nodes": [
        {
            "he": n.get("hebrew"),
            "gm": n.get("gematria"),
            "xref_count": len(n.get("xrefs") or []),
            "xrefs": n.get("xrefs") or [],
        }
        for n in data.get("nodes", [])
    ],
}

dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_text(json.dumps(out, ensure_ascii=False, indent=2))
print(json.dumps({"ok": True, "file": str(dst), "total_nodes": out["total_nodes"]}))
