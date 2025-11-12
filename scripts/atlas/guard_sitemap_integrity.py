from __future__ import annotations

from pathlib import Path
import json, sys


ROOT = Path("share/atlas")
smp = ROOT / "sitemap.json"
ok, errs = True, []
if not smp.exists():
    print("no sitemap.json")
    sys.exit(1)


sm = json.loads(smp.read_text(encoding="utf-8"))
anchors = sm.get("anchors") or []
for a in anchors:
    if "#" not in a:
        errs.append(f"bad anchor format: {a}")
        continue
    page, frag = a.split("#", 1)
    # Add .html extension if not present
    if not page.endswith(".html"):
        page = page + ".html"
    f = ROOT / page
    if not f.exists():
        errs.append(f"missing page: {f}")
        continue
    h = f.read_text(encoding="utf-8", errors="ignore")
    token = f'id="{frag}"'
    if token not in h:
        errs.append(f"missing id #{frag} in {page}")
if errs:
    print(json.dumps({"ok": False, "errors": errs}, indent=2))
    sys.exit(2)
print(json.dumps({"ok": True, "errors": []}))
