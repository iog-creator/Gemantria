#!/usr/bin/env python3
"""
E91 — Guard: Atlas Guard Receipts Index

Checks that:
- docs/atlas/browser/guard_receipts.html exists
- evidence/guard_*.json are discoverable
- each discovered receipt file is mentioned in the HTML

Outputs JSON verdict: {ok: bool, checks: {...}, counts: {...}}
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add project root to path
REPO = Path(__file__).resolve().parents[2]

EVIDENCE_DIR = REPO / "evidence"
HTML_PATH = REPO / "docs" / "atlas" / "browser" / "guard_receipts.html"
VERDICT_PATH = REPO / "evidence" / "guard_atlas_guard_receipts.json"


def main() -> int:
    """Run guard checks."""
    checks = {}
    counts = {}

    exists_html = HTML_PATH.exists()
    checks["html_exists"] = exists_html
    if not exists_html:
        verdict = {"ok": False, "checks": checks, "counts": counts}
        VERDICT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with VERDICT_PATH.open("w") as f:
            json.dump(verdict, f, indent=2)
        print(json.dumps(verdict, indent=2))
        return 1

    html_text = HTML_PATH.read_text(encoding="utf-8")

    guard_files = sorted(EVIDENCE_DIR.glob("guard_*.json")) if EVIDENCE_DIR.exists() else []
    counts["guard_files"] = len(guard_files)

    missing_refs = []
    for path in guard_files:
        basename = path.name if isinstance(path, Path) else str(path)
        if basename not in html_text:
            missing_refs.append(basename)

    checks["all_receipts_linked"] = len(missing_refs) == 0
    counts["missing_refs"] = len(missing_refs)

    # Check for required backlinks
    required_backlinks = [
        "backlink-compliance-summary",
        "backlink-compliance-timeseries",
        "backlink-violations-browser",
        "backlink-evidence-dir",
    ]
    missing_backlinks = []
    for backlink in required_backlinks:
        if f'data-testid="{backlink}"' not in html_text:
            missing_backlinks.append(backlink)

    checks["required_backlinks"] = len(missing_backlinks) == 0
    counts["missing_backlinks"] = len(missing_backlinks)

    # Check for E91 badge
    checks["e91_badge"] = 'class="badge">E91' in html_text or 'badge">E91' in html_text

    ok = all(checks.values()) if checks else True
    verdict = {
        "ok": ok,
        "checks": checks,
        "counts": counts,
        "missing_refs": missing_refs,
        "missing_backlinks": missing_backlinks,
    }

    VERDICT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with VERDICT_PATH.open("w") as f:
        json.dump(verdict, f, indent=2)

    print(json.dumps(verdict, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
