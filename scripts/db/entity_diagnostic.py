#!/usr/bin/env python3
"""Entity diagnostic script for Phase 14 PR 14.4 PoC.

This script demonstrates the retrieval of proper names and relationship data
from bible_db for RAG context enrichment.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pmagent.biblescholar.relationship_adapter import RelationshipAdapter
from pmagent.biblescholar.lexicon_adapter import LexiconAdapter


def main() -> int:
    """Run entity diagnostic for proper names."""
    print("=" * 80)
    print("Entity Diagnostic: Proper Names (Phase 14 PR 14.4 PoC)")
    print("=" * 80)
    print()

    # Initialize adapters
    relationship_adapter = RelationshipAdapter()
    lexicon_adapter = LexiconAdapter()

    # Get Mark 1:1 verse_id
    verse_id = lexicon_adapter._verse_ref_to_id("Mark.1.1")
    if not verse_id:
        print("ERROR: Could not resolve Mark 1:1 verse_id")
        return 1

    print(f"1. Verse ID for Mark 1:1: {verse_id}")
    print()

    # Get proper names for Mark 1:1
    print("2. Proper Names for Mark 1:1:")
    print("-" * 80)
    proper_names = relationship_adapter.get_proper_names_for_verse(verse_id, limit=10)

    if not proper_names:
        print("   No proper names found (may need word matching refinement)")
    else:
        print(f"   Found {len(proper_names)} proper name(s):")
        for i, pn in enumerate(proper_names, 1):
            print(f"   {i}. {pn.unified_name}")
            if pn.type:
                print(f"      Type: {pn.type}")
            if pn.category:
                print(f"      Category: {pn.category}")
            if pn.briefest:
                print(f"      Briefest: {pn.briefest[:60]}...")
            print()

    # Get verse-word links (will be empty, but shows structure)
    print("3. Verse-Word Links for Mark 1:1:")
    print("-" * 80)
    word_links = relationship_adapter.get_verse_word_links(verse_id)
    print(f"   Found {len(word_links)} link(s)")
    if word_links:
        for link in word_links:
            print(f"   - Link ID: {link.link_id}, Word ID: {link.word_id}, Type: {link.word_type}")
    else:
        print("   (Table is empty - structure ready for population)")

    print()

    # Get enriched context
    print("4. Enriched Context for Mark 1:1:")
    print("-" * 80)
    enriched = relationship_adapter.get_enriched_context(verse_id)
    if enriched:
        print(f"   Verse ID: {enriched.verse_id}")
        print(f"   Proper Names: {len(enriched.proper_names)}")
        print(f"   Word Links: {len(enriched.word_links)}")
        if enriched.context_summary:
            print(f"   Summary: {enriched.context_summary}")
    else:
        print("   Could not retrieve enriched context")

    print()
    print("=" * 80)
    print("Entity Diagnostic Complete")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
