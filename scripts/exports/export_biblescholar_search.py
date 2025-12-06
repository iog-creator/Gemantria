#!/usr/bin/env python3
"""Export BibleScholar search results to share/exports/biblescholar/search.json.

This script wraps pmagent.biblescholar.search_flow to generate static JSON exports
for the Orchestrator Shell UI.
"""

import argparse
import json
import pathlib
import sys
from dataclasses import asdict
from datetime import datetime, UTC

from pmagent.biblescholar.search_flow import get_db_status, search_verses

# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BibleScholar search results to Atlas")
    parser.add_argument(
        "--query",
        type=str,
        required=True,
        help="Search query (minimum 2 characters)",
    )
    parser.add_argument(
        "--translation",
        type=str,
        default="KJV",
        help="Translation identifier (default: KJV)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of results (default: 20)",
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

    # Get DB status
    db_status = get_db_status()
    if db_status == "db_off":
        print(
            "ERROR: Database is unavailable. Please ensure BIBLE_DB_DSN is set and the database is running.",
            file=sys.stderr,
        )
        return 1

    # Perform search
    try:
        results = search_verses(args.query, args.translation, args.limit)
    except Exception as e:
        print(f"ERROR: Search failed: {e}", file=sys.stderr)
        return 1

    # Build export structure
    export_data = {
        "query": args.query,
        "translation": args.translation,
        "limit": args.limit,
        "db_status": db_status,
        "results_count": len(results),
        "results": [asdict(verse) for verse in results],
        "generated_at": datetime.now(UTC).isoformat(),
    }

    # Write to file
    output_file = args.output_dir / "search.json"
    try:
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        print(f"✓ {output_file} ({len(results)} results)")
        return 0
    except Exception as e:
        print(f"ERROR: Failed to write {output_file}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
