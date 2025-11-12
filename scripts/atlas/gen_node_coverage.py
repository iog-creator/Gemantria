import json, pathlib
from datetime import datetime, UTC


def rfc3339():
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


node_dir = pathlib.Path("share/atlas/nodes/node_001")
files = []
if node_dir.exists():
    for p in sorted(node_dir.glob("*")):
        if p.is_file():
            files.append(p.name)

out = {
    "schema": {"id": "atlas.node_coverage.v1", "version": 1},
    "generated_at": rfc3339(),
    "node_id": "node_001",
    "files": files,
    "counts": {"files_present": len(files)},
}

node_dir.mkdir(parents=True, exist_ok=True)
(node_dir / "coverage.json").write_text(json.dumps(out, indent=2))
print("OK wrote", str(node_dir / "coverage.json"))
