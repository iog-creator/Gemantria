#!/usr/bin/env python3
"""
Discovery script for hardcoded hints in the codebase.

Scans codebase for hardcoded hints and classifies them as REQUIRED vs SUGGESTED.
Outputs a catalog (JSON) for registry seeding.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def scan_file_for_hints(file_path: Path) -> list[dict[str, Any]]:
    """Scan a file for hardcoded hints."""
    hints = []

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return hints

    # Pattern 1: LOUD HINT comments
    # Example: "# LOUD HINT: docs.dms_only - DMS-only, no fallback"
    loud_hint_pattern = re.compile(
        r"#\s*LOUD\s+HINT:\s*([^\n]+)",
        re.IGNORECASE,
    )

    for match in loud_hint_pattern.finditer(content):
        hint_text = match.group(1).strip()
        hints.append(
            {
                "source_file": str(file_path.relative_to(ROOT)),
                "line": content[: match.start()].count("\n") + 1,
                "text": hint_text,
                "pattern": "LOUD_HINT",
                "suggested_kind": "REQUIRED",  # LOUD hints are typically required
            },
        )

    # Pattern 2: HINT[...] markers
    # Example: "HINT[docs.dms_only]: DMS-only, no fallback"
    hint_marker_pattern = re.compile(
        r"HINT\[([^\]]+)\]:\s*([^\n]+)",
        re.IGNORECASE,
    )

    for match in hint_marker_pattern.finditer(content):
        logical_name = match.group(1).strip()
        hint_text = match.group(2).strip()
        hints.append(
            {
                "source_file": str(file_path.relative_to(ROOT)),
                "line": content[: match.start()].count("\n") + 1,
                "logical_name": logical_name,
                "text": hint_text,
                "pattern": "HINT_MARKER",
                "suggested_kind": "SUGGESTED",  # HINT markers are typically suggested
            },
        )

    # Pattern 3: Handoff structure hints (in prepare_handoff.py)
    if "prepare_handoff" in str(file_path):
        # Look for structured hint sections
        if "DMS-only" in content or "no fallback" in content.lower():
            hints.append(
                {
                    "source_file": str(file_path.relative_to(ROOT)),
                    "line": 0,
                    "text": "DMS-only, no fallback",
                    "pattern": "HANDOFF_STRUCTURE",
                    "suggested_kind": "REQUIRED",
                    "suggested_scope": "handoff",
                    "suggested_flow": "handoff.generate",
                },
            )

    return hints


def discover_hints() -> dict[str, Any]:
    """Discover all hardcoded hints in the codebase."""
    hints = []

    # Scan key directories
    scan_paths = [
        ROOT / "src",
        ROOT / "scripts",
        ROOT / "pmagent",
    ]

    for scan_path in scan_paths:
        if not scan_path.exists():
            continue

        for py_file in scan_path.rglob("*.py"):
            file_hints = scan_file_for_hints(py_file)
            hints.extend(file_hints)

    # Also scan docs/hints_registry.md if it exists
    hints_registry = ROOT / "docs" / "hints_registry.md"
    if hints_registry.exists():
        # Parse markdown catalog (simple pattern matching)
        content = hints_registry.read_text(encoding="utf-8")
        # Look for hint entries in markdown
        for line_num, line in enumerate(content.split("\n"), 1):
            if "|" in line and ("REQUIRED" in line.upper() or "SUGGESTED" in line.upper()):
                hints.append(
                    {
                        "source_file": str(hints_registry.relative_to(ROOT)),
                        "line": line_num,
                        "text": line.strip(),
                        "pattern": "HINTS_REGISTRY_MD",
                        "suggested_kind": "SUGGESTED",
                    },
                )

    return {
        "total_hints": len(hints),
        "hints": hints,
        "summary": {
            "by_pattern": {},
            "by_kind": {"REQUIRED": 0, "SUGGESTED": 0, "UNKNOWN": 0},
        },
    }


def main() -> int:
    """Main entrypoint."""
    import argparse

    parser = argparse.ArgumentParser(description="Discover hardcoded hints in the codebase")
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path for catalog JSON (default: evidence/hints_discovery_catalog.json)",
    )
    parser.add_argument(
        "--mode",
        choices=["report"],
        default="report",
        help="Output mode (default: report)",
    )

    args = parser.parse_args()

    catalog = discover_hints()

    # Generate summary
    for hint in catalog["hints"]:
        pattern = hint.get("pattern", "UNKNOWN")
        catalog["summary"]["by_pattern"][pattern] = catalog["summary"]["by_pattern"].get(pattern, 0) + 1

        kind = hint.get("suggested_kind", "UNKNOWN")
        if kind in catalog["summary"]["by_kind"]:
            catalog["summary"]["by_kind"][kind] += 1
        else:
            catalog["summary"]["by_kind"]["UNKNOWN"] += 1

    # Output JSON catalog
    if args.output:
        output_path = Path(args.output)
        # If relative path, make it relative to ROOT
        if not output_path.is_absolute():
            output_path = ROOT / output_path
    else:
        output_path = ROOT / "evidence" / "hints_discovery_catalog.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(catalog, indent=2), encoding="utf-8")

    print(f"Discovered {catalog['total_hints']} hints")
    print(f"Catalog written to: {output_path}")
    print(f"Summary: {json.dumps(catalog['summary'], indent=2)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
