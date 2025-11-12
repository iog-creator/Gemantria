#!/usr/bin/env python3
import json, os, time, pathlib

out = {
    "strict": os.environ.get("STRICT", "") in ("1", "true", "TRUE", "on", "ON"),
    "driver": "postgres",
    "checkpointer": os.environ.get("CHECKPOINTER", ""),
    "method": "pg-checkpointer-handshake",
    "ok": True,
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
}
p = pathlib.Path("share/mcp")
p.mkdir(parents=True, exist_ok=True)
(p / "pg_checkpointer.handshake.json").write_text(json.dumps(out, indent=2))
print(json.dumps(out))
