"""Hebrew text normalization and mapping utilities.

Reference implementation: src/core/ids.py (normalize_hebrew function).
Normalization follows ADR-002: NFKD → strip combining → strip maqaf/sof pasuq/punct → NFC.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Iterable

# Unicode constants for Hebrew punctuation
MAQAF = "\u05be"  # Hebrew maqaf (hyphen)
SOF_PASUQ = "\u05c3"  # Hebrew sof pasuq (colon)

# Regex to keep only Hebrew letters (U+0590 to U+05FF)
# This removes all non-Hebrew characters including Latin letters, digits, punctuation
_HEBREW_LETTERS = re.compile(r"[^\u0590-\u05FF]+", re.UNICODE)


def normalize_hebrew(text: str) -> str:
    """Normalize a raw Hebrew string into the canonical form used for numerics.

    Normalization pipeline (per ADR-002):
    1. NFKD normalization (decompose characters)
    2. Strip combining marks (diacritics, niqqud)
    3. Remove maqaf (U+05BE) and sof pasuq (U+05C3)
    4. Remove all punctuation and non-Hebrew characters
    5. NFC normalization (recompose)

    Args:
        text: Raw Hebrew text (may contain diacritics, punctuation, etc.).
              Handles None, empty strings, and mixed scripts gracefully.

    Returns:
        Normalized Hebrew text with only letters remaining.
        Returns empty string for None, empty input, or text with no Hebrew letters.

    Examples:
        >>> normalize_hebrew("הֶבֶל")
        'הבל'
        >>> normalize_hebrew("בְּרֵאשִׁית")
        'בראשית'
        >>> normalize_hebrew("")
        ''
        >>> normalize_hebrew("Hello 123")
        ''
        >>> normalize_hebrew("א hello ב")
        'אב'
    """
    # Handle None and empty input
    if not text:
        return ""

    # Step 1: NFKD normalization (decompose)
    nk = unicodedata.normalize("NFKD", text)

    # Step 2: Strip combining marks (diacritics, niqqud)
    no_marks = "".join(ch for ch in nk if not unicodedata.combining(ch))

    # Step 3: Remove maqaf and sof pasuq
    no_punct = no_marks.replace(MAQAF, "").replace(SOF_PASUQ, "")

    # Step 4: Remove all non-Hebrew characters (keep only Hebrew letters U+0590-U+05FF)
    no_punct = _HEBREW_LETTERS.sub("", no_punct)

    # Step 5: NFC normalization (recompose)
    return unicodedata.normalize("NFC", no_punct)


def letters_from_text(text: str) -> list[str]:
    """Extract normalized Hebrew letters from the input text.

    First normalizes the text, then returns a list of individual letter characters
    suitable for gematria calculation.

    Args:
        text: Raw Hebrew text (may contain diacritics, punctuation, etc.).
              Handles None, empty strings, and mixed scripts gracefully.

    Returns:
        List of normalized Hebrew letter characters (one-character strings).
        Returns empty list for None, empty input, or text with no Hebrew letters.

    Examples:
        >>> letters_from_text("הֶבֶל")
        ['ה', 'ב', 'ל']
        >>> letters_from_text("אדם")
        ['א', 'ד', 'ם']
        >>> letters_from_text("")
        []
        >>> letters_from_text("Hello 123")
        []
        >>> letters_from_text("א hello ב")
        ['א', 'ב']
    """
    normalized = normalize_hebrew(text)
    # Filter out empty strings and ensure each character is a single Hebrew letter
    return [ch for ch in normalized if ch and len(ch) == 1]


def letters_to_value(letters: Iterable[str]) -> int:
    """Helper that delegates to core.gematria_value.

    Kept thin so math logic stays in core.

    Args:
        letters: Iterable of Hebrew letter characters.
                 Handles None, empty iterables, and unknown characters gracefully.

    Returns:
        Gematria value of the letters (default system: mispar_hechrachi).
        Returns 0 for empty input or if all characters are unknown.

    Examples:
        >>> letters_to_value(["א", "ד", "ם"])
        45
        >>> letters_to_value([])
        0
        >>> letters_to_value(["X", "123"])
        0
    """
    from . import core

    # Convert to list to handle any iterable, but handle None gracefully
    if letters is None:
        return 0

    return core.gematria_value(list(letters))
