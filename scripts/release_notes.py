#!/usr/bin/env python3
import glob, hashlib, json

paths = sorted(glob.glob("share/evidence/*summary_*.json"))[-5:]
rows = []
for p in paths:
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()[:12]
    rows.append({"file": p, "sha256_12": h})
print(json.dumps({"evidence": rows}, indent=2))
