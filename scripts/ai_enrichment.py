#!/usr/bin/env python3
"""
AI Enrichment Script

Wrapper script for the enrichment agent.
Reads exports/ai_nouns.json, enriches nouns, writes to exports/ai_nouns.enriched.json
"""

import os
import sys
import json
from pathlib import Path

# Add src to path - handle both direct execution and PYTHONPATH
script_dir = Path(__file__).parent
project_root = script_dir.parent
src_dir = project_root / "src"

# Always add src to path
sys.path.insert(0, str(src_dir))

from src.nodes.enrichment import enrichment_node
from src.infra.env_loader import ensure_env_loaded


def main():
    """Run AI enrichment on discovered nouns."""
    ensure_env_loaded()

    input_file = os.environ.get("INPUT", "exports/ai_nouns.json")
    output_file = os.environ.get("OUTPUT", "exports/ai_nouns.enriched.json")
    book = os.environ.get("BOOK", "Genesis")

    print(f">> AI Enrichment for {book}", file=sys.stderr)

    # Read input nouns
    if not Path(input_file).exists():
        print(f"ERROR: Input file {input_file} not found", file=sys.stderr)
        sys.exit(1)

    with open(input_file, encoding="utf-8") as f:
        input_data = json.load(f)

    # Convert to pipeline state format
    state = {"book_name": book, "validated_nouns": input_data.get("nodes", [])}

    # Run enrichment
    enriched_state = enrichment_node(state)

    # Convert back to SSOT format (same schema but with enrichment)
    output_data = input_data.copy()
    output_data["nodes"] = enriched_state.get("enriched_nouns", [])

    # Ensure output directory exists
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    # Write JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    enriched_count = len(output_data.get("nodes", []))
    print(f"AI_ENRICHMENT_WRITTEN {enriched_count} enriched nouns to {output_file}")


if __name__ == "__main__":
    main()
