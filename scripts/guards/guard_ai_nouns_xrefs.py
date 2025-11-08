#!/usr/bin/env python3
"""
Guard: AI Nouns Cross-Reference Preservation

Validates that enriched AI nouns preserve cross-references from model output.
Computes ratio of nodes with xrefs (or legacy 'links' alias).

Mode: HINT by default (non-blocking)
      STRICT when STRICT_XREFS=1 (blocks on low ratio)

Environment Variables:
  MIN_XREF_RATIO: Minimum ratio of nodes with xrefs (default: 0.25)
  STRICT_XREFS: Enable STRICT mode (1) or HINT mode (0, default)

Exit Codes:
  0: Guard passed or skipped (HINT mode always returns 0)
  2: Guard failed in STRICT mode
"""

from __future__ import annotations

import json
import os
import sys
import pathlib
import datetime as dt
from typing import Any, Dict

EXPORT = pathlib.Path("exports/ai_nouns.enriched.json")
MIN_RATIO = float(os.getenv("MIN_XREF_RATIO", "0.25"))
STRICT = os.getenv("STRICT_XREFS", "0") == "1"


def main() -> int:
    out: Dict[str, Any] = {
        "ok": False,
        "mode": "STRICT" if STRICT else "HINT",
        "file": str(EXPORT),
        "min_ratio": MIN_RATIO,
    }

    if not EXPORT.exists():
        out.update(note="export missing; skipping", ok=True)
        print(json.dumps(out, ensure_ascii=False))
        return 0

    data = json.loads(EXPORT.read_text())
    nodes = data.get("nodes", [])
    n = len(nodes)
    with_refs = 0

    for nd in nodes:
        xrefs = nd.get("xrefs")
        if xrefs is None:
            xrefs = nd.get("links", [])
        if isinstance(xrefs, list) and len(xrefs) > 0:
            with_refs += 1

    ratio = 0.0 if n == 0 else with_refs / n
    out.update(
        total=n,
        with_xrefs=with_refs,
        ratio=round(ratio, 4),
        ts=dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z"),
    )

    ok = (ratio >= MIN_RATIO) or (n == 0)
    out["ok"] = ok

    if STRICT:
        rc = 0 if ok else 2
    else:
        rc = 0  # HINT mode always returns 0

    print(json.dumps(out, ensure_ascii=False))
    return rc


if __name__ == "__main__":
    sys.exit(main())
