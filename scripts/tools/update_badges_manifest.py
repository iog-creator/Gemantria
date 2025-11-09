#!/usr/bin/env python3

import json, sys, pathlib

MAN = pathlib.Path("evidence/badges_manifest.json")

name, path, desc = sys.argv[1], sys.argv[2], sys.argv[3]

MAN.parent.mkdir(parents=True, exist_ok=True)

doc = {"badges": []}

if MAN.exists():
    try: doc = json.loads(MAN.read_text())
    except Exception: doc = {"badges":[]}

# ensure badges key exists
if "badges" not in doc:
    doc["badges"] = []

# upsert
doc["badges"] = [b for b in doc["badges"] if b.get("name") != name]

doc["badges"].append({"name": name, "path": path, "desc": desc})

MAN.write_text(json.dumps(doc, indent=2))

print(f"OK: manifest updated → {MAN}")
