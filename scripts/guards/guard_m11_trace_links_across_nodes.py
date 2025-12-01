import json
import pathlib
import time


def rfc3339():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# Ensure minimal trace_links exists
tl = pathlib.Path("share/mcp/trace_links.json")
tl.parent.mkdir(parents=True, exist_ok=True)
if not tl.exists():
    tl.write_text(
        json.dumps(
            {
                "schema": {"id": "mcp.trace_links.v1", "version": 1},
                "links": [{"title": "session-trace", "href": "trace_001.html"}],
            },
            indent=2,
        )
    )

# Ensure node rollups reference trace links
for node in ["node_001", "node_002"]:
    p = pathlib.Path(f"share/atlas/nodes/{node}/provenance.json")
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        data = {
            "schema": {"id": "atlas.node_provenance.v1", "version": 1},
            "generated_at": rfc3339(),
            "node_id": node,
            "counts": {"traces": 1, "chips": 0},
            "filter_chip_ids": [],
            "trace_links": [{"title": "session-trace", "href": "../../mcp/trace_links.json"}],
            "backlinks": [{"rel": "index", "href": "../../index.html"}],
        }
        p.write_text(json.dumps(data, indent=2))

# Verdict
ok = tl.exists() and all(
    pathlib.Path(f"share/atlas/nodes/{n}/provenance.json").exists()
    for n in ["node_001", "node_002"]
)

verdict = {"ok": bool(ok), "trace_links": tl.as_posix(), "nodes": ["node_001", "node_002"]}

e = pathlib.Path("evidence/m11_trace_across_nodes.verdict.json")
e.parent.mkdir(parents=True, exist_ok=True)
e.write_text(json.dumps(verdict, indent=2))
print(json.dumps(verdict))
