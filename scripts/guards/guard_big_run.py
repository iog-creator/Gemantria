#!/usr/bin/env python3
import json, os, sys, pathlib

THRESH = int(os.getenv("BIGRUN_THRESHOLD_NOUNS", "2000"))  # default safety limit
CONFIRM = os.getenv("CONFIRM_BIGRUN", "")
path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "exports/ai_nouns.db_morph.json")
if not path.exists():
    print(f"guard_big_run: file not found: {path} — SKIP", file=sys.stderr)
    sys.exit(0)
data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
n = len(data.get("nodes", []) or [])
if n > THRESH and CONFIRM.upper() != "YES":
    print(f"ERROR: big-run blocked ({n} nouns > {THRESH}). Set CONFIRM_BIGRUN=YES to proceed.", file=sys.stderr)
    sys.exit(2)
print(f"OK: {n} nouns (<= {THRESH}) or confirmation provided.")
