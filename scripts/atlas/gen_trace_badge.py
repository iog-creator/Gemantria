import json
import pathlib
import time


def rfc3339():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


badge = {
    "schema": {"id": "atlas.badge.trace.v1", "version": 1},
    "generated_at": rfc3339(),
    "present": pathlib.Path("share/mcp/trace_links.json").exists(),
}

p = pathlib.Path("share/atlas/badges/trace.json")
p.parent.mkdir(parents=True, exist_ok=True)

p.write_text(json.dumps(badge, indent=2))

print("OK wrote", p)
