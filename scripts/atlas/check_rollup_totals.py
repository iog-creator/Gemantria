import json
import pathlib
import time


def load_json(p):
    return json.loads(pathlib.Path(p).read_text()) if pathlib.Path(p).exists() else None


chips = load_json("share/atlas/filter_chips.json") or {"items": []}
chip_ids = [it.get("id") for it in chips.get("items", []) if it.get("id")]

ok_nodes = {}

for node in ["node_001", "node_002"]:
    p = pathlib.Path(f"share/atlas/nodes/{node}/provenance.json")
    data = load_json(p) or {"counts": {"chips": 0}, "filter_chip_ids": []}
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
