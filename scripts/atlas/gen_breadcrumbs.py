import json
import time
import pathlib


def rfc3339():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


crumbs = [
    {"path": ["index"], "href": "index.html"},
    {"path": ["index", "node_001"], "href": "nodes/node_001/index.html"},
    {"path": ["index", "node_002"], "href": "nodes/node_002/index.html"},
]

out = {
    "schema": {"id": "atlas.breadcrumbs.v1", "version": 1},
    "generated_at": rfc3339(),
    "breadcrumbs": crumbs,
}

p = pathlib.Path("share/atlas/breadcrumbs.json")
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps(out, indent=2))
print("OK wrote", p)
