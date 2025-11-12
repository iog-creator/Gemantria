import json
import pathlib


def load(p):
    return json.loads(pathlib.Path(p).read_text()) if pathlib.Path(p).exists() else {"items": []}


chips = load("share/atlas/filter_chips.json")
a1 = load("share/atlas/filter_apply.json")
am = load("share/atlas/filter_apply_multi.json")

chip_ids = {it.get("id") for it in chips.get("items", []) if it.get("id")}

a1_ids = {it.get("chip_id") for it in a1.get("items", []) if it.get("chip_id")}

am_ids = {it.get("chip_id") for it in am.get("items", []) if it.get("chip_id")}

ok = chip_ids == (chip_ids & a1_ids) and chip_ids == (chip_ids & am_ids)

verdict = {"ok": ok, "chips": len(chip_ids), "apply": len(a1_ids), "apply_multi": len(am_ids)}

path = pathlib.Path("evidence/guard_m12_filter_apply_roundtrip.verdict.json")
path.parent.mkdir(parents=True, exist_ok=True)

path.write_text(json.dumps(verdict, indent=2))

print(json.dumps(verdict))
