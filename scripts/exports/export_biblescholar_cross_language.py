#!/usr/bin/env python3
"""Export BibleScholar cross-language connections to static JSON.

Generates: share/exports/biblescholar/cross_language.json
"""

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pmagent.biblescholar.cross_language_semantic_flow import find_cross_language_connections


def export_cross_language(strongs_id: str, limit: int, output_path: Path) -> None:
    """Export cross-language connections to JSON."""
    try:
        result = find_cross_language_connections(strongs_id=strongs_id, limit=limit)

        if not result:
            # Write empty result
            export_data = {
                "strongs_id": strongs_id,
                "lemma": "",
                "hebrew_verses": [],
                "connections": [],
                "total_connections": 0,
                "generated_at": datetime.now(UTC).isoformat(),
                "error": f"No verses found for {strongs_id}",
            }
        else:
            # Serialize to JSON
            export_data = {
                "strongs_id": result.strongs_id,
                "lemma": result.lemma,
                "hebrew_verses": result.hebrew_verses,
                "connections": [
                    {
                        "hebrew_verse": c.hebrew_verse,
                        "greek_verse": {
                            "verse_id": c.greek_verse.verse_id,
                            "book_name": c.greek_verse.book_name,
                            "chapter_num": c.greek_verse.chapter_num,
                            "verse_num": c.greek_verse.verse_num,
                            "text": c.greek_verse.text,
                            "translation_source": c.greek_verse.translation_source,
                        },
                        "similarity_score": c.similarity_score,
                    }
                    for c in result.connections
                ],
                "total_connections": result.total_connections,
                "generated_at": datetime.now(UTC).isoformat(),
            }

        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"✓ {output_path} ({result.total_connections if result else 0} connections)")

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        # Write minimal export with error
        error_data = {
            "strongs_id": strongs_id,
            "lemma": "",
            "hebrew_verses": [],
            "connections": [],
            "total_connections": 0,
            "error": str(e),
            "generated_at": datetime.now(UTC).isoformat(),
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(error_data, f, indent=2)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Export BibleScholar cross-language connections")
    parser.add_argument("--strongs", required=True, help="Strong's number (e.g., H7965)")
    parser.add_argument("--limit", type=int, default=10, help="Max connections (default: 10)")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("share/exports/biblescholar/cross_language.json"),
        help="Output path",
    )

    args = parser.parse_args()
    export_cross_language(args.strongs, args.limit, args.output)


if __name__ == "__main__":
    main()
