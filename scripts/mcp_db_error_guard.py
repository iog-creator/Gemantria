#!/usr/bin/env python3
import json, time, pathlib

out = {"ok": False, "error": "simulated-or-captured", "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
p = pathlib.Path("share/mcp")
p.mkdir(parents=True, exist_ok=True)
(p / "db_error.guard.json").write_text(json.dumps(out, indent=2))
print(json.dumps(out))
