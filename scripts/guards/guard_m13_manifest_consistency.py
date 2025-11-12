import json
import pathlib

man_p = pathlib.Path("share/manifest_linkage.json")

required = {
    "share/atlas/sitemap.json",
    "share/atlas/index_summary.json",
    "share/atlas/filter_chips.json",
    "share/atlas/filter_apply.json",
    "share/atlas/filter_apply_multi.json",
}

if not man_p.exists():
    verdict = {"ok": False, "error": "missing_manifest"}
else:
    man = json.loads(man_p.read_text())
    links = {it["path"]: it.get("exists", False) for it in man.get("links", [])}
    missing = sorted([p for p in required if not links.get(p, False) or not pathlib.Path(p).exists()])
    verdict = {"ok": len(missing) == 0, "missing": missing, "checked": len(required)}

pathlib.Path("evidence/guard_m13_manifest_consistency.verdict.json").write_text(json.dumps(verdict, indent=2))

print(json.dumps(verdict))
