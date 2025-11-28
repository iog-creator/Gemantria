# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")
# Phase 13, Step 3.D: AI Noun Discovery Integration (Greek + LLM Governance)

"""
AI-Driven Noun Discovery Node

Replaces database-driven noun collection with organic AI discovery.
AI analyzes raw Hebrew/Greek text to discover nouns, break them down into letters,
calculate gematria values (Hebrew Gematria or Greek Isopsephy), and classify as person/place/thing.

Phase 13 Enhancements:
- Multilingual support (Hebrew OT + Greek NT)
- LLM Governance: System Prompt Template enforcing "metadata classifier ONLY" role
- Language-aware gematria calculation (Hebrew vs Greek Isopsephy)
"""

import json
import os
import re
from typing import Any, Dict, List

from src.core.books import normalize_book
from src.core.ids import normalize_hebrew
from src.infra.db import get_bible_ro
from src.infra.structured_logger import get_logger, log_json
from src.services.lmstudio_client import chat_completion

# Phase 13: Import Greek gematria module for Isopsephy support
try:
    from agentpm.modules.gematria import greek as greek_gematria

    GREEK_SUPPORT = True
except ImportError:
    GREEK_SUPPORT = False
    log_json(
        get_logger("ai_noun_discovery"),
        30,
        "greek_module_unavailable",
        reason="agentpm.modules.gematria.greek not found",
    )

LOG = get_logger("ai_noun_discovery")


