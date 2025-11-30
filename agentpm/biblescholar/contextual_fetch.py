"""
Phase 15: Contextual Fetch Layer
--------------------------------

DB-only orchestration layer that aggregates Phase-14 adapter outputs
for use by the ContextualChunkBuilder.

Rules:

* All factual content must come from the database (DB ONLY).
* No LLM calls are allowed in this module.
* Missing mappings must use explicit None / [] semantics.
"""

from typing import Any, Dict, List

from agentpm.biblescholar.relationship_adapter import RelationshipAdapter
from agentpm.biblescholar.lexicon_adapter import LexiconAdapter
from agentpm.biblescholar.bible_db_adapter import BibleDbAdapter


class ContextualFetch:
    """DB-only aggregation of BibleScholar metadata for a single verse."""

    def __init__(self, engine: Any) -> None:
        self._engine = engine
        self._relationship = RelationshipAdapter(engine)
        self._lexicon = LexiconAdapter(engine)
        self._bible = BibleDbAdapter(engine)

    def fetch_for_verse(self, verse_id: int) -> Dict[str, Any]:
        """
        Fetch raw DB-backed metadata for a given verse.

        All fields are DB-derived. This function MUST NOT call any LLMs.
        """
        verse_text: str | None = self._bible.get_verse_text(verse_id)

        # Lexical / morphology signals
        lemmas: List[str] = self._lexicon.get_lemmas_for_verse(verse_id) or []
        morph_tokens: List[str] = self._lexicon.get_morph_tokens_for_verse(verse_id) or []

        # Relationship tables
        proper_names: List[str] = self._relationship.get_proper_names_for_verse(verse_id) or []
        verse_word_links = self._relationship.get_verse_word_links(verse_id) or []

        # Cross-language signals (if available)
        greek_words = getattr(self._lexicon, "get_greek_words_for_verse", lambda _v: [])(verse_id) or []
        xlang_lemmas = getattr(self._lexicon, "get_cross_language_lemmas_for_verse", lambda _v: [])(verse_id) or []

        return {
            "verse_id": verse_id,
            "verse_text": verse_text,
            "lemmas": lemmas,
            "morph_tokens": morph_tokens,
            "proper_names": proper_names,
            "verse_word_links": verse_word_links,
            "greek_words": greek_words,
            "xlang_lemmas": xlang_lemmas,
        }
