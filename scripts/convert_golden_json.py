# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
Convert old golden JSON format to new JSONL format.
Usage: python3 scripts/convert_golden_json.py <input.json> <output.jsonl>
"""

import json
import sys
from pathlib import Path
from typing import Any


def convert_record(record: dict[str, Any], book: str = "Genesis") -> dict[str, Any]:
    """Convert a single noun record from old format to new JSONL format."""
    # Map old fields to new structure
    new_record = {
        "noun": record.get("strong_number", ""),
        "name": record.get("name", ""),
        "hebrew": record.get("hebrew", ""),
        "hebrew_with_nikud": record.get("hebrew_with_nikud", ""),
        "value": record.get("value", 0),
        "calculation": record.get("calculation", ""),
        "primary_verse": record.get("primary_verse", ""),
        "verse_refs": record.get("verse_refs", []),
        "meaning": record.get("meaning", ""),
        "semantic_tags": record.get("semantic_tags", []),
        "insights": record.get("insights", ""),
        "theological_significance": record.get("theological_significance", ""),
        # Add enrichment metadata (simulated)
        "confidence": 0.98,  # High confidence for golden examples
        "tokens": 250,  # Approximate token count
        "source": "lm",
        "book": book,
        "chapter": extract_chapter(record.get("primary_verse", "")),
        "timestamp": "2025-10-25T02:55:50.000Z",
    }
    return new_record


def extract_chapter(verse_ref: str) -> int:
    """Extract chapter number from verse reference like 'Genesis 2:7'."""
    if ":" in verse_ref:
        parts = verse_ref.split(":")
        if len(parts) >= 1:
            chapter_part = parts[0].split()[-1]  # Get last part after space
            try:
                return int(chapter_part)
            except ValueError:
                pass
    return 1  # Default to chapter 1


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 scripts/convert_golden_json.py <input.json> <output.jsonl>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        sys.exit(1)

    try:
        with input_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        book_name = data.get("book_name", "Genesis")
        nouns = data.get("nouns", [])

        print(f"[convert] Converting {len(nouns)} nouns from {book_name}")

        with output_path.open("w", encoding="utf-8") as f:
            for noun in nouns:
                converted = convert_record(noun, book_name)
                f.write(json.dumps(converted, ensure_ascii=False) + "\n")

        print(f"[convert] Successfully converted to {output_path}")

    except Exception as e:
        print(f"ERROR: Failed to convert: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
