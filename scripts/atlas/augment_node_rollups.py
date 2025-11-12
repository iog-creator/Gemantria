import json, pathlib
from datetime import datetime, UTC


def rfc3339_now():
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


nodes = [("node_001", pathlib.Path("share/atlas/nodes/node_001/provenance.json"))]
chips_path = pathlib.Path("share/atlas/filter_chips.json")
chips = {"items": []}
if chips_path.exists():
    chips = json.loads(chips_path.read_text())

chip_ids = [it.get("id") for it in chips.get("items", []) if it.get("id")]

for node_id, p in nodes:
    p.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "schema": {"id": "atlas.node_provenance.v1", "version": 1},
        "generated_at": rfc3339_now(),
        "node_id": node_id,
        "counts": {"traces": 1, "chips": len(chip_ids)},
        "filter_chip_ids": chip_ids,
        "trace_links": [{"title": "session-trace", "href": "../../mcp/trace_links.json"}],
        "backlinks": [{"rel": "index", "href": "../../index.html"}],
    }
    p.write_text(json.dumps(data, indent=2))
    print("OK wrote", str(p))
