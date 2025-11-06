#!/usr/bin/env python3

import json, sys, re, pathlib

PATH = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "exports/ai_nouns.db_morph.json")
if not PATH.exists():
    print("guard_nouns_hebrew_sanity: envelope absent; SKIP.")
    sys.exit(0)

env = json.load(open(PATH, encoding="utf-8"))
nodes = env.get("nodes", [])

if not nodes:
    print("ERROR: envelope has zero nodes", file=sys.stderr)
    sys.exit(2)

hebrew = re.compile(r"[\u0590-\u05FF]")
sample = nodes[: max(25, min(200, len(nodes)))]
ok = sum(1 for n in sample if hebrew.search(n.get("surface") or n.get("hebrew_text") or ""))

if ok < max(10, int(len(sample) * 0.7)):
    print(f"ERROR: too few Hebrew surfaces in sample ({ok}/{len(sample)})", file=sys.stderr)
    sys.exit(2)

print(f"OK: Hebrew surfaces sanity {ok}/{len(sample)}.")
