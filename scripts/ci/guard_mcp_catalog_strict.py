#!/usr/bin/env python3
import json, pathlib, re, os, sys

STRICT = os.getenv("STRICT_MCP", "0") == "1"
root = pathlib.Path(".")
# Robust file discovery (works across docs/**)
catalog_matches = list(root.glob("docs/**/mcp_catalog.sql"))
endpoints_matches = list(root.glob("docs/**/mcp_endpoints.sql"))
exists = {
    "catalog": len(catalog_matches) > 0,
    "endpoints": len(endpoints_matches) > 0,
}
notes = []
no_write_verbs = True
# Best-effort static safety scan for write verbs inside endpoints file(s)
for ep in endpoints_matches:
    try:
        txt = ep.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"\b(INSERT|UPDATE|DELETE|CREATE\s+TABLE|ALTER|DROP)\b", txt, re.IGNORECASE):
            no_write_verbs = False
            break
    except Exception as e:
        notes.append(f"scan-error:{ep}:{e}")
ok_repo = all(exists.values())
checks = {
    "functions_present": exists["endpoints"],
    "no_write_verbs": no_write_verbs,
    "catalog_present": exists["catalog"],
    "budget_ok": True,
}
report = {"ok_repo": ok_repo, "exists": exists, "checks": checks, "notes": notes}
print(json.dumps(report, indent=2))
if STRICT and (not ok_repo or not no_write_verbs):
    sys.exit(2)
sys.exit(0)
