#!/usr/bin/env python3

import sys, re, json, pathlib

LOG = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "share/evidence/e2e_smoke.log")
if not LOG.exists():
    print("guard_enrichment_names: log absent; SKIP (no-op).")
    sys.exit(0)

txt = LOG.read_text(encoding="utf-8", errors="ignore")
# quick hits

if re.search(r"\bUnknown\b", txt):
    print("ERROR: Found 'Unknown' in enrichment logs; name resolution regression.", file=sys.stderr)
    sys.exit(2)

# look for JSON lines with noun fields in enrichment messages

bad = 0
for line in txt.splitlines():
    if '"noun"' in line and '"noun_enriched"' in line:
        try:
            data = json.loads(line[line.find("{") :])
            noun = data.get("noun") or data.get("name")
            if noun in (None, "", "Unknown"):
                bad += 1
        except Exception:
            continue

if bad:
    print(f"ERROR: {bad} enrichment lines missing noun names.", file=sys.stderr)
    sys.exit(2)

print("OK: enrichment names present; no 'Unknown' found.")
