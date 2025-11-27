#!/usr/bin/env python3
"""
OPS Script: Phase 13B - Update API Documentation
================================================
Updates API documentation to reflect translation_source as required parameter.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
AGENTS_MD = REPO_ROOT / "agentpm/biblescholar/AGENTS.md"


def update_agents_md():
    """Update AGENTS.md to reflect translation_source requirement."""
    print(f"Updating {AGENTS_MD}...")
    content = AGENTS_MD.read_text()

    # Update search_flow documentation
    old_search_doc = """**API**:
- `search_verses(query: str, translation: str = "KJV", limit: int = 20) -> list[VerseRecord]`
  - Validates query length (min 2 chars)
  - Delegates to `BibleDbAdapter.search_verses`"""

    new_search_doc = """**API**:
- `search_verses(query: str, translation: str, limit: int = 20) -> list[VerseRecord]`
  - **translation**: Required translation identifier (e.g., "KJV", "ESV", "ASV", "YLT")
  - Validates query length (min 2 chars)
  - Delegates to `BibleDbAdapter.search_verses`"""

    if old_search_doc in content:
        content = content.replace(old_search_doc, new_search_doc)
        print("  ✓ Updated search_flow API documentation")

    # Update usage example
    old_example = """# Basic search
results = search_verses("beginning", "KJV", limit=5)
for verse in results:
    print(f"{verse.book_name} {verse.chapter_num}:{verse.verse_num} - {verse.text}")

# Different translation
results = search_verses("love", "ESV")"""

    new_example = """# Basic search (translation is required)
results = search_verses("beginning", "KJV", limit=5)
for verse in results:
    print(f"{verse.book_name} {verse.chapter_num}:{verse.verse_num} - {verse.text}")

# Different translation
results = search_verses("love", "ESV")"""

    if old_example in content:
        content = content.replace(old_example, new_example)
        print("  ✓ Updated search_flow usage example")

    # Update semantic search documentation if present
    old_semantic = 'translation: str = "KJV"'
    if old_semantic in content:
        # Find semantic search section
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "semantic_search" in line.lower() and "translation" in line.lower():
                # Update the line
                if old_semantic in line:
                    lines[i] = line.replace(old_semantic, "translation: str  # Required")
                    print("  ✓ Updated semantic_search documentation")
                    break
        content = "\n".join(lines)

    AGENTS_MD.write_text(content)
    print(f"✅ Updated {AGENTS_MD}")


def main() -> int:
    """Main execution."""
    print("=" * 70)
    print("Phase 13B: Update API Documentation")
    print("=" * 70)
    print()

    try:
        update_agents_md()

        print()
        print("=" * 70)
        print("✅ Phase 13B: API documentation update complete")
        print("=" * 70)
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
