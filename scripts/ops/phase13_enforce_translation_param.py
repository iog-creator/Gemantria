#!/usr/bin/env python3
"""
OPS Script: Phase 13B - Enforce Translation Source Parameter
=============================================================
Removes KJV default from search_flow.py and makes translation_source required.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SEARCH_FLOW = REPO_ROOT / "agentpm/biblescholar/search_flow.py"
BIBLE_TOOL = REPO_ROOT / "agentpm/tools/bible.py"
API_ROUTER = REPO_ROOT / "src/services/routers/biblescholar.py"


def update_search_flow():
    """Remove KJV default from search_verses function."""
    print(f"Updating {SEARCH_FLOW}...")
    content = SEARCH_FLOW.read_text()

    # Remove default from function signature
    old_sig = 'def search_verses(\n    query: str, translation: str = "KJV", limit: int = 20, adapter: BibleDbAdapter | None = None\n) -> list[VerseRecord]:'
    new_sig = "def search_verses(\n    query: str, translation: str, limit: int = 20, adapter: BibleDbAdapter | None = None\n) -> list[VerseRecord]:"

    if old_sig in content:
        content = content.replace(old_sig, new_sig)
        print("  ✓ Removed KJV default from search_verses() signature")
    else:
        # Try alternative format
        old_sig2 = 'translation: str = "KJV"'
        new_sig2 = "translation: str"
        if old_sig2 in content:
            content = content.replace(old_sig2, new_sig2)
            print("  ✓ Removed KJV default from translation parameter")
        else:
            print("  ⚠ Could not find KJV default in search_verses()")

    # Update docstring
    old_doc = 'translation: Translation identifier (default: "KJV").'
    new_doc = 'translation: Translation identifier (required, e.g., "KJV", "ESV", "ASV", "YLT").'
    if old_doc in content:
        content = content.replace(old_doc, new_doc)
        print("  ✓ Updated docstring")

    SEARCH_FLOW.write_text(content)
    print(f"✅ Updated {SEARCH_FLOW}")


def update_bible_tool():
    """Remove KJV default from search_bible_verses tool function."""
    print(f"\nUpdating {BIBLE_TOOL}...")
    content = BIBLE_TOOL.read_text()

    # Remove default from function signature
    old_sig = 'def search_bible_verses(query: str, translation: str = "KJV", limit: int = 10, **kwargs: Any) -> dict[str, Any]:'
    new_sig = "def search_bible_verses(query: str, translation: str, limit: int = 10, **kwargs: Any) -> dict[str, Any]:"

    if old_sig in content:
        content = content.replace(old_sig, new_sig)
        print("  ✓ Removed KJV default from search_bible_verses() signature")
    else:
        # Try alternative format
        old_sig2 = 'translation: str = "KJV"'
        new_sig2 = "translation: str"
        if old_sig2 in content:
            content = content.replace(old_sig2, new_sig2)
            print("  ✓ Removed KJV default from translation parameter")
        else:
            print("  ⚠ Could not find KJV default in search_bible_verses()")

    # Update docstring
    old_doc = 'translation: Translation identifier (default: "KJV").'
    new_doc = 'translation: Translation identifier (required, e.g., "KJV", "ESV", "ASV", "YLT").'
    if old_doc in content:
        content = content.replace(old_doc, new_doc)
        print("  ✓ Updated docstring")

    BIBLE_TOOL.write_text(content)
    print(f"✅ Updated {BIBLE_TOOL}")


def update_api_router():
    """Remove KJV defaults from API router endpoints."""
    print(f"\nUpdating {API_ROUTER}...")
    content = API_ROUTER.read_text()

    # Update /search endpoint
    old_search = 'translation: str = "KJV",'
    new_search = (
        'translation: str = Query(..., description="Translation identifier (required, e.g., KJV, ESV, ASV, YLT)"),'
    )
    if old_search in content:
        content = content.replace(old_search, new_search)
        print("  ✓ Updated /search endpoint to require translation")

    # Update /semantic endpoint
    old_semantic = 'translation: str = "KJV",'
    if old_semantic in content and content.count(old_semantic) > 1:
        # Replace second occurrence (semantic search)
        parts = content.split(old_semantic, 1)
        if len(parts) > 1:
            # Find the semantic search function
            semantic_part = parts[1]
            if "api_semantic_search" in semantic_part[:200]:
                content = parts[0] + new_search + semantic_part
                print("  ✓ Updated /semantic endpoint to require translation")
            else:
                # Already replaced, try the second occurrence
                parts2 = semantic_part.split(old_semantic, 1)
                if len(parts2) > 1:
                    content = parts[0] + new_search + parts2[0] + new_search + parts2[1]
                    print("  ✓ Updated /semantic endpoint to require translation")

    # Update insights endpoint (hardcoded translations list)
    old_insights = 'translations=["KJV", "ESV"],  # Example defaults'
    new_insights = 'translations=["KJV", "ESV"],  # TODO: Make this configurable via query param'
    if old_insights in content:
        content = content.replace(old_insights, new_insights)
        print("  ✓ Updated insights endpoint comment")

    # Update contextual insights endpoint
    old_contextual = 'translations=["KJV", "ESV"],'
    if old_contextual in content:
        # Only update the one in api_get_contextual_insights
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "api_get_contextual_insights" in lines[max(0, i - 5) : i + 1] and old_contextual in line:
                lines[i] = line.replace(
                    old_contextual, 'translations=["KJV", "ESV"],  # TODO: Make this configurable via query param'
                )
                print("  ✓ Updated contextual insights endpoint comment")
                break
        content = "\n".join(lines)

    API_ROUTER.write_text(content)
    print(f"✅ Updated {API_ROUTER}")


def main() -> int:
    """Main execution."""
    print("=" * 70)
    print("Phase 13B: Enforce Translation Source Parameter")
    print("=" * 70)
    print()

    try:
        update_search_flow()
        update_bible_tool()
        update_api_router()

        print()
        print("=" * 70)
        print("✅ Phase 13B: Translation parameter enforcement complete")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  1. Update API documentation (run phase13_update_api_docs.py)")
        print("  2. Run tests to verify changes")
        print("  3. Run AWCG to generate completion envelope")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
