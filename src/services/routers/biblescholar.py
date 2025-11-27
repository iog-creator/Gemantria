"""
BibleScholar API Router.

Exposes BibleScholar features (search, semantic search, lexicon, cross-language)
as REST endpoints for the Orchestrator UI.
"""

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from agentpm.biblescholar.search_flow import search_verses
from agentpm.biblescholar.semantic_search_flow import semantic_search
from agentpm.biblescholar.lexicon_flow import fetch_lexicon_entry, fetch_word_study
from agentpm.biblescholar.cross_language_flow import analyze_word_in_context
from agentpm.biblescholar.cross_language_semantic_flow import find_cross_language_connections
from agentpm.biblescholar.passage import get_passage_and_commentary
from agentpm.biblescholar.gematria_flow import compute_verse_gematria
from agentpm.biblescholar.bible_db_adapter import BibleDbAdapter
from agentpm.db.loader import get_bible_engine
from sqlalchemy import text
from agentpm.modules.gematria.utils.osis import normalize_book_to_osis

router = APIRouter(prefix="/api/bible", tags=["biblescholar"])
biblescholar_router = APIRouter(prefix="/api/biblescholar", tags=["biblescholar"])


# --- DTOs ---


class VerseResult(BaseModel):
    book: str
    chapter: int
    verse: int
    text: str
    translation: str


class SearchResponse(BaseModel):
    results: list[VerseResult]
    count: int


class SemanticVerseResult(BaseModel):
    book: str
    chapter: int
    verse: int
    text: str
    similarity: float


class SemanticSearchResponse(BaseModel):
    query: str
    results: list[SemanticVerseResult]
    total: int


class LexiconEntryResponse(BaseModel):
    strongs_id: str
    lemma: str
    gloss: str | None
    definition: str | None
    transliteration: str | None
    usage: str | None


class WordStudyResponse(BaseModel):
    reference: str
    entries: list[LexiconEntryResponse]


class CrossLanguageMatchResponse(BaseModel):
    source_strongs: str
    target_strongs: str
    target_lemma: str
    similarity_score: float
    common_verses: list[str]


class WordAnalysisResponse(BaseModel):
    strongs_id: str
    lemma: str
    gloss: str | None
    occurrence_count: int
    related_verses: list[str]


class CrossLanguageResponse(BaseModel):
    strongs_id: str
    reference: str | None
    word_analysis: WordAnalysisResponse | None
    connections: list[CrossLanguageMatchResponse]
    connections_count: int
    errors: list[str]


# --- Endpoints ---


