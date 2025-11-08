#!/usr/bin/env python3
"""
Normalize Cross-Reference Fields

Converts legacy 'links' field to canonical 'xrefs' field in AI nouns export.
This is a lightweight post-processing step that ensures downstream consumers
can rely on a single field name.

Usage:
  python3 scripts/ops/normalize_xrefs.py

Input:
  exports/ai_nouns.enriched.json

Output:
  Updates file in-place if normalization needed
"""

from __future__ import annotations

import json
import sys
import pathlib

EXPORT = pathlib.Path("exports/ai_nouns.enriched.json")


def main() -> int:
    if not EXPORT.exists():
        print(f"SKIP: {EXPORT} not found", file=sys.stderr)
        return 0

    data = json.loads(EXPORT.read_text())
    changed = False

    for nd in data.get("nodes", []):
        # If xrefs missing but links present, promote links to xrefs
        if "xrefs" not in nd and "links" in nd and isinstance(nd["links"], list):
            nd["xrefs"] = nd["links"]
            changed = True

    if changed:
        EXPORT.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        print(f"✅ Normalized {EXPORT}: promoted 'links' to 'xrefs'", file=sys.stderr)
    else:
        print(f"✅ {EXPORT}: no normalization needed", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
