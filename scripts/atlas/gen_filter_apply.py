import json, os, pathlib
from datetime import datetime, UTC


def rfc3339_now():
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


path = pathlib.Path("share/atlas/filter_chips.json")
chips = {"items": []}
if path.exists():
    chips = json.loads(path.read_text())

mapping = []
for it in chips.get("items", []):
    cid = it.get("id")
    if not cid:
        continue
    # Minimal, deterministic query descriptor; STRICT/HINT safe.
    mapping.append(
        {
            "chip_id": cid,
            "query": {"kind": "sql", "text": "SELECT * FROM mcp_catalog LIMIT 10"},
            "applies_to": it.get("node_href", "index.html"),
        }
    )

out = {
    "schema": {"id": "atlas.filter_apply.v1", "version": 1},
    "generated_at": rfc3339_now(),
    "items": mapping,
}

os.makedirs("share/atlas", exist_ok=True)
with open("share/atlas/filter_apply.json", "w") as f:
    json.dump(out, f, indent=2)
print("OK wrote share/atlas/filter_apply.json")
