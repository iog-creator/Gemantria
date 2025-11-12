#!/usr/bin/env python3
import json, os, time, pathlib, hashlib

seed = f"{os.environ.get('USER', 'user')}|{time.strftime('%Y-%m-%d')}|{os.getpid()}"
trace_id = hashlib.sha256(seed.encode()).hexdigest()[:12]
out = {"trace_id": trace_id, "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
p = pathlib.Path("share/mcp")
p.mkdir(parents=True, exist_ok=True)
(p / "session_trace.json").write_text(json.dumps(out, indent=2))
print(json.dumps(out))
