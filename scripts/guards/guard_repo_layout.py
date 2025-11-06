#!/usr/bin/env python3

import sys, os

NEEDED = ["scripts", "src", "tests", "webui"]
missing = [d for d in NEEDED if not os.path.isdir(d)]
if missing:
    sys.stderr.write(f"ERROR: required repo directories missing: {', '.join(missing)}\n")
    sys.exit(2)
print("OK: canonical repo layout present.")
