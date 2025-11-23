#!/usr/bin/env python3
"""Export BibleScholar semantic search results to static JSON.

Generates: share/exports/biblescholar/semantic_search.json
"""

import argparse
import json
import sys
from datetime import datetime, UTC
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentpm.biblescholar.semantic_search_flow import semantic_search

# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`


def export_semantic_search(query: str, limit: int, translation: str, output_path: Path) -> int:
    """Export semantic search results to JSON.

    Args:
        query: Search query.
        limit: Max results.
        translation: Bible translation.
        output_path: Output JSON file path.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        # Run semantic search
        result = semantic_search(query=query, limit=limit, translation=translation)

        # Serialize to JSON
        export_data = {
            "query": result.query,
            "translation": translation,
            "limit": limit,
            "model": result.model,
            "results_count": result.total_results,
            "results": [
                {
                    "verse_id": v.verse_id,
                    "book_name": v.book_name,
                    "chapter_num": v.chapter_num,
                    "verse_num": v.verse_num,
                    "text": v.text,
                    "translation_source": v.translation_source,
                    "similarity_score": v.similarity_score,
                }
                for v in result.results
            ],
            "generated_at": datetime.now(UTC).isoformat(),
        }

        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"✓ {output_path} ({result.total_results} results)")
        return 0

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        # Write minimal export with error
        error_data = {
            "query": query,
            "translation": translation,
            "limit": limit,
            "results_count": 0,
            "results": [],
            "error": str(e),
            "generated_at": datetime.now(UTC).isoformat(),
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(error_data, f, indent=2)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BibleScholar semantic search results")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--limit", type=int, default=20, help="Max results (default: 20)")
    parser.add_argument("--translation", default="KJV", help="Bible translation (default: KJV)")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("share/exports/biblescholar/semantic_search.json"),
        help="Output path",
    )

    args = parser.parse_args()
    return export_semantic_search(args.query, args.limit, args.translation, args.output)


if __name__ == "__main__":
    sys.exit(main())