@router.get("/search", response_model=SearchResponse)
async def api_search_verses(
    q: str = Query(..., min_length=2, description="Keyword search query"),
    translation: str = Query(..., description="Translation identifier (required, e.g., KJV, ESV, ASV, YLT)"),
    limit: int = 20,
):
    """Keyword search for verses."""
    try:
        results = search_verses(q, translation=translation, limit=limit)
        return SearchResponse(
            results=[
                VerseResult(
                    book=r.book_name,
                    chapter=r.chapter_num,
                    verse=r.verse_num,
                    text=r.text,
                    translation=r.translation_source,
                )
                for r in results
            ],
            count=len(results),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/semantic", response_model=SemanticSearchResponse)
async def api_semantic_search(
    q: str = Query(..., description="Semantic search query"),
    limit: int = 20,
    translation: str = Query(..., description="Translation identifier (required, e.g., KJV, ESV, ASV, YLT)"),
):
    """Semantic search for verses."""
    try:
        result = semantic_search(q, limit=limit, translation=translation)
        return SemanticSearchResponse(
            query=result.query,
            results=[
                SemanticVerseResult(
                    book=r.book_name,
                    chapter=r.chapter_num,
                    verse=r.verse_num,
                    text=r.text,
                    similarity=r.similarity_score,
                )
                for r in result.results
            ],
            total=result.total_results,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/lexicon/{strongs_id}", response_model=LexiconEntryResponse)
async def api_get_lexicon(strongs_id: str):
    """Get lexicon entry by Strong's ID."""
    entry = fetch_lexicon_entry(strongs_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Lexicon entry not found")

    return LexiconEntryResponse(
        strongs_id=entry.strongs_id,
        lemma=entry.lemma,
        gloss=entry.gloss,
        definition=entry.definition,
        transliteration=entry.transliteration,
        usage=entry.usage,
    )


@router.get("/word-study", response_model=WordStudyResponse)
async def api_word_study(ref: str = Query(..., description="Bible reference (e.g. 'Genesis 1:1')")):
    """Get word study (lexicon entries) for a verse."""
    try:
        result = fetch_word_study(ref)
        return WordStudyResponse(
            reference=result.reference,
            entries=[
                LexiconEntryResponse(
                    strongs_id=e.strongs_id,
                    lemma=e.lemma,
                    gloss=e.gloss,
                    definition=e.definition,
                    transliteration=e.transliteration,
                    usage=e.usage,
                )
                for e in result.entries
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/cross-language/{strongs_id}", response_model=list[CrossLanguageMatchResponse])
async def api_cross_language(strongs_id: str, limit: int = 10):
    """Find cross-language connections for a Strong's ID."""
    try:
        matches = find_cross_language_connections(strongs_id, limit=limit)
        return [
            CrossLanguageMatchResponse(
                source_strongs=m.source_strongs,
                target_strongs=m.target_strongs,
                target_lemma=m.target_lemma,
                similarity_score=m.similarity_score,
                common_verses=m.common_verses,
            )
            for m in matches
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# --- Insights ---


class VerseContextResponse(BaseModel):
    reference: str
    primary_text: str
    secondary_texts: dict[str, str]
    lexicon_entries: list[LexiconEntryResponse]
    similar_verses: list[SemanticVerseResult]


class InsightsResponse(BaseModel):
    reference: str
    insight_text: str
    source: str  # "lm_theology" | "raw_context"
    context: VerseContextResponse
    errors: list[str]


@router.get("/insights/{ref}", response_model=VerseContextResponse)
async def api_get_insights(ref: str):
    """Get aggregated insights for a verse."""
    try:
        # Normalize ref (simple replacement for now, ideally use reference_parser)
        normalized_ref = ref.replace(".", " ")

        from agentpm.biblescholar.insights_flow import get_verse_context

        context = get_verse_context(
            reference=normalized_ref,
            translations=["KJV", "ESV"],  # TODO: Make this configurable via query param
            include_lexicon=True,
            include_similar=True,
        )

        if not context:
            raise HTTPException(status_code=404, detail="Verse not found")

        return VerseContextResponse(
            reference=context.reference,
            primary_text=context.primary_text,
            secondary_texts=context.secondary_texts,
            lexicon_entries=[
                LexiconEntryResponse(
                    strongs_id=e.strongs_id,
                    lemma=e.lemma,
                    gloss=e.gloss,
                    definition=e.definition,
                    transliteration=e.transliteration,
                    usage=e.usage,
                )
                for e in context.lexicon_entries
            ],
            similar_verses=[
                SemanticVerseResult(
                    book=v.book_name,
                    chapter=v.chapter_num,
                    verse=v.verse_num,
                    text=v.text,
                    similarity=v.similarity_score,
                )
                for v in context.similar_verses
            ],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# --- Passage with Gematria ---


class GematriaSystemResult(BaseModel):
    system: str
    value: int
    normalized: str
    letters: list[str]


class VerseWithGematria(BaseModel):
    book: str
    chapter: int
    verse: int
    text: str
    gematria: dict[str, GematriaSystemResult] | None = None  # None if Hebrew text unavailable


class PassageResponse(BaseModel):
    reference: str
    verses: list[VerseWithGematria]
    commentary: dict[str, Any]
    errors: list[str]


def _get_hebrew_text_for_verse(verse_id: int) -> str | None:
    """Get Hebrew text for a verse from bible_db.

    Args:
        verse_id: Verse ID from bible.verses table.

    Returns:
        Hebrew text string or None if not found or not OT verse.
    """
    try:
        engine = get_bible_engine()
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT hw.word_text
                    FROM bible.hebrew_ot_words hw
                    WHERE hw.verse_id = :verse_id
                      AND LEFT(hw.strongs_id, 1) = 'H'
                    ORDER BY hw.word_position
                """),
                {"verse_id": verse_id},
            )
            words = [row[0] for row in result]
            if words:
                return " ".join(words)
        return None
    except Exception:
        return None


@biblescholar_router.get("/passage", response_model=PassageResponse)
async def api_get_passage_with_gematria(
    reference: str = Query(..., description="Bible reference (e.g., 'John 3:16-18')"),
    translation: str = Query(..., description="Translation identifier (required, e.g., KJV, ESV, ASV, YLT)"),
    use_lm: bool = Query(False, description="Use AI commentary (default: False, requires explicit opt-in)"),
):
    """Get Bible passage with Gematria calculations.

    For Old Testament verses, computes Gematria values from Hebrew text.
    For New Testament verses, Gematria is None.
    """
    try:
        # Get passage and commentary
        passage_data = get_passage_and_commentary(reference, translation_source=translation, use_lm=use_lm)

        # Get Hebrew text and compute Gematria for each verse
        verses_with_gematria = []
        adapter = BibleDbAdapter()

        for verse in passage_data["verses"]:
            # Get verse record to access verse_id
            verse_record = adapter.get_verse(verse["book"], verse["chapter"], verse["verse"])

            gematria_results = None
            if verse_record:
                # Get Hebrew text
                hebrew_text = _get_hebrew_text_for_verse(verse_record.verse_id)

                if hebrew_text:
                    # Convert to OSIS format
                    osis_book = normalize_book_to_osis(verse["book"].lower())
                    if osis_book:
                        osis_ref = f"{osis_book}.{verse['chapter']}.{verse['verse']}"
                        # Compute Gematria
                        try:
                            gematria_summary = compute_verse_gematria(hebrew_text, osis_ref)
                            gematria_results = {
                                system: GematriaSystemResult(
                                    system=system,
                                    value=result.value,
                                    normalized=result.normalized,
                                    letters=result.letters,
                                )
                                for system, result in gematria_summary.systems.items()
                            }
                        except Exception:
                            # Gematria computation failed, continue without it
                            pass

            verses_with_gematria.append(
                VerseWithGematria(
                    book=verse["book"],
                    chapter=verse["chapter"],
                    verse=verse["verse"],
                    text=verse["text"],
                    gematria=gematria_results,
                )
            )

        return PassageResponse(
            reference=passage_data["reference"],
            verses=verses_with_gematria,
            commentary=passage_data["commentary"],
            errors=passage_data["errors"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@biblescholar_router.get("/insights", response_model=InsightsResponse)
async def api_get_contextual_insights(
    reference: str = Query(..., description="Bible reference (e.g., 'John 3:16')"),
    use_lm: bool = Query(False, description="Use LM synthesis (default: False, requires explicit opt-in)"),
):
    """Get contextual insights for a verse using DB-grounded LM synthesis.

    This endpoint:
    1. Gathers DB context (primary text, lexicon entries, similar verses)
    2. Formats context for LLM consumption
    3. Calls theology LM to synthesize insights (DB-grounded)
    4. Returns synthesized insight text with raw context

    The LM only synthesizes/formats data from bible_db; it never invents content.
    """
    try:
        from agentpm.biblescholar.insights_flow import get_verse_context, format_context_for_llm
        from agentpm.adapters.theology import chat as theology_chat

        # Normalize reference
        normalized_ref = reference.replace(".", " ")

        # 1. Gather DB context
        context = get_verse_context(
            reference=normalized_ref,
            translations=["KJV", "ESV"],
            include_lexicon=True,
            include_similar=True,
            similarity_limit=5,
        )

        if not context:
            raise HTTPException(status_code=404, detail=f"Verse not found: {reference}")

        # 2. Build VerseContextResponse for return
        context_response = VerseContextResponse(
            reference=context.reference,
            primary_text=context.primary_text,
            secondary_texts=context.secondary_texts,
            lexicon_entries=[
                LexiconEntryResponse(
                    strongs_id=e.strongs_id,
                    lemma=e.lemma,
                    gloss=e.gloss,
                    definition=e.definition,
                    transliteration=e.transliteration,
                    usage=e.usage,
                )
                for e in context.lexicon_entries
            ],
            similar_verses=[
                SemanticVerseResult(
                    book=v.book_name,
                    chapter=v.chapter_num,
                    verse=v.verse_num,
                    text=v.text,
                    similarity=v.similarity_score,
                )
                for v in context.similar_verses
            ],
        )

        # 3. Generate insight text
        insight_text = ""
        source = "raw_context"
        errors = []

        if use_lm:
            try:
                # Format context for LLM
                formatted_context = format_context_for_llm(context)

                # System prompt emphasizing DB-grounded synthesis
                system_prompt = """You are a Christian Bible expert. Synthesize insights from the provided database context.

CRITICAL RULE: All content must be grounded in the provided data. You may only:
- Summarize and format the provided text, lexicon entries, and similar verses
- Connect themes and patterns visible in the provided context
- Provide theological interpretation based on the provided data

You must NOT:
- Invent content not present in the provided context
- Add external knowledge not supported by the provided data
- Speculate beyond what the provided context allows

Keep insights concise (2-4 paragraphs) and clearly reference the provided context."""

                user_prompt = f"""Based on the following database context, provide a theological insight:

{formatted_context}

Insight:"""

                # Call theology LM
                insight_text = theology_chat(user_prompt, system=system_prompt)
                source = "lm_theology"
            except Exception as lm_error:
                # LM unavailable - return raw context summary
                errors.append(f"LM synthesis unavailable: {lm_error!s}")
                insight_text = f"Context for {context.reference}:\n\nPrimary Text: {context.primary_text}"
                if context.lexicon_entries:
                    insight_text += f"\n\nLexicon Entries: {len(context.lexicon_entries)} word(s) found"
                if context.similar_verses:
                    insight_text += f"\n\nSimilar Verses: {len(context.similar_verses)} verse(s) found"
                source = "raw_context"
        else:
            # Return raw context summary
            insight_text = f"Context for {context.reference}:\n\nPrimary Text: {context.primary_text}"
            if context.lexicon_entries:
                insight_text += f"\n\nLexicon Entries: {len(context.lexicon_entries)} word(s) found"
            if context.similar_verses:
                insight_text += f"\n\nSimilar Verses: {len(context.similar_verses)} verse(s) found"
            source = "raw_context"

        return InsightsResponse(
            reference=context.reference,
            insight_text=insight_text,
            source=source,
            context=context_response,
            errors=errors,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@biblescholar_router.get("/cross-language", response_model=CrossLanguageResponse)
async def api_cross_language_search(
    strongs_id: str = Query(..., description="Strong's number (e.g., 'H7965' or 'G1')"),
    reference: str | None = Query(None, description="Optional Bible reference (e.g., 'Genesis 1:1')"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of connections to return"),
):
    """Find cross-language connections for a Strong's number.

    This endpoint:
    1. Analyzes the word in context (if reference provided)
    2. Finds cross-language connections (Hebrew↔Greek) using vector similarity
    3. Returns word analysis and connection matches

    Uses DB-grounded vector search to find semantically similar verses in the other language.
    """
    try:
        errors = []

        # 1. Analyze word in context (if reference provided)
        word_analysis = None
        if reference:
            try:
                analysis = analyze_word_in_context(reference, strongs_id)
                if analysis:
                    word_analysis = WordAnalysisResponse(
                        strongs_id=analysis.strongs_id,
                        lemma=analysis.lemma,
                        gloss=analysis.gloss,
                        occurrence_count=analysis.occurrence_count,
                        related_verses=analysis.related_verses,
                    )
                else:
                    errors.append(f"Word {strongs_id} not found in reference {reference}")
            except Exception as e:
                errors.append(f"Word analysis failed: {e!s}")

        # 2. Find cross-language connections
        try:
            matches = find_cross_language_connections(strongs_id=strongs_id, reference=reference, limit=limit)

            connections = [
                CrossLanguageMatchResponse(
                    source_strongs=m.source_strongs,
                    target_strongs=m.target_strongs,
                    target_lemma=m.target_lemma,
                    similarity_score=m.similarity_score,
                    common_verses=m.common_verses,
                )
                for m in matches
            ]
        except Exception as e:
            errors.append(f"Cross-language search failed: {e!s}")
            connections = []

        return CrossLanguageResponse(
            strongs_id=strongs_id,
            reference=reference,
            word_analysis=word_analysis,
            connections=connections,
            connections_count=len(connections),
            errors=errors,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
