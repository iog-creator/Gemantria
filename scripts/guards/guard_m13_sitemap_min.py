import json
import os
import pathlib

min_required = int(os.getenv("M13_SITEMAP_MIN", "2"))

p = pathlib.Path("share/atlas/sitemap.json")

count = 0

if p.exists():
    try:
        count = len(json.loads(p.read_text()).get("entries", []))
    except Exception:
        count = 0

ok = count >= min_required

verdict = {"ok": ok, "count": count, "min_required": min_required}

pathlib.Path("evidence/guard_m13_sitemap_min.verdict.json").write_text(
    json.dumps(verdict, indent=2)
)

print(json.dumps(verdict))