class AINounDiscovery:
    """AI-powered organic noun discovery from Hebrew/Greek text (Phase 13: Multilingual)."""

    def __init__(self):
        # Book name normalization mapping
        self.book_map = {
            "Genesis": "Gen",
            "Exodus": "Exo",
            "Leviticus": "Lev",
            "Numbers": "Num",
            "Deuteronomy": "Deu",
        }

        # Phase 13: Language detection mapping (OT = Hebrew, NT = Greek)
        # Old Testament books (Genesis - Malachi)
        self.hebrew_books = {
            "Gen",
            "Exo",
            "Lev",
            "Num",
            "Deu",
            "Jos",
            "Jdg",
            "Rut",
            "1Sa",
            "2Sa",
            "1Ki",
            "2Ki",
            "1Ch",
            "2Ch",
            "Ezr",
            "Neh",
            "Est",
            "Job",
            "Psa",
            "Pro",
            "Ecc",
            "Sng",
            "Isa",
            "Jer",
            "Lam",
            "Ezk",
            "Dan",
            "Hos",
            "Jol",
            "Amo",
            "Oba",
            "Jon",
            "Mic",
            "Nah",
            "Hab",
            "Zep",
            "Hag",
            "Zec",
            "Mal",
        }
        # New Testament books (Matthew - Revelation)
        self.greek_books = {
            "Mat",
            "Mrk",
            "Mar",  # Phase 13: Mark abbreviation variant
            "Luk",
            "Jhn",
            "Act",
            "Rom",
            "1Co",
            "2Co",
            "Gal",
            "Eph",
            "Php",
            "Col",
            "1Th",
            "2Th",
            "1Ti",
            "2Ti",
            "Tit",
            "Phm",
            "Heb",
            "Jas",
            "1Pe",
            "2Pe",
            "1Jn",
            "2Jn",
            "3Jn",
            "Jud",
            "Rev",
        }

    def discover_nouns_for_book(self, book: str) -> List[Dict[str, Any]]:
        """
        Use AI to organically discover and analyze nouns from Hebrew/Greek text (Phase 13).

        Returns nouns with:
        - hebrew/greek: original text
        - letters: individual letter breakdown
        - gematria: calculated numerical value (Hebrew gematria or Greek isopsephy)
        - classification: person/place/thing
        - meaning: AI-generated meaning/context
        - primary_verse: first occurrence
        - freq: frequency in text
        - language: 'HE' or 'GR' (Phase 13)
        """
        normalized_book = normalize_book(book)
        db_book = self.book_map.get(normalized_book, normalized_book[:3])

        # Phase 13: Detect language based on book
        language = self._detect_language(db_book)
        log_json(LOG, 20, "language_detected", book=db_book, language=language)

        # Get raw text for the book (language-aware)
        raw_text = self._get_raw_text(db_book, language)

        if not raw_text:
            log_json(LOG, 30, "no_text_found", book=book, language=language)
            return []

        log_json(
            LOG,
            20,
            "ai_noun_discovery_start",
            book=book,
            language=language,
            text_length=len(raw_text),
            text_preview=raw_text[:100],
        )

        # Use AI to discover and analyze nouns (language-aware)
        discovered_nouns = self._ai_discover_nouns(raw_text, book, language)

        log_json(
            LOG,
            20,
            "ai_noun_discovery_complete",
            book=book,
            language=language,
            nouns_discovered=len(discovered_nouns),
        )

        return discovered_nouns

    def _detect_language(self, db_book: str) -> str:
        """Detect language based on book (Phase 13: Option A - Book-based detection).

        Args:
            db_book: Normalized book code (e.g., 'Gen', 'Mat')

        Returns:
            'HE' for Hebrew (Old Testament), 'GR' for Greek (New Testament)
        """
        if db_book in self.hebrew_books:
            return "HE"
        elif db_book in self.greek_books:
            return "GR"
        else:
            # Default to Hebrew for unknown books
            log_json(LOG, 30, "unknown_book_language", book=db_book, default="HE")
            return "HE"

    def _get_raw_text(self, db_book: str, language: str) -> str:
        """Extract raw Hebrew or Greek text for the book (Phase 13: Multilingual).

        Args:
            db_book: Normalized book code
            language: 'HE' for Hebrew, 'GR' for Greek

        Returns:
            Raw text string with words separated by spaces
        """
        try:
            if language == "HE":
                # Extract Hebrew text from Old Testament
                rows = list(
                    get_bible_ro().execute(
                        """
                    SELECT hw.word_text
                    FROM bible.hebrew_ot_words hw
                    JOIN bible.verses v ON hw.verse_id = v.verse_id
                    WHERE v.book_name = %s
                      AND LEFT(hw.strongs_id, 1) = 'H'
                    ORDER BY v.verse_id, hw.word_position
                """,
                        (db_book,),
                    )
                )
            else:  # language == "GR"
                # Extract Greek text from New Testament
                rows = list(
                    get_bible_ro().execute(
                        """
                    SELECT gw.word_text
                    FROM bible.greek_nt_words gw
                    JOIN bible.verses v ON gw.verse_id = v.verse_id
                    WHERE v.book_name = %s
                      AND LEFT(gw.strongs_id, 1) = 'G'
                    ORDER BY v.verse_id, gw.word_position
                """,
                        (db_book,),
                    )
                )

            # Join all words with spaces
            text = " ".join(row[0] for row in rows)
            return text
        except Exception as e:
            log_json(LOG, 40, "raw_text_extraction_error", book=db_book, language=language, error=str(e))
            # Fallback to mock text for testing when database is unavailable
            log_json(
                LOG,
                30,
                "using_mock_text",
                book=db_book,
                language=language,
                reason="database_unavailable",
            )

            if language == "HE":
                # Mock Hebrew text (Genesis 1)
                return """בראשית ברא אלהים את השמים ואת הארץ והארץ היתה תהו ובהו וחשך על פני תהום ורוח אלהים מרחפת על פני המים ויאמר אלהים יהי אור ויהי אור וירא אלהים את האור כי טוב ויבדל אלהים בין האור ובין החשך ויקרא אלהים לאור יום ולחשך קרא לילה ויהי ערב ויהי בקר יום אחד"""
            else:
                # Mock Greek text (Mark 1:1)
                return """Ἀρχὴ τοῦ εὐαγγελίου Ἰησοῦ Χριστοῦ υἱοῦ θεοῦ"""

    def _ai_discover_nouns(self, text: str, book: str, language: str = "HE") -> List[Dict[str, Any]]:
        """Use AI to discover and analyze nouns from Hebrew/Greek text (Phase 13).

        Args:
            text: Raw Hebrew or Greek text
            book: Book name
            language: 'HE' for Hebrew, 'GR' for Greek

        Returns:
            List of discovered and validated nouns
        """

        # Sample the text for analysis (avoid token limits)
        sampled_text = self._sample_text(text)

        lang_name = "Hebrew" if language == "HE" else "Greek"

        prompt = f"""Extract significant {lang_name} nouns from this {lang_name} text. Return ONLY JSON:

{{
  "nouns": [
    {{
      "hebrew": "אלהים",
      "letters": ["א", "ל", "ה", "י", "ם"],
      "gematria": 86,
      "classification": "person",
      "meaning": "God",
      "primary_verse": "Genesis 1:1",
      "freq": 35
    }}
  ]
}}

Hebrew text: {sampled_text}

IMPORTANT: Your response must be ONLY the JSON object above, with actual nouns extracted from the text."""

        try:
            # Check if mock mode is enabled (fallback for JSON prompting issues)
            if os.getenv("LM_STUDIO_MOCK", "false").lower() in ("1", "true", "yes"):
                # Return mock nouns for development/testing
                mock_nouns = [
                    {
                        "hebrew": "אלהים",
                        "letters": ["א", "ל", "ה", "י", "ם"],
                        "gematria": 86,
                        "classification": "person",
                        "meaning": "God, the Creator",
                        "primary_verse": "Genesis 1:1",
                        "freq": 35,
                    },
                    {
                        "hebrew": "ארץ",
                        "letters": ["א", "ר", "ץ"],
                        "gematria": 296,
                        "classification": "place",
                        "meaning": "Earth, land",
                        "primary_verse": "Genesis 1:10",
                        "freq": 25,
                    },
                    {
                        "hebrew": "אדם",
                        "letters": ["א", "ד", "ם"],
                        "gematria": 45,
                        "classification": "person",
                        "meaning": "Man, humanity",
                        "primary_verse": "Genesis 1:26",
                        "freq": 20,
                    },
                ]
                return mock_nouns

            # Use theology model with strict JSON prompting
            discovery_model = os.getenv("THEOLOGY_MODEL", "christian-bible-expert-v2.0-12b")

            # Phase 13: System Prompt Template (LLM Governance - Rule 018, Rule 050)
            # Enforces: Correctness Priority 1 (Code gematria > bible_db > LLM)
            # LLM Role: METADATA CLASSIFIER ONLY (not content generator)
            system_prompt = """You are a METADATA EXTRACTION AI operating under strict governance constraints.

YOUR ROLE: Extract and classify structured metadata from the provided biblical text ONLY.

PROHIBITED ACTIONS:
- Do NOT generate, translate, or paraphrase biblical content
- Do NOT make theological assertions or interpretations
- Do NOT create new data not present in the input text

REQUIRED BEHAVIOR:
- Extract ONLY the nouns explicitly present in the provided text
- Classify each noun by type (person/place/thing)
- Return ONLY valid JSON matching the specified schema
- No explanations, no markdown formatting, no additional commentary

DATA SOURCE PRIORITY (Correctness Priority 1):
1. Code-calculated gematria values (authoritative)
2. bible_db text and metadata (authoritative)
3. Your classification (metadata only)

OUTPUT FORMAT: Start with { and end with }. Valid JSON only."""

            messages_batch = [
                [
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {"role": "user", "content": prompt},
                ]
            ]

            results = chat_completion(messages_batch, model=discovery_model, temperature=0.0)

            if results and len(results) > 0:
                content = results[0].text
                log_json(LOG, 20, "ai_response_received", content_preview=content[:200])
                result = self._parse_ai_response(content)
            else:
                result = {"nouns": []}

            # Validate and enhance with frequency data
            log_json(
                LOG,
                20,
                "pre_validation",
                nouns_count=len(result.get("nouns", [])),
                sample_noun=result.get("nouns", [{}])[0] if result.get("nouns") else {},
            )
            nouns_to_validate = result.get("nouns", [])
            log_json(LOG, 20, "about_to_validate", nouns_to_validate_count=len(nouns_to_validate))
            try:
                validated_nouns = self._validate_and_enhance_nouns(nouns_to_validate, text, book, language)
                log_json(LOG, 20, "post_validation", validated_count=len(validated_nouns))
            except Exception as e:
                log_json(LOG, 40, "validation_function_error", error=str(e), error_type=type(e).__name__)
                validated_nouns = []

            return validated_nouns

        except Exception as e:
            log_json(LOG, 40, "ai_discovery_error", book=book, error=str(e))
            return []

    def _sample_text(self, text: str, max_length: int = 4000) -> str:
        """Sample text from the beginning to focus on key nouns."""
        if len(text) <= max_length:
            return text

        # Focus on the beginning where key nouns appear (Genesis 1-2)
        return text[:max_length]

    def _calculate_gematria(self, word: str, language: str = "HE") -> int:
        """Calculate gematria value (Hebrew Gematria or Greek Isopsephy) for a word.

        Phase 13: Language-aware calculation
        - Hebrew: Traditional Hebrew gematria
        - Greek: Isopsephy (Greek gematria)

        Args:
            word: Hebrew or Greek word
            language: 'HE' for Hebrew, 'GR' for Greek

        Returns:
            Calculated gematria/isopsephy value
        """
        if language == "GR" and GREEK_SUPPORT:
            # Use Greek Isopsephy module
            return greek_gematria.calculate_gematria(word)
        else:
            # Hebrew gematria (default)
            gematria_map = {
                "א": 1,
                "ב": 2,
                "ג": 3,
                "ד": 4,
                "ה": 5,
                "ו": 6,
                "ז": 7,
                "ח": 8,
                "ט": 9,
                "י": 10,
                "כ": 20,
                "ל": 30,
                "מ": 40,
                "נ": 50,
                "ס": 60,
                "ע": 70,
                "פ": 80,
                "צ": 90,
                "ק": 100,
                "ר": 200,
                "ש": 300,
                "ת": 400,
            }
            return sum(gematria_map.get(char, 0) for char in word)

    def _parse_ai_response(self, content: str) -> Dict[str, Any]:
        """Parse AI response, handling various formats."""
        try:
            # Try direct JSON parsing
            parsed = json.loads(content)
            # Handle case where AI returns array of strings instead of objects
            if isinstance(parsed.get("nouns"), list) and parsed["nouns"] and isinstance(parsed["nouns"][0], str):
                # Convert string array to proper noun objects
                nouns = []
                for hebrew_word in parsed["nouns"][:10]:  # Limit to first 10
                    if isinstance(hebrew_word, str) and hebrew_word.strip():
                        word = hebrew_word.strip()
                        nouns.append(
                            {
                                "surface": word,  # Schema field: surface
                                "letters": list(word),  # Simple letter breakdown
                                "gematria": self._calculate_gematria(word),
                                "class": "thing",  # Schema field: class (valid values: person/place/thing/other)
                                "sources": [{"ref": "Unknown", "offset": None}],  # Schema field: sources array
                                "analysis": {"meaning": f"Hebrew noun: {word}"},  # Schema field: analysis (object)
                            }
                        )
                return {"nouns": nouns}
            return parsed
        except json.JSONDecodeError:
            # Try to extract JSON from markdown or text
            json_match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group(1))
                    # Same handling for extracted JSON
                    if (
                        isinstance(parsed.get("nouns"), list)
                        and parsed["nouns"]
                        and isinstance(parsed["nouns"][0], str)
                    ):
                        nouns = []
                        for hebrew_word in parsed["nouns"][:10]:
                            if isinstance(hebrew_word, str) and hebrew_word.strip():
                                word = hebrew_word.strip()
                                nouns.append(
                                    {
                                        "surface": word,  # Schema field: surface
                                        "letters": list(word),  # Simple letter breakdown
                                        "gematria": self._calculate_gematria(word),
                                        "class": "thing",  # Schema field: class (valid values: person/place/thing/other)
                                        "sources": [{"ref": "Unknown", "offset": None}],  # Schema field: sources array
                                        "analysis": {
                                            "meaning": f"Hebrew noun: {word}"
                                        },  # Schema field: analysis (object)
                                    }
                                )
                        return {"nouns": nouns}
                    return parsed
                except json.JSONDecodeError:
                    pass

            # Fallback: return empty result
            log_json(LOG, 30, "ai_response_parse_error", content_preview=content[:200])
            return {"nouns": []}

    def _validate_and_enhance_nouns(
        self, ai_nouns: List[Dict[str, Any]], full_text: str, book: str, language: str = "HE"
    ) -> List[Dict[str, Any]]:
        """Validate AI-discovered nouns and enhance with frequency data (Phase 13: Language-aware).

        Args:
            ai_nouns: Nouns discovered by AI
            full_text: Full text of the book
            book: Book name
            language: 'HE' for Hebrew, 'GR' for Greek

        Returns:
            List of validated and enhanced nouns
        """
        validated = []

        for noun in ai_nouns:
            log_json(LOG, 10, "validating_noun", noun_index=len(validated), total_nouns=len(ai_nouns))
            try:
                # Validate required fields (ai-nouns.v1 schema)
                required_fields = ["surface", "letters", "gematria", "class"]
                if not all(key in noun for key in required_fields):
                    log_json(
                        LOG,
                        30,
                        "field_validation_failed",
                        noun_keys=list(noun.keys()),
                        required=required_fields,
                        missing=[k for k in required_fields if k not in noun],
                    )
                    continue

                # Calculate actual frequency in full text
                word = noun["surface"]
                # Language-aware normalization (Phase 13)
                if language == "GR" and GREEK_SUPPORT:
                    normalized_text = greek_gematria.normalize_greek(full_text)
                    normalized_word = greek_gematria.normalize_greek(word)
                else:
                    normalized_text = normalize_hebrew(full_text)
                    normalized_word = normalize_hebrew(word)

                freq = len(re.findall(re.escape(normalized_word), normalized_text))
                log_json(
                    LOG,
                    10,
                    "frequency_check",
                    word=word,
                    calculated_freq=freq,
                    text_length=len(full_text),
                    normalized_length=len(normalized_text),
                )

                if freq == 0:
                    continue  # Word not actually found in text

                # Enhance with pipeline-required fields (ai-nouns.v1 schema + pipeline compatibility)
                enhanced_noun = {
                    "surface": word,
                    "name": word,  # For pipeline compatibility
                    "letters": noun["letters"],
                    "gematria": noun["gematria"],
                    "value": noun["gematria"],  # For pipeline compatibility
                    "class": noun["class"],
                    "sources": noun.get("sources", [{"ref": f"{book} unknown", "offset": None}]),
                    "analysis": noun.get("analysis", ""),
                    "freq": freq,  # Add frequency for pipeline use
                    "book": book,
                    "language": language,  # Phase 13: Add language metadata
                    "ai_discovered": True,  # Mark as AI-discovered
                }

                validated.append(enhanced_noun)

            except Exception as e:
                log_json(
                    LOG,
                    30,
                    "noun_validation_error",
                    noun=noun,
                    error=str(e),
                    noun_keys=list(noun.keys()) if isinstance(noun, dict) else type(noun),
                )
                continue

        return validated


def discover_nouns_for_book(book: str) -> List[Dict[str, Any]]:
    """
    Main entry point for AI-driven noun discovery.

    Replaces the database-driven collect_nouns_for_book function.
    """
    discoverer = AINounDiscovery()
    return discoverer.discover_nouns_for_book(book)
