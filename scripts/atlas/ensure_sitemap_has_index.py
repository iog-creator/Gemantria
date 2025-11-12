import json
import time
import pathlib

root = pathlib.Path("share/atlas")
root.mkdir(parents=True, exist_ok=True)
p = root / "sitemap.json"

entries = []
if p.exists():
    try:
        entries = json.loads(p.read_text()).get("entries", [])
    except Exception:
        entries = []

if not any(e.get("href") == "index.html" for e in entries):
    entries = [{"href": "index.html", "kind": "index"}] + entries

out = {
    "schema": {"id": "atlas.sitemap.v1", "version": 1},
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "entries": entries,
}

p.write_text(json.dumps(out, indent=2))
print("OK ensured index in", p)
