#!/usr/bin/env python3
import json, time, pathlib

idx = pathlib.Path("share/atlas/index.html")
node = pathlib.Path("share/atlas/nodes/0.html")
ok = False
details = []
for p in (idx, node):
    if p.exists():
        t = p.read_text(errors="ignore")
        hit = ("data-trace-id=" in t) or ("trace-link" in t)
        ok = ok or hit
        details.append({"path": str(p), "has_marker": bool(hit)})
    else:
        details.append({"path": str(p), "missing": True})
out = {"ok": ok, "details": details, "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
op = pathlib.Path("share/mcp/trace_link.guard.json")
op.write_text(json.dumps(out, indent=2))
print(json.dumps(out))
