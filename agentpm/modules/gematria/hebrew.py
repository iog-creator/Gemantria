from __future__ import annotations

"""Hebrew text normalization and mapping utilities.

Reference implementation: src/core/ids.py (normalize_hebrew function).
Normalization follows ADR-002: NFKD → strip combining → strip maqaf/sof pasuq/punct → NFC.
"""

import re
import unicodedata
from typing import Iterable

# Unicode constants for Hebrew punctuation
MAQAF = "\u05be"  # Hebrew maqaf (hyphen)
SOF_PASUQ = "\u05c3"  # Hebrew sof pasuq (colon)

# Regex to remove non-Hebrew-word characters (keeps Hebrew letters)
_PUNCT = re.compile(r"[^\w\u0590-\u05FF]+", re.UNICODE)


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

    Returns:
        Normalized Hebrew text with only letters remaining.

    Examples:
        >>> normalize_hebrew("הֶבֶל")
        'הבל'
        >>> normalize_hebrew("בְּרֵאשִׁית")
        'בראשית'
    """
    # Step 1: NFKD normalization (decompose)
    nk = unicodedata.normalize("NFKD", text)

    # Step 2: Strip combining marks (diacritics, niqqud)
    no_marks = "".join(ch for ch in nk if not unicodedata.combining(ch))

    # Step 3: Remove maqaf and sof pasuq
    no_punct = no_marks.replace(MAQAF, "").replace(SOF_PASUQ, "")

    # Step 4: Remove all remaining punctuation and non-Hebrew characters
    no_punct = _PUNCT.sub("", no_punct)

    # Step 5: NFC normalization (recompose)
    return unicodedata.normalize("NFC", no_punct)


def letters_from_text(text: str) -> list[str]:
    """Extract normalized Hebrew letters from the input text.

    First normalizes the text, then returns a list of individual letter characters
    suitable for gematria calculation.

    Args:
        text: Raw Hebrew text (may contain diacritics, punctuation, etc.).

    Returns:
        List of normalized Hebrew letter characters (one-character strings).

    Examples:
        >>> letters_from_text("הֶבֶל")
        ['ה', 'ב', 'ל']
        >>> letters_from_text("אדם")
        ['א', 'ד', 'ם']
    """
    normalized = normalize_hebrew(text)
    return [ch for ch in normalized if ch]  # Filter out empty strings


def letters_to_value(letters: Iterable[str]) -> int:
    """Helper that delegates to core.gematria_value.

    Kept thin so math logic stays in core.

    Args:
        letters: Iterable of Hebrew letter characters.

    Returns:
        Gematria value of the letters.

    Examples:
        >>> letters_to_value(["א", "ד", "ם"])
        45
    """
    from . import core

    return core.gematria_value(list(letters))
