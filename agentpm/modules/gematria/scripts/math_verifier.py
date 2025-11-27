# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
Math Verifier Script

Standalone script to verify gematria calculations using MATH_MODEL.
Reads exports/ai_nouns.enriched.json, verifies gematria, writes back.
"""

import os
import sys
import json
from pathlib import Path

# Add src to path
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

from agentpm.modules.gematria.utils.math_verifier import math_verifier_node  # noqa: E402
from src.infra.env_loader import ensure_env_loaded  # noqa: E402

ensure_env_loaded()


def main():
    """Run math verification on enriched nouns."""
    input_file = os.environ.get("INPUT", "exports/ai_nouns.enriched.json")
    output_file = os.environ.get("OUTPUT", input_file)  # Default to overwrite input
    book = os.environ.get("BOOK", "Genesis")

    print(f">> Math Verifier for {book}", file=sys.stderr)

    # Read input nouns
    if not Path(input_file).exists():
        print(f"ERROR: Input file {input_file} not found", file=sys.stderr)
        sys.exit(1)

    with open(input_file, encoding="utf-8") as f:
        input_data = json.load(f)

    # Convert to pipeline state format
    state = {
        "book_name": book,
        "book": book,
        "enriched_nouns": input_data.get("nodes", []),
        "run_id": "math_verifier_standalone",
    }

    # Run math verification
    verified_state = math_verifier_node(state)

    # Convert back to SSOT format
    output_data = input_data.copy()
    output_data["nodes"] = verified_state.get("enriched_nouns", [])

    # Ensure output directory exists
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    # Write JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    verified_count = len(output_data.get("nodes", []))
    math_checks = sum(1 for n in output_data.get("nodes", []) if n.get("analysis", {}).get("math_check"))
    print(f"MATH_VERIFICATION_COMPLETE {verified_count} nouns processed, {math_checks} with math_check")


if __name__ == "__main__":
    main()
