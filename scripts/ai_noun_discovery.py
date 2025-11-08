#!/usr/bin/env python3
"""
AI Noun Discovery Script

Wrapper script for the AI-driven noun discovery agent.
Reads from .env, calls the discovery function, and outputs to exports/ai_nouns.json
"""

import os
import sys
import json
import datetime
from pathlib import Path

# Add src to path - handle both direct execution and PYTHONPATH
script_dir = Path(__file__).parent
project_root = script_dir.parent
src_dir = project_root / "src"

# Always add src to path
sys.path.insert(0, str(src_dir))

from src.nodes.ai_noun_discovery import discover_nouns_for_book  # noqa: E402
from src.infra.env_loader import ensure_env_loaded  # noqa: E402


def main():
    """Run AI noun discovery for a book."""
    ensure_env_loaded()

    book = os.environ.get("BOOK", "Genesis")
    output_file = os.environ.get("OUTPUT", "exports/ai_nouns.json")

    print(f">> AI Noun Discovery for {book}", file=sys.stderr)

    # Run discovery
    nouns = discover_nouns_for_book(book)

    # Convert to SSOT format
    data = {
        "schema": "gematria/ai-nouns.v1",
        "book": book,
        "generated_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "nodes": [],
    }

    for noun in nouns:
        # Map from discovery function fields to ai-nouns.v1 schema
        node = {
            "noun_id": str(noun.get("noun_id", f"ai-{book.lower()}-{hash(noun.get('surface', ''))}")),
            "surface": noun.get("surface", ""),
            "lemma": noun.get("lemma", None),
            "letters": noun.get("letters", []),
            "gematria": noun.get("gematria", 0),
            "class": noun.get("class", "thing"),
            "ai_discovered": noun.get("ai_discovered", True),
            "analysis": noun.get("analysis", f"Hebrew noun: {noun.get('surface', '')}"),
            "sources": noun.get("sources", [{"ref": f"{book} unknown", "offset": None}]),
        }
        data["nodes"].append(node)

    # Ensure output directory exists
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    # Write JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"AI_NOUNS_WRITTEN {len(data['nodes'])} nouns to {output_file}")


if __name__ == "__main__":
    main()
