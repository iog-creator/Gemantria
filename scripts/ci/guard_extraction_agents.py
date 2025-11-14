#!/usr/bin/env python3
import json, sys, pathlib

root = pathlib.Path("agentpm/tests/extractors")
fixdir = root / "fixtures"
resp = {"ok": True, "errors": []}
# presence
for p in [root / "test_extraction_correctness.py", root / "test_extraction_provenance_e06_e10.py", fixdir]:
    if not p.exists():
        resp["ok"] = False
        resp["errors"].append(f"missing:{p}")
# size caps (hermetic hygiene)
for f in fixdir.glob("*.json"):
    if f.stat().st_size > 2048:
        resp["ok"] = False
        resp["errors"].append(f"oversize:{f.name}")
print(json.dumps(resp))
sys.exit(0 if resp["ok"] else 1)
