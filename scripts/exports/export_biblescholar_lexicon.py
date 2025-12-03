#!/usr/bin/env python3
"""Export BibleScholar lexicon entry to share/exports/biblescholar/lexicon.json.

This script wraps pmagent.biblescholar.lexicon_flow to generate static JSON exports
for the Orchestrator Shell UI.
"""

import argparse
import json
import pathlib
import sys
from dataclasses import asdict
from datetime import datetime, UTC

from pmagent.biblescholar.lexicon_adapter import LexiconAdapter

# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BibleScholar lexicon entry to Atlas")
    parser.add_argument(
        "--strongs",
        type=str,
        required=True,
        help="Strong's number (e.g., H1, G1)",
    )
    parser.add_argument(
        "--output-dir",
        type=pathlib.Path,
        default=pathlib.Path("share/exports/biblescholar"),
        help="Output directory for BibleScholar JSONs",
    )

    args = parser.parse_args()

    # Ensure output directory exists
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Fetch lexicon entry (this will actually connect and update status)
    # We need to create an adapter to get the actual status after connection

    adapter = LexiconAdapter()
    try:
        # Determine language from Strong's prefix
        if args.strongs.upper().startswith("H"):
            entry = adapter.get_hebrew_entry(args.strongs)
        elif args.strongs.upper().startswith("G"):
            entry = adapter.get_greek_entry(args.strongs)
        else:
            # Try Hebrew first, then Greek
            entry = adapter.get_hebrew_entry(args.strongs)
            if not entry:
                entry = adapter.get_greek_entry(args.strongs)
        # Get actual DB status after attempting fetch
        db_status = adapter.db_status
    except Exception as e:
        print(
            f"WARNING: Failed to fetch lexicon entry: {e}. Exporting with null entry.",
            file=sys.stderr,
        )
        entry = None
        db_status = adapter.db_status

    # Build export structure
    export_data = {
        "strongs_id": args.strongs,
        "db_status": db_status,
        "found": entry is not None,
        "entry": asdict(entry) if entry else None,
        "generated_at": datetime.now(UTC).isoformat(),
    }

    # Write to file
    output_file = args.output_dir / "lexicon.json"
    try:
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        if entry:
            print(f"✓ {output_file} (found: {entry.lemma})")
        else:
            print(f"✓ {output_file} (not found)")
        return 0
    except Exception as e:
        print(f"ERROR: Failed to write {output_file}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
