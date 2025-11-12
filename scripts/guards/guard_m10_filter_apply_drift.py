import json, os, pathlib

force = os.getenv("M10_DRIFT_FORCE", "0") == "1"

chips = (
    json.loads(pathlib.Path("share/atlas/filter_chips.json").read_text())
    if pathlib.Path("share/atlas/filter_chips.json").exists()
    else {"items": []}
)
apply1 = (
    json.loads(pathlib.Path("share/atlas/filter_apply.json").read_text())
    if pathlib.Path("share/atlas/filter_apply.json").exists()
    else {"items": []}
)
applym = (
    json.loads(pathlib.Path("share/atlas/filter_apply_multi.json").read_text())
    if pathlib.Path("share/atlas/filter_apply_multi.json").exists()
    else {"items": []}
)

chip_ids = {it.get("id") for it in chips.get("items", []) if it.get("id")}
a1_ids = {it.get("chip_id") for it in apply1.get("items", []) if it.get("chip_id")}
am_ids = {it.get("chip_id") for it in applym.get("items", []) if it.get("chip_id")}

ok = chip_ids.issubset(a1_ids) and chip_ids.issubset(am_ids) and (not force)

verdict = {
    "ok": bool(ok),
    "chips": len(chip_ids),
    "apply": len(a1_ids),
    "apply_multi": len(am_ids),
    "forced": force,
}

path = pathlib.Path("evidence/guard_m10_filter_apply_drift.verdict.json")
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(verdict, indent=2))
print(json.dumps(verdict))
