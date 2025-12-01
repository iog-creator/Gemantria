import json
import pathlib

root = pathlib.Path("share/atlas")

chips = (
    json.loads((root / "filter_chips.json").read_text())
    if (root / "filter_chips.json").exists()
    else {"items": []}
)

chip_ids = {it.get("id") for it in chips.get("items", []) if it.get("id")}

nodes_dir = root / "nodes"

seen = set()

if nodes_dir.exists():
    for pv in nodes_dir.glob("*/provenance.json"):
        data = json.loads(pv.read_text())
        seen.update(data.get("filter_chip_ids", []))

ok = chip_ids.issubset(seen)

verdict = {"ok": ok, "chip_count": len(chip_ids), "covered_in_nodes": len(chip_ids & seen)}

path = pathlib.Path("evidence/guard_m12_chip_coverage.verdict.json")
path.parent.mkdir(parents=True, exist_ok=True)

path.write_text(json.dumps(verdict, indent=2))

print(json.dumps(verdict))
