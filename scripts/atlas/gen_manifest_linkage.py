import json
import pathlib
import time


def rfc3339():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


artifacts = [
    "share/atlas/sitemap.json",
    "share/atlas/index_summary.json",
    "share/atlas/filter_chips.json",
    "share/atlas/filter_apply.json",
    "share/atlas/filter_apply_multi.json",
]

links = [{"path": a, "exists": pathlib.Path(a).exists()} for a in artifacts]

out = {"schema": {"id": "share.manifest_linkage.v1", "version": 1}, "generated_at": rfc3339(), "links": links}

p = pathlib.Path("share/manifest_linkage.json")
p.write_text(json.dumps(out, indent=2))

print("OK wrote", p)
