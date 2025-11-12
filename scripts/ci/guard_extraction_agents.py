#!/usr/bin/env python3
import json, os, sys

paths = ["agentpm/tests/extractors/test_extraction_correctness.py", "agentpm/tests/extractors/fixtures"]

ok = all(os.path.exists(p) for p in paths)

print(json.dumps({"ok": ok, "paths": paths}))
sys.exit(0 if ok else 1)
