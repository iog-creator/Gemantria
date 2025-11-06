#!/usr/bin/env python3
"""
Guard: Cross-References Extracted

Validates that nouns mentioning verses in their enrichment insights
have corresponding cross-references extracted and attached.
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from src.utils.osis import extract_verse_references
except ImportError:
    # Fallback for direct execution
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from src.utils.osis import extract_verse_references


def main():
    """Validate cross-reference extraction from enriched nouns."""
    if len(sys.argv) < 2:
        print("Usage: guard_crossrefs_extracted.py <enriched_nouns.json>", file=sys.stderr)
        sys.exit(1)

    nouns_file = sys.argv[1]

    try:
        with open(nouns_file, encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"ERROR: Cannot read {nouns_file}: {e}", file=sys.stderr)
        sys.exit(1)

    nouns = data.get("nodes", [])
    if not nouns:
        print("SKIP: No nouns in file", file=sys.stderr)
        sys.exit(0)

    nouns_with_insights = 0
    nouns_with_verse_mentions = 0
    nouns_with_crossrefs = 0
    nouns_with_missing_crossrefs = 0

    for noun in nouns:
        insights = noun.get("insights", "")
        if not insights:
            continue

        nouns_with_insights += 1

        # Check if insights mention verses
        verse_refs = extract_verse_references(insights)
        if not verse_refs:
            continue

        nouns_with_verse_mentions += 1

        # Check if noun has crossrefs attached
        enrichment = noun.get("enrichment", {})
        crossrefs = enrichment.get("crossrefs", [])

        if crossrefs:
            nouns_with_crossrefs += 1
        else:
            nouns_with_missing_crossrefs += 1
            print(
                f"WARN: Noun '{noun.get('surface', 'unknown')}' mentions {len(verse_refs)} verses but has no crossrefs",
                file=sys.stderr,
            )

    # Summary
    if nouns_with_verse_mentions == 0:
        print("SKIP: No nouns mention verses in insights", file=sys.stderr)
        sys.exit(0)

    extraction_rate = nouns_with_crossrefs / nouns_with_verse_mentions

    if extraction_rate < 0.8:  # Require 80% extraction rate
        print(f".2f{nouns_with_missing_crossrefs} nouns missing crossrefs", file=sys.stderr)
        sys.exit(1)

    print(
        f"OK: crossrefs extracted for {nouns_with_crossrefs}/{nouns_with_verse_mentions} verse-mentioning nouns ({extraction_rate:.1%})"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
