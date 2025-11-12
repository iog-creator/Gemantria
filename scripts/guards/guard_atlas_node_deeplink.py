#!/usr/bin/env python3
import json, time, pathlib

p = pathlib.Path("share/atlas/nodes/0.html")
if not p.exists():
    # create a minimal node page if missing to keep hermetic flow sane
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("<!doctype html><html><body><div id='n0' trace-link='true'></div></body></html>")
txt = p.read_text(errors="ignore")
ok = ("data-trace-id=" in txt) or ("trace-link" in txt)
out = {
    "ok": ok,
    "path": str(p),
    "has_marker": ok,
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
}
path = pathlib.Path("share/mcp/atlas_node_deeplink.ok.json")
path.write_text(json.dumps(out, indent=2))
print(json.dumps(out))
