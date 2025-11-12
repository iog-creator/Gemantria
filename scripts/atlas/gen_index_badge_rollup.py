import json
import pathlib
import time


def rfc3339():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


root = pathlib.Path("share/atlas")
root.mkdir(parents=True, exist_ok=True)

lat_p = root / "badges/latency.json"

trc_p = root / "badges/trace.json"

lat = json.loads(lat_p.read_text()) if lat_p.exists() else {"present": False}

trc = json.loads(trc_p.read_text()) if trc_p.exists() else {"present": False}

roll = {
    "schema": {"id": "atlas.badges.rollup.v1", "version": 1},
    "generated_at": rfc3339(),
    "badges": {
        "latency_present": bool(lat.get("schema")) or bool(lat.get("present")),
        "trace_present": bool(trc.get("present")),
    },
}

roll["ok"] = roll["badges"]["latency_present"] and roll["badges"]["trace_present"]

out = root / "badges/index_rollup.json"

out.write_text(json.dumps(roll, indent=2))

print("OK wrote", out)
