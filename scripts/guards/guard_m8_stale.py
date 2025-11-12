import json, os, time

PATH = "share/atlas/filter_chips.json"
THRESH = int(os.getenv("M8_STALE_THRESHOLD_SECONDS", "86400"))  # 24h default

now = time.time()
try:
    mtime = os.path.getmtime(PATH)
    stale = (now - mtime) > THRESH
    verdict = {"ok": not stale, "stale": stale, "threshold_sec": THRESH, "path": PATH}
except FileNotFoundError:
    verdict = {"ok": False, "stale": True, "error": "missing", "path": PATH}

os.makedirs("evidence", exist_ok=True)
with open("evidence/guard_m8_stale.verdict.json", "w") as f:
    json.dump(verdict, f, indent=2)
print(json.dumps(verdict))
