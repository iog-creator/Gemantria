#!/usr/bin/env python3

"""
Guard: ensure docs/SSOT/GPT_SYSTEM_PROMPT.md contains the required literal markers.

Exits non-zero if checks fail.
"""

import sys

from pathlib import Path


prompt = Path("docs/SSOT/GPT_SYSTEM_PROMPT.md")
if not prompt.exists():
    print("MISSING: docs/SSOT/GPT_SYSTEM_PROMPT.md")
    sys.exit(2)
txt = prompt.read_text()


required = ["=== OPS OUTPUT (for Cursor to execute) ===", "=== TUTOR NOTES ===", "Rule-062"]


missing = [r for r in required if r not in txt]
if missing:
    print("GUARD_FAIL: missing required tokens in GPT_SYSTEM_PROMPT.md ->", missing)
    sys.exit(3)


print("OK: prompt format guard passed")
sys.exit(0)
