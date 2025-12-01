"""BibleScholar contextual insights flow (read-only).

This module aggregates data from various BibleScholar flows (passage, lexicon, vector)
into a unified VerseContext object and provides formatting for LLM consumption.

See:
- docs/SSOT/BIBLESCHOLAR_MIGRATION_PLAN.md (Phase 8A)
- agentpm/biblescholar/AGENTS.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


from agentpm.biblescholar.bible_passage_flow import fetch_verse
from agentpm.biblescholar.lexicon_adapter import LexiconEntry
from agentpm.biblescholar.lexicon_flow import fetch_word_study
from agentpm.biblescholar.vector_adapter import VerseSimilarityResult
from agentpm.biblescholar.vector_flow import similar_verses_for_reference


@dataclass
class VerseContext:
    """Aggregated context for a single verse."""

    reference: str
    primary_text: str  # KJV text
    secondary_texts: dict[str, str] = field(default_factory=dict)  # Other translations
    lexicon_entries: list[LexiconEntry] = field(default_factory=list)
    similar_verses: list[VerseSimilarityResult] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


def get_verse_context(
    reference: str,
    translations: list[str] | None = None,
    include_lexicon: bool = True,
    include_similar: bool = True,
    similarity_limit: int = 5,
) -> VerseContext | None:
    """Aggregate context for a verse from multiple sources.

    Args:
        reference: Bible reference (e.g., "Genesis 1:1").
        translations: List of additional translations to fetch (default: ["KJV"]).
                      Note: KJV is always fetched as primary text.
        include_lexicon: Whether to include lexicon entries (word study).
        include_similar: Whether to include similar verses (vector search).
        similarity_limit: Number of similar verses to fetch.

    Returns:
        VerseContext object if verse found, None otherwise.
    """
    if translations is None:
        translations = ["KJV"]

    # 1. Fetch primary text (KJV)
    primary_verse = fetch_verse(reference, "KJV")
    if not primary_verse:
        return None

    context = VerseContext(
        reference=f"{primary_verse.book_name} {primary_verse.chapter_num}:{primary_verse.verse_num}",
        primary_text=primary_verse.text,
    )

    # 2. Fetch secondary translations
    for trans in translations:
        if trans == "KJV":
            continue
        verse = fetch_verse(reference, trans)
        if verse:
            context.secondary_texts[trans] = verse.text

    # 3. Fetch lexicon data
    if include_lexicon:
        word_study = fetch_word_study(reference)
        if word_study:
            context.lexicon_entries = word_study.entries

    # 4. Fetch similar verses
    if include_similar:
        similar = similar_verses_for_reference(reference, limit=similarity_limit)
        context.similar_verses = similar

    return context


def format_context_for_llm(context: VerseContext) -> str:
    """Format verse context into a markdown string for LLM consumption.

    Args:
        context: VerseContext object.

    Returns:
        Markdown formatted string.
    """
    lines = []

    # Header
    lines.append(f"# Context: {context.reference}")
    lines.append("")

    # Primary Text
    lines.append("## Text (KJV)")
    lines.append(f"> {context.primary_text}")
    lines.append("")

    # Secondary Texts
    if context.secondary_texts:
        lines.append("## Other Translations")
        for trans, text in context.secondary_texts.items():
            lines.append(f"**{trans}**: {text}")
        lines.append("")

    # Lexicon
    if context.lexicon_entries:
        lines.append("## Lexicon (Original Language)")
        for entry in context.lexicon_entries:
            # Heuristic for Hebrew vs Greek based on Strong's ID
            lang = "Hebrew" if entry.strongs_id.startswith("H") else "Greek"
            definition = entry.gloss if hasattr(entry, "gloss") else getattr(entry, "definition", "")
            lines.append(f"- **{entry.lemma}** ({lang} {entry.strongs_id}): {definition}")
        lines.append("")

    # Similar Verses
    if context.similar_verses:
        lines.append("## Similar Verses (Semantic)")
        for v in context.similar_verses:
            lines.append(f"- **{v.book_name} {v.chapter_num}:{v.verse_num}** ({v.similarity_score:.2f}): {v.text}")
        lines.append("")

    return "\n".join(lines)
