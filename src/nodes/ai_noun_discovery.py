"""
AI-Driven Noun Discovery Node

Replaces database-driven noun collection with organic AI discovery.
AI analyzes raw Hebrew text to discover nouns, break them down into letters,
calculate gematria values, and classify as person/place/thing.
"""

import json
import re
from typing import Any, Dict, List
from pathlib import Path

from src.core.books import normalize_book
from src.infra.db import get_bible_ro
from src.infra.env_loader import ensure_env_loaded
from src.infra.structured_logger import get_logger, log_json
from src.services.lmstudio_client import LMStudioClient

LOG = get_logger("ai_noun_discovery")


class AINounDiscovery:
    """AI-powered organic noun discovery from Hebrew text."""

    def __init__(self):
        self.client = LMStudioClient()
        self.book_map = {
            "Genesis": "Gen",
            "Exodus": "Exo",
            "Leviticus": "Lev",
            "Numbers": "Num",
            "Deuteronomy": "Deu",
        }

    def discover_nouns_for_book(self, book: str) -> List[Dict[str, Any]]:
        """
        Use AI to organically discover and analyze nouns from Hebrew text.

        Returns nouns with:
        - hebrew: original Hebrew text
        - letters: individual Hebrew letters breakdown
        - gematria: calculated numerical value
        - classification: person/place/thing
        - meaning: AI-generated meaning/context
        - primary_verse: first occurrence
        - freq: frequency in text
        """
        normalized_book = normalize_book(book)
        db_book = self.book_map.get(normalized_book, normalized_book[:3])

        # Get raw Hebrew text for the book
        raw_text = self._get_raw_hebrew_text(db_book)

        if not raw_text:
            log_json(LOG, 30, "no_hebrew_text", book=book)
            return []

        log_json(LOG, 20, "ai_noun_discovery_start", book=book, text_length=len(raw_text))

        # Use AI to discover and analyze nouns
        discovered_nouns = self._ai_discover_nouns(raw_text, book)

        log_json(LOG, 20, "ai_noun_discovery_complete",
                book=book, nouns_discovered=len(discovered_nouns))

        return discovered_nouns

    def _get_raw_hebrew_text(self, db_book: str) -> str:
        """Extract raw Hebrew text for the book."""
        try:
            with get_bible_ro() as conn, conn.cursor() as cur:
                cur.execute("""
                    SELECT string_agg(hw.word_text, ' ' ORDER BY v.verse_id, hw.position)
                    FROM bible.hebrew_ot_words hw
                    JOIN bible.verses v ON hw.verse_id = v.verse_id
                    WHERE v.book_name = %s
                      AND LEFT(hw.strongs_id, 1) = 'H'
                """, (db_book,))

                result = cur.fetchone()
                return result[0] if result and result[0] else ""
        except Exception as e:
            log_json(LOG, 40, "raw_text_extraction_error", book=db_book, error=str(e))
            return ""

    def _ai_discover_nouns(self, hebrew_text: str, book: str) -> List[Dict[str, Any]]:
        """Use AI to discover and analyze nouns from Hebrew text."""

        # Sample the text for analysis (avoid token limits)
        sampled_text = self._sample_text(hebrew_text)

        prompt = f"""
        Analyze this Hebrew text from {book} and discover significant nouns.

        For each noun you discover:
        1. Extract the original Hebrew word
        2. Break it down into individual Hebrew letters
        3. Calculate its gematria (numerical) value
        4. Classify it as: person, place, or thing
        5. Provide a brief theological/contextual meaning
        6. Note its first occurrence in the text

        Focus on nouns that appear to be significant for biblical theology.
        Return in JSON format with array of noun objects.

        Hebrew text sample:
        {sampled_text}

        Return format:
        {{
            "nouns": [
                {{
                    "hebrew": "אברהם",
                    "letters": ["א", "ב", "ר", "ה", "ם"],
                    "gematria": 248,
                    "classification": "person",
                    "meaning": "Father of many nations",
                    "primary_verse": "Genesis 11:27",
                    "freq": 5
                }}
            ]
        }}
        """

        try:
            response = self.client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # Low creativity for consistent analysis
                max_tokens=4000
            )

            content = response["choices"][0]["message"]["content"]
            result = self._parse_ai_response(content)

            # Validate and enhance with frequency data
            validated_nouns = self._validate_and_enhance_nouns(result.get("nouns", []), hebrew_text)

            return validated_nouns

        except Exception as e:
            log_json(LOG, 40, "ai_discovery_error", book=book, error=str(e))
            return []

    def _sample_text(self, text: str, max_length: int = 8000) -> str:
        """Sample text to avoid token limits while preserving context."""
        if len(text) <= max_length:
            return text

        # Take samples from beginning, middle, and end
        chunk_size = max_length // 3
        return (
            text[:chunk_size] +
            " ... " +
            text[len(text)//2:len(text)//2 + chunk_size] +
            " ... " +
            text[-chunk_size:]
        )

    def _parse_ai_response(self, content: str) -> Dict[str, Any]:
        """Parse AI response, handling various formats."""
        try:
            # Try direct JSON parsing
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown or text
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass

            # Fallback: return empty result
            log_json(LOG, 30, "ai_response_parse_error", content_preview=content[:200])
            return {"nouns": []}

    def _validate_and_enhance_nouns(self, ai_nouns: List[Dict[str, Any]], full_text: str) -> List[Dict[str, Any]]:
        """Validate AI-discovered nouns and enhance with frequency data."""
        validated = []

        for noun in ai_nouns:
            try:
                # Validate required fields
                if not all(key in noun for key in ["hebrew", "letters", "gematria", "classification"]):
                    continue

                # Calculate actual frequency in full text
                hebrew_word = noun["hebrew"]
                freq = len(re.findall(re.escape(hebrew_word), full_text))

                if freq == 0:
                    continue  # Word not actually found in text

                # Enhance with pipeline-required fields
                enhanced_noun = {
                    "hebrew": hebrew_word,
                    "name": hebrew_word,  # For pipeline compatibility
                    "letters": noun["letters"],
                    "gematria": noun["gematria"],
                    "value": noun["gematria"],  # For pipeline compatibility
                    "classification": noun["classification"],
                    "meaning": noun.get("meaning", ""),
                    "primary_verse": noun.get("primary_verse", f"{book} unknown"),
                    "freq": freq,
                    "book": book,
                    "ai_discovered": True,  # Mark as AI-discovered
                }

                validated.append(enhanced_noun)

            except Exception as e:
                log_json(LOG, 30, "noun_validation_error", noun=noun, error=str(e))
                continue

        return validated


def discover_nouns_for_book(book: str) -> List[Dict[str, Any]]:
    """
    Main entry point for AI-driven noun discovery.

    Replaces the database-driven collect_nouns_for_book function.
    """
    discoverer = AINounDiscovery()
    return discoverer.discover_nouns_for_book(book)
