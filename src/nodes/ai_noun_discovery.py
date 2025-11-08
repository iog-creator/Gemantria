"""
AI-Driven Noun Discovery Node

Replaces database-driven noun collection with organic AI discovery.
AI analyzes raw Hebrew text to discover nouns, break them down into letters,
calculate gematria values, and classify as person/place/thing.
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

LOG = get_logger("ai_noun_discovery")


class AINounDiscovery:
    """AI-powered organic noun discovery from Hebrew text."""

    def __init__(self):
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

        log_json(LOG, 20, "ai_noun_discovery_start", book=book, text_length=len(raw_text), text_preview=raw_text[:100])

        # Use AI to discover and analyze nouns
        discovered_nouns = self._ai_discover_nouns(raw_text, book)

        log_json(LOG, 20, "ai_noun_discovery_complete", book=book, nouns_discovered=len(discovered_nouns))

        return discovered_nouns

    def _get_raw_hebrew_text(self, db_book: str) -> str:
        """Extract raw Hebrew text for the book."""
        try:
            # BibleReadOnly.execute() handles connection internally
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

            # Join all words with spaces
            text = " ".join(row[0] for row in rows)
            return text
        except Exception as e:
            log_json(LOG, 40, "raw_text_extraction_error", book=db_book, error=str(e))
            # Fallback to mock Hebrew text for testing when database is unavailable
            log_json(LOG, 30, "using_mock_hebrew_text", book=db_book, reason="database_unavailable")
            # Use longer Genesis text to include more nouns for validation
            return """בראשית ברא אלהים את השמים ואת הארץ והארץ היתה תהו ובהו וחשך על פני תהום ורוח אלהים מרחפת על פני המים ויאמר אלהים יהי אור ויהי אור וירא אלהים את האור כי טוב ויבדל אלהים בין האור ובין החשך ויקרא אלהים לאור יום ולחשך קרא לילה ויהי ערב ויהי בקר יום אחד ויאמר אלהים יהי רקיע בתוך המים ויהי מבדיל בין מים למים ויעש אלהים את הרקיע ויבדל בין המים אשר מתחת לרקיע ובין המים אשר מעל לרקיע ויהי כן ויקרא אלהים לרקיע שמים ויהי ערב ויהי בקר יום שני ויאמר אלהים יקוו המים מתחת השמים אל מקום אחד ותראה היבשה ויהי כן ויקרא אלהים ליבשה ארץ ולמקוה המים קרא ימים וירא אלהים כי טוב ויאמר אלהים תדשא הארץ דשא עשב מזריע זרע עץ פרי עשה פרי למינו אשר זרעו בו על הארץ ויהי כן ותוצא הארץ דשא עשב מזריע זרע למינהו ועץ עשה פרי אשר זרעו בו למינו וירא אלהים כי טוב ויהי ערב ויהי בקר יום שלישי ויאמר אלהים יהי מארת ברקיע השמים להבדיל בין היום ובין הלילה והיו לאתת ולמועדים ולימים ושנים והיו למאורת ברקיע השמים להאיר על הארץ ויהי כן ויעש אלהים שני מאורת גדלים את המאור הגדל לממשלת היום ואת המאור הקטן לממשלת הלילה ואת הכוכבים ויתן אתם אלהים ברקיע השמים להאיר על הארץ ולמשל ביום ובלילה ולהבדיל בין האור ובין החשך וירא אלהים כי טוב ויהי ערב ויהי בקר יום רביעי ויאמר אלהים ישרצו המים שרץ נפש חיה ועוף יעופף על הארץ על פני רקיע השמים ויברא אלהים את התנינם הגדלים ואת כל נפש החיה הרמשת אשר שרצו המים למינהם ואת כל עוף כנף למינהו וירא אלהים כי טוב ויברך אתם אלהים לאמר פרו ורבו ומלאו את המים בימים והעוף ירב בארץ ויהי ערב ויהי בקר יום חמישי ויאמר אלהים תוצא הארץ נפש חיה למינה בהמה ורמש וחיתו ארץ למינה ויהי כן ויעש אלהים את חית הארץ למינה ואת הבהמה למינה ואת כל רמש האדמה למינהו וירא אלהים כי טוב ויאמר אלהים נעשה אדם בצלמנו כדמותנו וירדו בדגת הים ובעוף השמים ובבהמה ובכל הארץ ובכל הרמש הרמש על הארץ ויברא אלהים את האדם בצלמו בצלם אלהים ברא אתו זכר ונקבה ברא אתם ויברך אתם אלהים ויאמר להם אלהים פרו ורבו ומלאו את הארץ וכבשה ורדו בדגת הים ובעוף השמים ובכל חיה הרמשת על הארץ ויאמר אלהים הנה נתתי לכם את כל עשב זורע זרע אשר על פני כל הארץ ואת כל העץ אשר בו פרי עץ זורע זרע לכם יהיה לאכלה ולכל חית הארץ ולכל עוף השמים ולכל רמש על הארץ אשר בו נפש חיה את כל ירק עשב לאכלה ויהי כן וירא אלהים את כל אשר עשה והנה טוב מאד ויהי ערב ויהי בקר יום הששי"""

    def _ai_discover_nouns(self, hebrew_text: str, book: str) -> List[Dict[str, Any]]:
        """Use AI to discover and analyze nouns from Hebrew text."""

        # Sample the text for analysis (avoid token limits)
        sampled_text = self._sample_text(hebrew_text)

        prompt = f"""Extract significant Hebrew nouns from this Hebrew text. Return ONLY JSON:

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

            messages_batch = [
                [
                    {
                        "role": "system",
                        "content": "You are a data extraction AI. You must respond with ONLY valid JSON. No explanations, no markdown, no additional text. Start your response with { and end with }.",
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
                validated_nouns = self._validate_and_enhance_nouns(nouns_to_validate, hebrew_text, book)
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

    def _calculate_gematria(self, hebrew_word: str) -> int:
        """Calculate basic gematria value for a Hebrew word."""
        # Simple mapping - this could be enhanced with proper Hebrew gematria rules
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
        return sum(gematria_map.get(char, 0) for char in hebrew_word)

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
        self, ai_nouns: List[Dict[str, Any]], full_text: str, book: str
    ) -> List[Dict[str, Any]]:
        """Validate AI-discovered nouns and enhance with frequency data."""
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
                hebrew_word = noun["surface"]
                # Normalize the full text to remove vowels/cantillation for matching
                normalized_text = normalize_hebrew(full_text)
                freq = len(re.findall(re.escape(hebrew_word), normalized_text))
                log_json(
                    LOG,
                    10,
                    "frequency_check",
                    word=hebrew_word,
                    calculated_freq=freq,
                    text_length=len(full_text),
                    normalized_length=len(normalized_text),
                )

                if freq == 0:
                    continue  # Word not actually found in text

                # Enhance with pipeline-required fields (ai-nouns.v1 schema + pipeline compatibility)
                enhanced_noun = {
                    "surface": hebrew_word,
                    "name": hebrew_word,  # For pipeline compatibility
                    "letters": noun["letters"],
                    "gematria": noun["gematria"],
                    "value": noun["gematria"],  # For pipeline compatibility
                    "class": noun["class"],
                    "sources": noun.get("sources", [{"ref": f"{book} unknown", "offset": None}]),
                    "analysis": noun.get("analysis", ""),
                    "freq": freq,  # Add frequency for pipeline use
                    "book": book,
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
