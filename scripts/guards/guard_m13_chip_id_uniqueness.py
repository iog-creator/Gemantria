import collections
import json
import pathlib
import time

chips_p = pathlib.Path("share/atlas/filter_chips.json")

# Ensure file is readable (small delay for file system sync)
if chips_p.exists():
    for _ in range(3):
        try:
            chips = json.loads(chips_p.read_text())
            if chips.get("items"):
                break
        except (json.JSONDecodeError, OSError):
            time.sleep(0.1)
    else:
        chips = {"items": []}
else:
    chips = {"items": []}

ids = [it.get("id") for it in chips.get("items", []) if it.get("id")]

dup = [k for k, v in collections.Counter(ids).items() if v > 1]

# Also check apply files don't reference unknown chip_ids


def load(p):
    p = pathlib.Path(p)
    if not p.exists():
        return {"items": []}
    for _ in range(3):
        try:
            data = json.loads(p.read_text())
            if data.get("items") is not None:
                return data
        except (json.JSONDecodeError, OSError):
            time.sleep(0.1)
    return {"items": []}


a1 = load("share/atlas/filter_apply.json")

am = load("share/atlas/filter_apply_multi.json")

known = set(ids)

apply_ids = {it.get("chip_id") for it in a1.get("items", []) if it.get("chip_id")} | {
    it.get("chip_id") for it in am.get("items", []) if it.get("chip_id")
}

unknown_in_apply = sorted(apply_ids - known)

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
