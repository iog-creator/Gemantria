#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

root = Path(".")
html = root / "docs/atlas/mcp_catalog_view.html"
js = root / "docs/atlas/js/mcp_catalog_viewer.js"
data = root / "docs/atlas/data/mcp_catalog.json"

exists = {"html": html.exists(), "js": js.exists(), "json": data.exists()}
ok = all(exists.values())

endpoints = None
notes = []

if exists["json"]:
    try:
        j = json.loads(data.read_text())
        endpoints = len(j.get("endpoints", []))
        if endpoints is not None and endpoints > 12:
            ok = False
            notes.append("Budget exceeded: endpoints>12")
    except Exception as e:
        ok = False
        notes.append(f"JSON parse error: {e}")

report = {"ok_repo": ok, "exists": exists, "endpoints": endpoints, "notes": notes}
print(json.dumps(report, indent=2))
sys.exit(0 if ok else 1)
