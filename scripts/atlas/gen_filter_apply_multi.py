import json, pathlib
from datetime import datetime, UTC


def rfc3339():
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


chips_path = pathlib.Path("share/atlas/filter_chips.json")
chips = {"items": []}
if chips_path.exists():
    chips = json.loads(chips_path.read_text())

items = []
for it in chips.get("items", []):
    cid = it.get("id")
    if not cid:
        continue
    items.append(
        {
            "chip_id": cid,
            "queries": [
                {"kind": "sql", "text": "SELECT id,label FROM mcp_catalog LIMIT 5"},
                {"kind": "sql", "text": "SELECT COUNT(*) AS n FROM mcp_catalog"},
            ],
        }
    )

out = {
    "schema": {"id": "atlas.filter_apply_multi.v1", "version": 1},
    "generated_at": rfc3339(),
    "items": items,
}

path = pathlib.Path("share/atlas/filter_apply_multi.json")
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(out, indent=2))
print("OK wrote", str(path))
