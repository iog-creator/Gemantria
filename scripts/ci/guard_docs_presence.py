#!/usr/bin/env python3

import json
import os
import sys

paths = [
    "docs/atlas/index.html",
    "docs/SSOT",
    "AGENTS.md",
    "RULES_INDEX.md",
    "docs/SSOT/SHARE_MANIFEST.json",
]

exists = {p: (os.path.isdir(p) if p.endswith("SSOT") else os.path.exists(p)) for p in paths}
ok = all(
    [
        exists["docs/atlas/index.html"],
        exists["docs/SSOT"],
        exists["AGENTS.md"],
        exists["RULES_INDEX.md"],
        exists["docs/SSOT/SHARE_MANIFEST.json"],
    ]
)

print(json.dumps({"ok": ok, "exists": exists}, indent=2))
sys.exit(0 if ok else 1)

