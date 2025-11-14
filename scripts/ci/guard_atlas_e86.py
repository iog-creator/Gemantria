#!/usr/bin/env python3
import json, os, sys

path = "share/atlas/control_plane/e86_compliance_summary.json"
if not os.path.exists(path):
    print(json.dumps({"ok": False, "errors": ["missing_export"]}))
    sys.exit(1)

try:
    data = json.load(open(path))
except Exception as e:
    print(json.dumps({"ok": False, "errors": [f"json_error: {e}"]}))
    sys.exit(1)

errors = []
if data.get("episode") != "E86":
    errors.append("wrong_episode")
if "metrics" not in data:
    errors.append("missing_metrics")

if errors:
    print(json.dumps({"ok": False, "errors": errors}))
    sys.exit(1)

print(json.dumps({"ok": True, "errors": []}))
