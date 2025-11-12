import json, os, hashlib
from datetime import datetime, UTC


def rfc3339_now():
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def host_hash():
    h = hashlib.sha256(os.uname().nodename.encode()).hexdigest()[:8]
    return h


def try_strict_probe():
    # STRICT path: we don't fail if DB is absent; we record HINT vs STRICT
    dsn = os.getenv("GEMATRIA_DSN") or os.getenv("GEMATRIA_RO_DSN") or os.getenv("ATLAS_DSN_RO") or ""
    strict = os.getenv("STRICT_DB_PROBE", "0") == "1" or os.getenv("ENFORCE_STRICT", "0") == "1"
    mode = "STRICT" if strict and dsn else "HINT"
    # Light probe: SELECT 1 equivalent (no external calls; we only record mode + hashes)
    return {"mode": mode, "dsn_present": bool(dsn)}


out = {
    "schema": {"id": "atlas.filter_chips.v1", "version": 1},
    "generated_at": rfc3339_now(),
    "host_hash": host_hash(),
    "probe": try_strict_probe(),
    "items": [
        {
            "id": "chip:db-backed",
            "label": "DB-backed",
            "type": "source",
            "node_href": "nodes/node_001/index.html",
        },
        {
            "id": "chip:has-trace",
            "label": "Has Trace",
            "type": "state",
            "node_href": "nodes/node_001/index.html",
        },
    ],
}

os.makedirs("share/atlas", exist_ok=True)
with open("share/atlas/filter_chips.json", "w") as f:
    json.dump(out, f, indent=2)
print("OK wrote share/atlas/filter_chips.json")
