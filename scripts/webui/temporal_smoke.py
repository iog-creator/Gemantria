#!/usr/bin/env python3

import json, pathlib

p = pathlib.Path("build/webui_bundle/bundle.json")
if p.exists():
    meta = json.loads(p.read_text(encoding="utf-8")).get("meta", {})
    print("[webui.temporal] meta.temporal =", meta.get("temporal"))
else:
    print("[webui.temporal] no bundle present (no exports) — OK")
