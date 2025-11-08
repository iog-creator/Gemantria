#!/usr/bin/env python3
"""Guard for cross-reference extraction ratio.

Validates that enriched nouns contain cross-references in the xrefs[] field.
Operates in HINT mode by default (non-blocking) or STRICT mode (fail-closed).

Environment variables:
- MIN_XREF_RATIO: Minimum ratio threshold (default: 0.25)
- STRICT_XREFS: Set to '1' for fail-closed behavior

Exit codes:
- 0: HINT mode or STRICT mode passed
- 1: STRICT mode failed (ratio below threshold)
- 2: File missing or malformed
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def main() -> int:
    """Check cross-reference extraction ratio."""
    # Configuration
    src = Path("exports/ai_nouns.enriched.json")
    min_ratio = float(os.getenv("MIN_XREF_RATIO", "0.25"))
    strict = os.getenv("STRICT_XREFS") == "1"

    # Check file exists
    if not src.exists():
        result = {
            "ok": False,
            "mode": "STRICT" if strict else "HINT",
            "note": "exports/ai_nouns.enriched.json not found",
        }
        print(json.dumps(result))
        return 2 if strict else 0

    # Load and analyze
    try:
        data = json.loads(src.read_text())
    except json.JSONDecodeError as e:
        result = {
            "ok": False,
            "mode": "STRICT" if strict else "HINT",
            "note": f"JSON parse error: {e}",
        }
        print(json.dumps(result))
        return 2 if strict else 0

    nodes = data.get("nodes", [])
    total = len(nodes)
    with_xrefs = sum(1 for nd in nodes if nd.get("xrefs") and len(nd["xrefs"]) > 0)

    ratio = with_xrefs / total if total > 0 else 0.0

    # Determine pass/fail
    passed = ratio >= min_ratio
    result = {
        "ok": passed,
        "mode": "STRICT" if strict else "HINT",
        "min_ratio": min_ratio,
        "total": total,
        "with_xrefs": with_xrefs,
        "ratio": round(ratio, 3),
        "note": (
            f"Cross-reference ratio: {with_xrefs}/{total} = {ratio:.3f} "
            f"({'✅ PASS' if passed else f'❌ FAIL (< {min_ratio})'})"
        ),
    }
    print(json.dumps(result))

    if strict and not passed:
        print(
            f"GUARD FAILED: xref ratio {ratio:.3f} < {min_ratio} (STRICT mode)",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
