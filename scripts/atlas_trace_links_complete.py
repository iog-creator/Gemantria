#!/usr/bin/env python3
import json, pathlib

base = pathlib.Path("share/atlas")
idx = base / "index.html"
n0 = base / "nodes/0.html"
# Try to read session trace id if available
trace = None
st = pathlib.Path("share/mcp/session_trace.json")
if st.exists():
    try:
        trace = json.loads(st.read_text()).get("trace_id")
    except Exception:
        pass
links = []
if idx.exists():
    links.append({"path": str(idx), "trace_id": trace, "rel": "index"})
if n0.exists():
    links.append({"path": str(n0), "trace_id": trace, "rel": "node"})
out = {"links": links, "count": len(links), "complete": bool(len(links) >= 2)}
(base / "trace_links.json").write_text(json.dumps(out, indent=2))
print(json.dumps(out))
