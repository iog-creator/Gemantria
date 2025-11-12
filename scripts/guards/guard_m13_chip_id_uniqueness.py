import collections
import json
import pathlib

chips_p = pathlib.Path("share/atlas/filter_chips.json")

chips = json.loads(chips_p.read_text()) if chips_p.exists() else {"items": []}

ids = [it.get("id") for it in chips.get("items", []) if it.get("id")]

dup = [k for k, v in collections.Counter(ids).items() if v > 1]

# Also check apply files don't reference unknown chip_ids


def load(p):
    p = pathlib.Path(p)
    return json.loads(p.read_text()) if p.exists() else {"items": []}


a1 = load("share/atlas/filter_apply.json")

am = load("share/atlas/filter_apply_multi.json")

known = set(ids)

unknown_in_apply = sorted(
    {it.get("chip_id") for it in a1.get("items", []) if it.get("chip_id")}
    | {it.get("chip_id") for it in am.get("items", []) if it.get("chip_id")} - known
)

ok = (len(dup) == 0) and (len(unknown_in_apply) == 0)

verdict = {
    "ok": ok,
    "duplicates_count": len(dup),
    "unknown_in_apply_count": len(unknown_in_apply),
    "duplicates": dup,
    "unknown_in_apply": unknown_in_apply,
}

pathlib.Path("evidence/guard_m13_chip_id_uniqueness.verdict.json").write_text(json.dumps(verdict, indent=2))

print(json.dumps(verdict))
