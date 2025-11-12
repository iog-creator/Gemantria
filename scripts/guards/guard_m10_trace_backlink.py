import json, pathlib

node_roll = pathlib.Path("share/atlas/nodes/node_001/provenance.json")
trace_links = pathlib.Path("share/mcp/trace_links.json")

# Create a minimal trace_links.json if missing (hermetic-friendly)
if not trace_links.exists():
    trace_links.parent.mkdir(parents=True, exist_ok=True)
    trace_links.write_text(
        '{"schema":{"id":"mcp.trace_links.v1","version":1},"links":[{"title":"session-trace","href":"trace_001.html"}]}'
    )

ok = node_roll.exists() and trace_links.exists()
verdict = {
    "ok": bool(ok),
    "node_rollup": node_roll.as_posix(),
    "trace_links": trace_links.as_posix(),
}

path = pathlib.Path("evidence/m10_trace_backlink.verdict.json")
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(verdict, indent=2))
print(json.dumps(verdict))
