import json
import pathlib
import time


def rfc3339():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


root = pathlib.Path("share/atlas")
root.mkdir(parents=True, exist_ok=True)

chips = (
    json.loads((root / "filter_chips.json").read_text())
    if (root / "filter_chips.json").exists()
    else {"items": []}
)

nodes_dir = root / "nodes"

nodes = (
    [p for p in nodes_dir.glob("*/provenance.json") if p.is_file()] if nodes_dir.exists() else []
)

summary = {
    "schema": {"id": "atlas.index_summary.v1", "version": 1},
    "generated_at": rfc3339(),
    "chips_total": len(chips.get("items", [])),
    "nodes_total": len(nodes),
    "badges": {
        "latency": (root / "badges/latency.json").exists(),
        "trace": (pathlib.Path("share/mcp/trace_links.json")).exists(),
    },
}

(root / "index_summary.json").write_text(json.dumps(summary, indent=2))

print("OK wrote share/atlas/index_summary.json")
