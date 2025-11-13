#!/usr/bin/env python3
"""
Guard for control-plane compliance webproof backlinks.

Validates that control_compliance.html contains all required backlinks with data-testid attributes.
Emits a machine-readable verdict JSON to evidence/guard_control_compliance_webproof_backlinks.json.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, UTC
from html.parser import HTMLParser
from pathlib import Path

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

VERDICT_PATH = REPO / "evidence" / "guard_control_compliance_webproof_backlinks.json"

# Expected backlinks: (testid, expected_path_fragment)
EXPECTED_BACKLINKS = [
    ("backlink-compliance-head-json", "compliance.head.json"),
    ("backlink-top-violations-7d-json", "top_violations_7d.json"),
    ("backlink-top-violations-30d-json", "top_violations_30d.json"),
    ("backlink-guard-control-compliance-exports-json", "guard_control_compliance_exports.json"),
]


class BacklinkParser(HTMLParser):
    """Parse HTML to extract backlinks with data-testid attributes."""

    def __init__(self):
        super().__init__()
        self.backlinks: dict[str, str] = {}  # testid -> href

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        if tag == "a":
            testid = None
            href = None
            for attr, value in attrs:
                if attr == "data-testid":
                    testid = value
                elif attr == "href":
                    href = value
            if testid and href:
                self.backlinks[testid] = href


def main() -> int:
    """Run guard and emit verdict."""
    VERDICT_PATH.parent.mkdir(parents=True, exist_ok=True)

    html_file = REPO / "docs" / "atlas" / "webproof" / "control_compliance.html"

    if not html_file.exists():
        verdict_data = {
            "ok": False,
            "page": "control_compliance.html",
            "errors": [f"HTML file missing: {html_file}"],
            "generated_at": datetime.now(UTC).isoformat(),
        }
        VERDICT_PATH.write_text(json.dumps(verdict_data, indent=2) + "\n", encoding="utf-8")
        print("[guard_control_compliance_webproof_backlinks] FAIL: HTML file missing", file=sys.stderr)
        return 1

    try:
        content = html_file.read_text(encoding="utf-8")
    except Exception as e:
        verdict_data = {
            "ok": False,
            "page": "control_compliance.html",
            "errors": [f"Failed to read HTML: {e}"],
            "generated_at": datetime.now(UTC).isoformat(),
        }
        VERDICT_PATH.write_text(json.dumps(verdict_data, indent=2) + "\n", encoding="utf-8")
        print(
            "[guard_control_compliance_webproof_backlinks] FAIL: Failed to read HTML",
            file=sys.stderr,
        )
        return 1

    parser = BacklinkParser()
    parser.feed(content)

    missing = []
    found = []

    for testid, expected_path_fragment in EXPECTED_BACKLINKS:
        if testid not in parser.backlinks:
            missing.append(f"Missing backlink: {testid}")
        else:
            href = parser.backlinks[testid]
            # Check if href contains expected path fragment
            if expected_path_fragment in href:
                found.append(testid)
            else:
                missing.append(
                    f"Backlink {testid} points to wrong path: {href} (expected fragment: {expected_path_fragment})"
                )

    all_ok = len(missing) == 0

    verdict_data = {
        "ok": all_ok,
        "page": "control_compliance.html",
        "errors": missing if missing else [],
        "found": found,
        "generated_at": datetime.now(UTC).isoformat(),
    }

    VERDICT_PATH.write_text(json.dumps(verdict_data, indent=2) + "\n", encoding="utf-8")

    if all_ok:
        print(f"[guard_control_compliance_webproof_backlinks] OK: All {len(found)} backlinks found")
        return 0
    else:
        print(
            f"[guard_control_compliance_webproof_backlinks] FAIL: {len(missing)} backlink(s) missing",
            file=sys.stderr,
        )
        print(json.dumps(verdict_data, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
