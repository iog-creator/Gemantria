#!/usr/bin/env python3
"""
Test enrichment fix: verify Hebrew text is used instead of "Unknown".

Tests the enrichment node with ingested nouns to ensure:
1. Hebrew text is correctly extracted from adapted nouns
2. Prompts use Hebrew text, not "Unknown"
3. No "Unknown" nouns reach the model
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ssot.noun_adapter import adapt_ai_noun


def test_enrichment_prompt_generation():
    """Test that enrichment prompts use Hebrew text correctly."""
    print("Testing enrichment prompt generation fix...\n")

    # Load ingested nouns
    with open("exports/ai_nouns.db_morph.json") as f:
        data = json.load(f)

    # Adapt first 5 nouns
    adapted_nouns = [adapt_ai_noun(n) for n in data["nodes"][:5]]

    print(f"Testing {len(adapted_nouns)} nouns from ingestion...\n")

    # Simulate the exact logic from enrichment.py build_enrichment_prompt
    def escape_hebrew(text):
        return text.encode("unicode_escape").decode("ascii")

    issues = []
    for idx, noun in enumerate(adapted_nouns):
        # Get Hebrew text (same logic as enrichment.py)
        hebrew = noun.get("surface", "") or noun.get("hebrew_text", "") or noun.get("hebrew", "")
        name = noun.get("name", "") or hebrew or "Unknown"

        # Build prompt fragment (same as enrichment.py)
        base_info = (
            f"Noun: {name}\nHebrew: {escape_hebrew(hebrew)}\nPrimary Verse: {noun.get('primary_verse', 'Unknown')}\n"
        )

        # Check for issues
        if name == "Unknown":
            issues.append(f"Noun {idx}: name is 'Unknown' (hebrew={hebrew!r})")
        if not hebrew or hebrew.strip() == "":
            issues.append(f"Noun {idx}: empty Hebrew text (name={name!r})")
        if "Noun: Unknown\n" in base_info:
            issues.append(f"Noun {idx}: prompt contains 'Noun: Unknown'")

        print(f"Noun {idx + 1}:")
        print(f"  surface: {noun.get('surface', '')[:20]!r}")
        print(f"  name (resolved): {name[:20]!r}")
        print(f"  prompt start: {base_info[:80]}...")
        print()

    # Summary
    if issues:
        print("❌ ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ All nouns correctly use Hebrew text in prompts")
        print("✅ No 'Unknown' nouns found")
        return True


if __name__ == "__main__":
    try:
        success = test_enrichment_prompt_generation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
