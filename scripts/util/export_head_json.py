#!/usr/bin/env python3
"""
Head Extraction Utility for PM Share Package

Reads a file and extracts the first N lines as JSON.
Used for exporting head of AGENTS.md, PM_CONTRACT.md, NEXT_STEPS.md.

Usage:
    python scripts/util/export_head_json.py <file_path> [--lines N] [--output <path>]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

DEFAULT_LINES = 100


def now_iso() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now(UTC).isoformat()


def export_head(file_path: Path, lines: int = DEFAULT_LINES) -> dict[str, Any]:
    """Extract first N lines from file and return as JSON structure."""
    if not file_path.exists():
        return {
            "schema": "file_head.v1",
            "generated_at": now_iso(),
            "file_path": str(file_path),
            "exists": False,
            "line_count": 0,
            "head_lines": [],
            "error": "File not found",
        }

    try:
        with file_path.open(encoding="utf-8") as f:
            all_lines = f.readlines()
            head_lines = all_lines[:lines]

        return {
            "schema": "file_head.v1",
            "generated_at": now_iso(),
            "file_path": str(file_path),
            "exists": True,
            "line_count": len(all_lines),
            "head_lines": [line.rstrip("\n") for line in head_lines],
            "head_line_count": len(head_lines),
            "error": None,
        }
    except Exception as exc:
        return {
            "schema": "file_head.v1",
            "generated_at": now_iso(),
            "file_path": str(file_path),
            "exists": True,
            "line_count": 0,
            "head_lines": [],
            "error": f"Read error: {exc!s}",
        }


def main() -> int:
    """Main entrypoint."""
    parser = argparse.ArgumentParser(description="Export head of file as JSON")
    parser.add_argument("file_path", type=Path, help="Path to file to extract head from")
    parser.add_argument(
        "--lines",
        type=int,
        default=DEFAULT_LINES,
        help=f"Number of lines to extract (default: {DEFAULT_LINES})",
    )
    parser.add_argument("--output", type=Path, help="Output JSON file path (default: stdout)")

    args = parser.parse_args()

    # Resolve file path relative to repo root if not absolute
    if not args.file_path.is_absolute():
        file_path = REPO / args.file_path
    else:
        file_path = args.file_path

    export_data = export_head(file_path, args.lines)

    if args.output:
        # Resolve output path relative to repo root if not absolute
        if not args.output.is_absolute():
            output_path = REPO / args.output
        else:
            output_path = args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(export_data, indent=2, default=str),
            encoding="utf-8",
        )
        print(f"✅ Exported head of {file_path} to {output_path}")
    else:
        print(json.dumps(export_data, indent=2, default=str))

    return 0 if export_data.get("error") is None else 1


if __name__ == "__main__":
    sys.exit(main())
