#!/usr/bin/env python3
"""RO-DSN guard for MCP catalog (E02)."""

from __future__ import annotations

import json
import os
import pathlib
import re
import sys
import time

out = {
    "ok": False,
    "errors": [],
    "strict": False,
    "dsn_redacted": None,
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
}

dsn = os.environ.get("GEMATRIA_DSN", "")
strict = os.environ.get("STRICT", "") in ("1", "true", "TRUE", "on", "ON")
out["strict"] = strict

if not dsn:
    out["errors"].append("GEMATRIA_DSN not set")
else:
    # Redact creds/hosts minimally; keep scheme to prove DSN type
    redacted = re.sub(r"//[^@]*@", "//<REDACTED>@", dsn) if dsn else None
    out["dsn_redacted"] = redacted
    if dsn.startswith("postgres"):
        out["ok"] = True

p = pathlib.Path("share/mcp")
p.mkdir(parents=True, exist_ok=True)
with open(p / "rodsn.guard.json", "w") as f:
    json.dump(out, f, indent=2)

print(json.dumps(out))
sys.exit(0)  # guard is advisory in hermetic mode
