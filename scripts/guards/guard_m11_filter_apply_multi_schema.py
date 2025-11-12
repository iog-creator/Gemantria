import json
import os
import pathlib

min_q = int(os.getenv("M11_APPLY_MULTI_MIN_QUERIES", "2"))
p = pathlib.Path("share/atlas/filter_apply_multi.json")

if not p.exists():
    verdict = {"ok": False, "error": "missing", "path": str(p)}
else:
    data = json.loads(p.read_text())
    items = data.get("items", [])
    ok = bool(items) and all(isinstance(it.get("queries", []), list) and len(it["queries"]) >= min_q for it in items)
    verdict = {"ok": ok, "min_queries": min_q, "items": len(items)}

out = pathlib.Path("evidence/guard_m11_apply_multi_schema.verdict.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(verdict, indent=2))
print(json.dumps(verdict))
