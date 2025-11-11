#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

p = Path("docs/atlas/data/mcp_catalog.json")
d = json.loads(p.read_text())
eps = d.get("endpoints", [])
print("[validate] endpoints:", len(eps))
assert isinstance(eps, list) and len(eps) >= 1
print("[validate] ok")
