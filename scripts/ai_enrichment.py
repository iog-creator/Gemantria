# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
AI Enrichment Script

Wrapper script for the enrichment agent.
Reads exports/ai_nouns.json, enriches nouns, writes to exports/ai_nouns.enriched.json
Writes incrementally after each batch for real-time progress monitoring.
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

from src.nodes.enrichment import enrichment_node  # noqa: E402
from src.infra.env_loader import ensure_env_loaded  # noqa: E402


def write_incremental_output(output_file: Path, input_data: dict, enriched_nouns: list) -> None:
    """Write output file incrementally with current enriched nouns."""
    output_data = input_data.copy()
    output_data["nodes"] = enriched_nouns

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Write JSON atomically (write to temp file then rename)
    temp_file = output_file.with_suffix(".tmp.json")
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    temp_file.replace(output_file)


def main():
    """Run AI enrichment on discovered nouns with incremental writes."""
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

    # Initialize output file with empty enriched list
    write_incremental_output(Path(output_file), input_data, [])

    # Create progress callback to write incrementally after each batch
    def progress_callback(enriched_nouns_list: list):
        """Write output file after each batch with current enriched nouns."""
        write_incremental_output(Path(output_file), input_data, enriched_nouns_list)

    # Run enrichment with incremental write callback
    enriched_state = enrichment_node(state, progress_callback=progress_callback)
    enriched_nouns = enriched_state.get("enriched_nouns", [])

    # Write final output (in case callback wasn't called for last batch)
    write_incremental_output(Path(output_file), input_data, enriched_nouns)

    enriched_count = len(enriched_nouns)
    print(f"AI_ENRICHMENT_WRITTEN {enriched_count} enriched nouns to {output_file}")


if __name__ == "__main__":
    main()
