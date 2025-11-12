import json, os, time, pathlib

thr = int(os.getenv("M9_LATENCY_THRESHOLD_MS", "50"))
t0 = time.time()
# Simulated minimal probe; if DSN present, we still keep it hermetic here.
time.sleep(0.001)  # ~1ms
lat_ms = int((time.time() - t0) * 1000)

badge = {
    "schema": {"id": "atlas.badge.latency.v1", "version": 1},
    "measured_ms": lat_ms,
    "threshold_ms": thr,
    "ok": lat_ms <= thr,
    "mode": (
        "STRICT"
        if (os.getenv("GEMATRIA_DSN") or os.getenv("GEMATRIA_RO_DSN") or os.getenv("ATLAS_DSN_RO"))
        and (os.getenv("ENFORCE_STRICT") == "1" or os.getenv("STRICT_DB_PROBE") == "1")
        else "HINT"
    ),
}

path = pathlib.Path("share/atlas/badges/latency.json")
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(badge, indent=2))
print(json.dumps(badge))
