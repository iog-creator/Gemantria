import json, os, time, pathlib

PATH = "share/atlas/nodes/node_001/provenance.json"
THRESH = int(os.getenv("M9_ROLLUP_STALE_THRESHOLD_SECONDS", "86400"))

p = pathlib.Path(PATH)
if not p.exists():
    verdict = {"ok": False, "stale": True, "error": "missing", "path": PATH}
else:
    mtime = p.stat().st_mtime
    stale = (time.time() - mtime) > THRESH
    verdict = {"ok": not stale, "stale": stale, "threshold_sec": THRESH, "path": PATH}

path_out = pathlib.Path("evidence/guard_m9_rollup_stale.verdict.json")
path_out.parent.mkdir(parents=True, exist_ok=True)
path_out.write_text(json.dumps(verdict, indent=2))
print(json.dumps(verdict))
