#!/usr/bin/env python3
import json, time, pathlib

paths = [pathlib.Path("share/atlas/index.html"), pathlib.Path("share/atlas/nodes/0.html")]
details, ok = [], False
for q in paths:
    if q.exists():
        t = q.read_text(errors="ignore")
        has = ("data-trace-id=" in t) or ("trace-link" in t)
        ok = ok or has
        details.append({"path": str(q), "has_marker": has})
    else:
        details.append({"path": str(q), "missing": True})
out = {"ok": ok, "details": details, "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
path = pathlib.Path("share/mcp/trace_link.guard.json")
path.write_text(json.dumps(out, indent=2))
print(json.dumps(out))
