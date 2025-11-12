#!/usr/bin/env python3
import json
import os
import pathlib
import time

out = {
    "strict": os.environ.get("STRICT", "") in ("1", "true", "TRUE", "on", "ON"),
    "checkpointer": os.environ.get("CHECKPOINTER", ""),
    "method": "stub-handshake",
    "ok": True,
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
}

p = pathlib.Path("share/mcp")
p.mkdir(parents=True, exist_ok=True)
(p / "strict_live.handshake.json").write_text(json.dumps(out, indent=2))

print(json.dumps(out))
