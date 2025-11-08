#!/usr/bin/env python3
"""Index AGENTS.md files into database for search/telemetry (docs remain SSOT)."""

import os
import json
import hashlib

rows = []
for root, _, files in os.walk(".", topdown=True):
    if "AGENTS.md" in files and "__pycache__" not in root and "node_modules" not in root:
        p = os.path.join(root, "AGENTS.md")
        with open(p, "rb") as f:
            b = f.read()
        sha = hashlib.sha256(b).hexdigest()[:12]
        head = "\n".join(b.decode("utf-8", errors="ignore").splitlines()[:24])
        rows.append({"path": p, "sha256_12": sha, "excerpt": {"head": head}})

with open("tmp.agent_docs_index.json", "w", encoding="utf-8") as f:
    json.dump(rows, f)

print(f"Indexed {len(rows)} AGENTS.md files")
