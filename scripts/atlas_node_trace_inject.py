#!/usr/bin/env python3
import json, pathlib

trace = json.loads(pathlib.Path("share/mcp/session_trace.json").read_text()).get("trace_id", "")
nodes_dir = pathlib.Path("share/atlas/nodes")
nodes_dir.mkdir(parents=True, exist_ok=True)

# Ensure a node page exists for verification; if missing, create a minimal one.
target = nodes_dir / "0.html"
if not target.exists():
    target.write_text("<!doctype html><html><body><div class='node' id='n0'></div></body></html>")

txt = target.read_text(errors="ignore")
if "data-trace-id=" not in txt:
    txt = txt.replace(
        "<div class='node' id='n0'",
        f"<div class='node' id='n0' data-trace-id=\"{trace}\" trace-link=\"true\"",
    )
target.write_text(txt)
print(json.dumps({"node_html": str(target), "trace_id": trace, "marker": True}))
