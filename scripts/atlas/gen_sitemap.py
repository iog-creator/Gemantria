import json, pathlib
from datetime import datetime, UTC


def rfc3339():
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


root = pathlib.Path("share/atlas")
nodes_dir = root / "nodes"
entries = []

# canonical index
entries.append({"href": "index.html", "kind": "index"})

# enumerate known node artifacts (minimal)
p = nodes_dir / "node_001" / "provenance.json"
if p.exists():
    entries.append({"href": "nodes/node_001/provenance.json", "kind": "node-proof"})

out = {
    "schema": {"id": "atlas.sitemap.v1", "version": 1},
    "generated_at": rfc3339(),
    "entries": entries,
}

root.mkdir(parents=True, exist_ok=True)
with open(root / "sitemap.json", "w") as f:
    json.dump(out, f, indent=2)
print("OK wrote share/atlas/sitemap.json")
