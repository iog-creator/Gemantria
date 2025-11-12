#!/usr/bin/env python3
import json, pathlib

base = pathlib.Path("share/atlas")
links = []
trace = None
st = pathlib.Path("share/mcp/session_trace.json")
if st.exists():
    trace = json.loads(st.read_text()).get("trace_id")
if (base / "index.html").exists():
    links.append({"path": "share/atlas/index.html", "trace_id": trace, "rel": "index"})
n0 = base / "nodes/0.html"
if n0.exists():
    links.append({"path": "share/atlas/nodes/0.html", "trace_id": trace, "rel": "node"})
out = {"links": links, "count": len(links)}
(base).mkdir(parents=True, exist_ok=True)
(base / "trace_links.json").write_text(json.dumps(out, indent=2))
print(json.dumps(out))
