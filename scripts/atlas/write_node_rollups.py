import json, os
from datetime import datetime, UTC


def rfc3339_now():
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


node_dir = "share/atlas/nodes/node_001"
os.makedirs(node_dir, exist_ok=True)

rollup = {
    "schema": {"id": "atlas.node_provenance.v1", "version": 1},
    "generated_at": rfc3339_now(),
    "node_id": "node_001",
    "counts": {"traces": 1, "chips": 2},
    "filter_chip_ids": ["chip:db-backed", "chip:has-trace"],
    "trace_links": [{"title": "session-trace", "href": "../../mcp/trace_links.json"}],
}

with open(os.path.join(node_dir, "provenance.json"), "w") as f:
    json.dump(rollup, f, indent=2)
print("OK wrote", os.path.join(node_dir, "provenance.json"))
