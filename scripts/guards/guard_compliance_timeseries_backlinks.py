#!/usr/bin/env python3
import json, os, sys

EXPORT_PATH = "share/atlas/control_plane/compliance_timeseries.json"
HTML_TS = "docs/atlas/dashboard/compliance_timeseries.html"
HTML_HM = "docs/atlas/dashboard/compliance_heatmap.html"

errors = []

if not os.path.exists(EXPORT_PATH):
    errors.append("missing_export")

for path in (HTML_TS, HTML_HM):
    if not os.path.exists(path):
        errors.append(f"missing_html:{path}")

if os.path.exists(EXPORT_PATH):
    try:
        data = json.load(open(EXPORT_PATH))
        if data.get("episode") != "E87":
            errors.append("wrong_episode")
        if "series" not in data:
            errors.append("missing_series")
    except Exception as e:
        errors.append(f"json_error:{e}")

if errors:
    print(json.dumps({"ok": False, "errors": errors}))
    sys.exit(1)

print(json.dumps({"ok": True, "errors": []}))
