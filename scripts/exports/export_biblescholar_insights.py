#!/usr/bin/env python3
"""Export BibleScholar insights to share/exports/biblescholar/insights.json.

This script wraps agentpm.biblescholar.insights_flow to generate static JSON exports
for the Orchestrator Shell UI.
"""

import argparse
import json
import pathlib
import sys
from dataclasses import asdict
from datetime import datetime, UTC

from agentpm.biblescholar.insights_flow import get_verse_context

# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BibleScholar insights to Atlas")
    parser.add_argument(
        "--ref",
        type=str,
        required=True,
        help="Bible reference (e.g., Genesis 1:1, Matthew 5:3)",
    )
    parser.add_argument(
        "--translations",
        type=str,
        nargs="*",
        default=[],
        help="Additional translations to include (default: KJV only)",
    )
    parser.add_argument(
        "--include-lexicon",
        action="store_true",
        default=True,
        help="Include lexicon entries (default: True)",
    )
    parser.add_argument(
        "--no-lexicon",
        dest="include_lexicon",
        action="store_false",
        help="Exclude lexicon entries",
    )
    parser.add_argument(
        "--include-similar",
        action="store_true",
        default=True,
        help="Include similar verses (default: True)",
    )
    parser.add_argument(
        "--no-similar",
        dest="include_similar",
        action="store_false",
        help="Exclude similar verses",
    )
    parser.add_argument(
        "--similarity-limit",
        type=int,
        default=5,
        help="Number of similar verses to fetch (default: 5)",
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

    # Get verse context
    translations = ["KJV"] + args.translations if args.translations else None
    try:
        context = get_verse_context(
            args.ref,
            translations=translations,
            include_lexicon=args.include_lexicon,
            include_similar=args.include_similar,
            similarity_limit=args.similarity_limit,
        )
    except Exception as e:
        print(f"WARNING: Failed to get verse context: {e}. Exporting with null context.", file=sys.stderr)
        context = None

    # Build export structure
    export_data = {
        "reference": args.ref,
        "found": context is not None,
        "context": None,
        "generated_at": datetime.now(UTC).isoformat(),
    }

    if context:
        # Serialize context (dataclass to dict)
        context_dict = {
            "reference": context.reference,
            "primary_text": context.primary_text,
            "secondary_texts": context.secondary_texts,
            "lexicon_entries": [asdict(entry) for entry in context.lexicon_entries],
            "similar_verses": [asdict(v) for v in context.similar_verses],
            "metadata": context.metadata,
        }
        export_data["context"] = context_dict

    # Write to file
    output_file = args.output_dir / "insights.json"
    try:
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        if context:
            print(f"✓ {output_file} (found: {context.reference})")
        else:
            print(f"✓ {output_file} (not found)")
        return 0
    except Exception as e:
        print(f"ERROR: Failed to write {output_file}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
