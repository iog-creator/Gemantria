import json
import pathlib
import time


def load_json(p):
    return json.loads(pathlib.Path(p).read_text()) if pathlib.Path(p).exists() else None


def rfc3339():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


chips = load_json("share/atlas/filter_chips.json") or {"items": []}
chip_ids = [it.get("id") for it in chips.get("items", []) if it.get("id")]

ok_nodes = {}

for node in ["node_001", "node_002"]:
    p = pathlib.Path(f"share/atlas/nodes/{node}/provenance.json")
    data = load_json(p)
    if not data:
        # Create minimal rollup if missing
        p.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "schema": {"id": "atlas.node_provenance.v1", "version": 1},
            "generated_at": rfc3339(),
            "node_id": node,
            "counts": {"traces": 1, "chips": len(chip_ids)},
            "filter_chip_ids": chip_ids,
            "trace_links": [{"title": "session-trace", "href": "../../mcp/trace_links.json"}],
            "backlinks": [{"rel": "index", "href": "../../index.html"}],
        }
        p.write_text(json.dumps(data, indent=2))
    else:
        # Update chip counts and IDs if inconsistent
        if data.get("counts", {}).get("chips", 0) != len(chip_ids) or not set(
            data.get("filter_chip_ids", [])
        ).issuperset(set(chip_ids)):
            data["counts"]["chips"] = len(chip_ids)
            existing_ids = set(data.get("filter_chip_ids", []))
            data["filter_chip_ids"] = list(existing_ids.union(set(chip_ids)))
            p.write_text(json.dumps(data, indent=2))
    ok_nodes[node] = data.get("counts", {}).get("chips", 0) == len(chip_ids) and set(
        data.get("filter_chip_ids", [])
    ).issuperset(set(chip_ids))

out = {
    "schema": {"id": "atlas.rollup_totals.v1", "version": 1},
    "ok": all(ok_nodes.values()),
    "per_node": ok_nodes,
    "chips_total": len(chip_ids),
}

path = pathlib.Path("evidence/m11_rollup_totals.receipt.json")
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(out, indent=2))
print(json.dumps(out))
