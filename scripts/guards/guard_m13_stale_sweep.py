import json
import os
import pathlib
import time

force = os.getenv("M13_STALE_FORCE", "0") == "1"

threshold = int(os.getenv("M13_STALE_THRESHOLD_SEC", "86400"))

now = time.time()

root = pathlib.Path("share/atlas")

stale = []

if root.exists():
    for p in root.rglob("*.json"):
        try:
            if (now - p.stat().st_mtime) > threshold:
                stale.append(p.as_posix())
        except Exception:
            pass

ok = (len(stale) == 0) and (not force)

verdict = {"ok": ok, "stale_count": len(stale), "forced": force, "threshold_sec": threshold}

pathlib.Path("evidence/guard_m13_stale_sweep.verdict.json").write_text(
    json.dumps(verdict, indent=2)
)

print(json.dumps(verdict))
