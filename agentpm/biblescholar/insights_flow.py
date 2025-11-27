"""
Contextual Insights Flow (Phase 8A)
-----------------------------------
This module implements the DB-grounded contextual analysis flow.

CONTRACT:
1. All biblical content MUST come from bible_db (verse_word_links, proper_names).
2. LMs are used ONLY for formatting, summarization, and metadata extraction.
3. LMs MUST NOT invent biblical content.
4. No direct Gematria dependencies (pure semantic/contextual flow).
"""

from typing import Dict, List
from dataclasses import dataclass

from agentpm.biblescholar.bible_db_adapter import BibleDbAdapter


@dataclass
class VerseContext:
    """
    Container for DB-grounded context data.
    """

    verse_id: str
    proper_names: List[Dict]
    word_links: List[Dict]
    cross_references: List[str]
    # The LM will format this data, not invent it.


class InsightsFlow:
    """
    Orchestrates the retrieval of contextual insights from the DB
    and their formatting via LM.
    """

    def __init__(self):
        self.db = BibleDbAdapter()

    def get_verse_context(self, verse_id: str) -> VerseContext:
        """
        Retrieves raw context data from the DB.
        """
        try:
            verse_id_int = int(verse_id)
        except ValueError:
            # Handle non-integer verse_id (maybe it's a reference string?)
            # For now, assume it's an ID.
            return VerseContext(verse_id=verse_id, proper_names=[], word_links=[], cross_references=[])

        # 1. Get verse details (for cross-refs)
        verse = self.db.get_verse_by_id(verse_id_int)
        if not verse:
            return VerseContext(verse_id=verse_id, proper_names=[], word_links=[], cross_references=[])

        # 2. Get proper names
        proper_names = self.db.get_proper_names_for_verse(verse_id_int)

        # 3. Get word links
        word_links = self.db.get_word_links_for_verse(verse_id_int)

        # 4. Get cross-references
        cross_refs = self.db.get_cross_references(verse.book_name, verse.chapter_num, verse.verse_num)

        return VerseContext(
            verse_id=verse_id,
            proper_names=proper_names,
            word_links=word_links,
            cross_references=cross_refs,
        )

    def generate_insight(self, verse_id: str) -> Dict:
        """
        Main entry point: Retrieves context (DB) and formats it (LM).
        """
        context = self.get_verse_context(verse_id)
        # TODO: Call LM to format context
        return {
            "verse_id": verse_id,
            "insight": "Placeholder",
            "context": {
                "proper_names": context.proper_names,
                "word_links": context.word_links,
                "cross_references": context.cross_references,
            },
        }
