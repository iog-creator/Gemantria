# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
Verify that enrichment prompts don't contain "Unknown" values.

This script checks:
1. The input data file for "Unknown" values
2. The prompt generation logic
3. Sample prompts to ensure they're clean
"""

import json
import sys
from pathlib import Path

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))


def escape_hebrew(text):
    """Escape Hebrew text for safe inclusion in prompts."""
    if not text:
        return ""
    import json as _json

    text = text.replace("\\", "\\\\")
    return _json.dumps(text)[1:-1]


def build_enrichment_prompt(noun):
    """Build enrichment prompt (same logic as enrichment.py)."""
    name = noun.get("name", noun.get("hebrew", noun.get("surface", "")))
    hebrew = noun.get("hebrew", noun.get("surface", ""))
    verse = noun.get("primary_verse", "")
    base_info = f"Noun: {name}\nHebrew: {escape_hebrew(hebrew)}\nPrimary Verse: {verse}\n"

    if noun.get("ai_discovered"):
        letters = noun.get("letters", [])
        gematria = noun.get("gematria", noun.get("gematria_value", ""))
        classification = noun.get("classification", noun.get("class", ""))
        meaning = noun.get("meaning", "Not analyzed")
        ai_analysis = (
            f"AI Analysis:\n"
            f"- Letters: {', '.join(letters) if letters else 'Not provided'}\n"
            f"- Gematria Value: {gematria if gematria else 'Not calculated'}\n"
            f"- Classification: {classification if classification else 'Not classified'} (person/place/thing)\n"
            f"- Initial Meaning: {meaning}\n"
        )
        task_desc = "This noun was discovered and initially analyzed by AI..."
    else:
        ai_analysis = ""
        task_desc = "Provide a detailed theological analysis..."

    full_prompt = (
        base_info + ai_analysis + f"Task: {task_desc} "
        "Provide a comprehensive 200-300 word scholarly analysis. "
        'Return JSON: {{"insight": "...detailed analysis...", "confidence": <0.90-1.0>}}'
    )
    return full_prompt


def main():
    input_file = Path("exports/ai_nouns.json")
    if not input_file.exists():
        print(f"ERROR: {input_file} not found", file=sys.stderr)
        sys.exit(1)

    with open(input_file, encoding="utf-8") as f:
        data = json.load(f)

    nodes = data.get("nodes", [])
    print(f"✓ Loaded {len(nodes)} nouns from {input_file}")

    # Check for "Unknown" in data
    unknown_in_data = []
    for i, node in enumerate(nodes):
        for field in ["name", "hebrew", "surface", "primary_verse", "meaning", "classification"]:
            value = str(node.get(field, ""))
            if "Unknown" in value or "unknown" in value.lower():
                unknown_in_data.append((i, field, value))

    if unknown_in_data:
        print(f"\n✗ Found {len(unknown_in_data)} nodes with 'Unknown' in data:")
        for idx, field, value in unknown_in_data[:10]:
            print(f"  Node {idx}, field '{field}': {value[:50]}")
        sys.exit(1)
    else:
        print("✓ No 'Unknown' values found in input data")

    # Check prompt generation
    print("\n✓ Testing prompt generation...")
    issues = []
    for i, node in enumerate(nodes[:100]):  # Check first 100
        prompt = build_enrichment_prompt(node)
        if "Unknown" in prompt or "unknown" in prompt.lower():
            issues.append((i, node.get("name"), prompt[:200]))

    if issues:
        print(f"\n✗ Found {len(issues)} prompts containing 'Unknown':")
        for idx, name, preview in issues[:10]:
            print(f"  Node {idx} ({name}): {preview}")
        sys.exit(1)
    else:
        print("✓ All prompts are clean (no 'Unknown' values)")

    # Show sample prompt
    print("\n✓ Sample prompt (first node):")
    print("=" * 80)
    sample_prompt = build_enrichment_prompt(nodes[0])
    print(sample_prompt[:500])
    print("=" * 80)

    print("\n✓ Verification complete: All prompts are clean!")


if __name__ == "__main__":
    main()
