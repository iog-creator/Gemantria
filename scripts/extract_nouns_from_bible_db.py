# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""Extract nouns from bible_db (read-only) and output in SSOT format."""

import argparse
import json
import os
import re
import sys
from datetime import datetime, UTC

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env
from src.infra.env_loader import ensure_env_loaded

ensure_env_loaded()

from src.nodes.collect_nouns_db import collect_nouns_for_book
from src.core.books import normalize_book


def main():
    ap = argparse.ArgumentParser(description="Extract nouns from bible_db (read-only)")
    ap.add_argument("--book", required=True, help="Book name (e.g., Genesis)")
    ap.add_argument(
        "--min-confidence", type=float, default=0.0, help="Minimum confidence (for filtering after enrichment)"
    )
    ap.add_argument("--output", required=True, help="Output JSON file path")
    args = ap.parse_args()

    # Extract nouns from bible_db
    book = normalize_book(args.book)
    print(f"Extracting nouns from bible_db for book: {book}")

    try:
        nouns = collect_nouns_for_book(book)
        print(f"Found {len(nouns)} nouns from bible_db")
    except Exception as e:
        print(f"ERROR: Failed to collect nouns: {e}", file=sys.stderr)
        sys.exit(1)

    # Convert to SSOT format
    ssot_nouns = []
    for noun in nouns:
        hebrew = noun.get("hebrew", "")
        # Skip invalid Hebrew (Unknown, empty, Strong's numbers)
        if not hebrew or not hebrew.strip():
            continue
        if hebrew.strip().lower() in ("unknown", "null", "none"):
            continue
        if re.match(r"^H\d+$", hebrew.strip(), re.I):
            continue

        ssot_noun = {
            "surface": hebrew,
            "hebrew": hebrew,  # Set hebrew field for enrichment filter
            "name": hebrew,  # Set name field as fallback
            "primary_verse": noun.get("primary_verse", ""),  # Set primary_verse for enrichment prompt
            "ai_discovered": False,  # Mark as DB-seeded, not AI-discovered (prevents "Unknown" in AI analysis section)
            "letters": [],  # Empty list (not None) to avoid "Unknown" in prompt
            "gematria": None,  # Will be calculated downstream
            "gematria_value": None,  # calculated downstream
            "class": "other",  # will be enriched downstream
            "classification": None,  # Will be enriched downstream
            "meaning": None,  # Will be enriched downstream
            "analysis": {
                "lemma": noun.get("name", hebrew),
                "primary_verse": noun.get("primary_verse"),
                "freq": noun.get("freq", 0),
            },
            "sources": [{"name": "bible_db.v_hebrew_tokens", "ref": noun.get("primary_verse", "")}],
        }
        ssot_nouns.append(ssot_noun)

    # Create envelope
    envelope = {
        "schema": "gemantria/ai-nouns.v1",
        "source": "bible_db.v_hebrew_tokens",
        "book": book,
        "generated_at": datetime.now(UTC).isoformat(),
        "nodes": ssot_nouns,
    }

    # Write output
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(envelope, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(ssot_nouns)} nouns → {args.output}")
    print(f"Filtered out {len(nouns) - len(ssot_nouns)} invalid nouns")


if __name__ == "__main__":
    main()
