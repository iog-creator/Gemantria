#!/usr/bin/env python3
"""
guard.atlas.live — HINT mode

Checks presence of dev-only live server and Make targets (non-fatal).

STRICT: same checks but still non-fatal (viewer already covers budget).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

root = Path(".")

sentinels = {
    "server": root / "scripts/mcp/http_export_server.py",
    "viewer_live_js": root / "docs/atlas/js/mcp_catalog_live.js",
}

exists = {k: p.exists() for k, p in sentinels.items()}
# Simple Makefile grep for targets
mk = (root / "Makefile").read_text()
has_server = bool(re.search(r"^atlas\.live\.server:", mk, re.M))
has_fetch = bool(re.search(r"^atlas\.live\.fetch:", mk, re.M))

report = {
    "ok_repo": all(exists.values()) and has_server and has_fetch,
    "exists": exists,
    "make": {"atlas.live.server": has_server, "atlas.live.fetch": has_fetch},
    "notes": ["HINT: Dev-only. Safe to ignore in CI; viewer remains offline-safe."],
}
print(json.dumps(report, indent=2))
sys.exit(0)
