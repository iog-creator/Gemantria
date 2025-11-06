#!/usr/bin/env python3
"""
Quick test to verify "Unknown" noun filtering logic works.

Tests the filtering logic directly without importing full pipeline modules.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ssot.noun_adapter import adapt_ai_noun


def test_unknown_noun_filtering():
    """Test that invalid/Unknown nouns are identified correctly."""
    print("Testing 'Unknown' noun filtering logic...\n")

    # Create test nouns: some valid, some invalid
    test_nouns = [
        {"surface": "אלהים", "hebrew": "אלהים", "name": "God", "gematria": 86},  # Valid
        {"surface": "Unknown", "name": "Unknown"},  # Invalid - should be filtered
        {"surface": "", "hebrew": "", "name": "Empty"},  # Invalid - empty surface
        {"hebrew_text": None, "surface": None},  # Invalid - null values
        {"surface": "אברהם", "hebrew": "אברהם", "name": "Abraham", "gematria": 248},  # Valid
        {"name": "Unknown", "surface": ""},  # Invalid - Unknown name, no Hebrew
    ]

    print(f"Input: {len(test_nouns)} test nouns")
    print("  - Expected valid: 2 (אלהים, אברהם)")
    print("  - Expected invalid: 4 (Unknown, empty, null, Unknown without Hebrew)\n")

    # Adapt nouns (what collect_nouns_node does)
    adapted = [adapt_ai_noun(n) for n in test_nouns]
    print(f"After adaptation: {len(adapted)} nouns")

    # Test validation logic (same as validate_batch_node)
    valid_nouns = []
    filtered_count = 0

    for noun in adapted:
        surface = noun.get("surface", "") or noun.get("hebrew", "") or noun.get("hebrew_text", "")
        name = noun.get("name", "")

        # Same logic as validate_batch_node
        if not surface or surface.strip() == "" or surface == "Unknown":
            filtered_count += 1
            print(f"  ❌ Filtered: surface='{surface}', name='{name}'")
            continue

        if name == "Unknown" and not surface:
            filtered_count += 1
            print("  ❌ Filtered: name='Unknown', no surface")
            continue

        valid_nouns.append(noun)
        print(f"  ✅ Valid: surface='{surface}', name='{name}'")

    print("\nValidation results:")
    print(f"  - Valid nouns: {len(valid_nouns)}")
    print(f"  - Filtered nouns: {filtered_count}")

    # Test enrichment defensive check logic
    print("\nTesting enrichment defensive check logic...")
    enrichment_filtered = 0
    for noun in valid_nouns:
        hebrew = noun.get("surface", "") or noun.get("hebrew_text", "") or noun.get("hebrew", "")
        if not hebrew or hebrew.strip() == "" or hebrew == "Unknown":
            enrichment_filtered += 1
            print(f"  ❌ Would be filtered in enrichment: surface='{hebrew}'")
        else:
            # Check prompt wouldn't contain "Unknown"
            name = noun.get("name", "") or hebrew or "Unknown"
            if name == "Unknown" or hebrew == "Unknown":
                print(f"  ❌ ERROR: Would create prompt with 'Unknown': name='{name}', hebrew='{hebrew}'")
                return False
            else:
                print(f"  ✅ Would create valid prompt: name='{name}', hebrew='{hebrew}'")

    # Verify final counts
    if len(valid_nouns) != 2:
        print(f"\n❌ ERROR: Expected 2 valid nouns, got {len(valid_nouns)}")
        return False

    if enrichment_filtered > 0:
        print(f"\n❌ ERROR: {enrichment_filtered} nouns would be filtered in enrichment (should be 0)")
        return False

    print("\n✅ All tests passed!")
    print(f"   - {len(test_nouns)} input nouns")
    print(f"   - {len(valid_nouns)} valid nouns after validation filtering")
    print(f"   - {enrichment_filtered} additional filtered in enrichment (defensive)")
    print("   - 0 'Unknown' nouns would reach enrichment\n")

    return True


if __name__ == "__main__":
    success = test_unknown_noun_filtering()
    sys.exit(0 if success else 1)
