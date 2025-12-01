#!/usr/bin/env python3
"""Contextual search script for Phase 14 PR 14.4 PoC.

This script demonstrates enhanced RAG context retrieval using relationship tables.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from agentpm.biblescholar.relationship_adapter import RelationshipAdapter
from agentpm.biblescholar.lexicon_adapter import LexiconAdapter
from agentpm.biblescholar.bible_db_adapter import BibleDbAdapter


def main() -> int:
    """Run contextual search with enriched context."""
    print("=" * 80)
    print("Contextual Search: Enhanced RAG Context (Phase 14 PR 14.4 PoC)")
    print("=" * 80)
    print()

    # Initialize adapters
    relationship_adapter = RelationshipAdapter()
    lexicon_adapter = LexiconAdapter()
    bible_adapter = BibleDbAdapter()

    # Get verse reference
    verse_ref = "Mark.1.1"
    query = "Who is the forerunner in this verse?"

    print(f"Verse: {verse_ref}")
    print(f"Query: {query}")
    print()

    # Get verse_id
    verse_id = lexicon_adapter._verse_ref_to_id(verse_ref)
    if not verse_id:
        print("ERROR: Could not resolve verse_id")
        return 1

    # Get base verse text
    print("1. Base Verse Text:")
    print("-" * 80)
    # Parse reference to get book, chapter, verse
    from agentpm.biblescholar.reference_parser import parse_reference

    parsed = parse_reference(verse_ref)
    passage = bible_adapter.get_passage(parsed.book, parsed.chapter, parsed.verse, parsed.chapter, parsed.verse)
    if passage:
        for verse in passage:
            print(f"   {verse.book_name} {verse.chapter_num}:{verse.verse_num} - {verse.text}")
    else:
        print("   Could not retrieve verse text")
    print()

    # Get enriched context
    print("2. Enriched Context (Proper Names & Relationships):")
    print("-" * 80)
    enriched = relationship_adapter.get_enriched_context(verse_id)
    if enriched:
        print(f"   Verse ID: {enriched.verse_id}")
        print(f"   Proper Names Found: {len(enriched.proper_names)}")
        if enriched.proper_names:
            print("   Proper Names:")
            for pn in enriched.proper_names[:5]:
                print(f"     - {pn.unified_name}")
                if pn.type:
                    print(f"       Type: {pn.type}")
                if pn.briefest:
                    print(f"       Briefest: {pn.briefest[:60]}...")
        print(f"   Word Links: {len(enriched.word_links)}")
        if enriched.context_summary:
            print(f"   Context Summary: {enriched.context_summary}")
    else:
        print("   Could not retrieve enriched context")
    print()

    # Demonstrate RAG enhancement
    print("3. RAG Context Enhancement:")
    print("-" * 80)
    print("   The enriched context provides:")
    print("   - Proper name identification for entity recognition")
    print("   - Relationship data for contextual understanding")
    print("   - Word links for semantic connections")
    print("   - Enhanced grounding for LLM responses")
    print()
    print("   Example: Query about 'forerunner' can be enriched with:")
    if enriched and enriched.proper_names:
        for pn in enriched.proper_names:
            if "John" in pn.unified_name or "Baptist" in pn.unified_name:
                print(f"     - {pn.unified_name}: {pn.briefest or pn.brief or 'N/A'}")
    print()

    print("=" * 80)
    print("Contextual Search Complete")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
