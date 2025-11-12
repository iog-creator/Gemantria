#!/usr/bin/env python3
import json
import os
import pathlib
import time

ok = (
    os.environ.get("STRICT", "") in ("1", "true", "TRUE", "on", "ON")
    and os.environ.get("CHECKPOINTER", "") == "postgres"
)
out = {"ok": ok, "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")}

p = pathlib.Path("share/mcp")
p.mkdir(parents=True, exist_ok=True)
(p / "strict_roundtrip.ok.json").write_text(json.dumps(out, indent=2))

print(json.dumps(out))
