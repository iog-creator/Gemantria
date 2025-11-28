"""Greek text normalization and Isopsephy calculation utilities.

Implements Rule G-001 (Greek Normalization Contract):
NFKD → Strip polytonic accents/breathing marks → Strip punctuation/spaces → NFC

Reference: agentpm/modules/gematria/hebrew.py (ADR-002 for Hebrew)
"""

from __future__ import annotations

import re
import unicodedata

# 27-Letter Isopsephy Mapping (Classical Greek Gematria)
MAP: dict[str, int] = {
    # Units (1-9)
    "α": 1,
    "β": 2,
    "γ": 3,
    "δ": 4,
    "ε": 5,
    "ϝ": 6,  # Digamma (archaic, stigma)
    "ζ": 7,
    "η": 8,
    "θ": 9,
    # Tens (10-90)
    "ι": 10,
    "κ": 20,
    "λ": 30,
    "μ": 40,
    "ν": 50,
    "ξ": 60,
    "ο": 70,
    "π": 80,
    "ϙ": 90,  # Koppa (archaic)
    # Hundreds (100-900)
    "ρ": 100,
    "σ": 200,
    "ς": 200,  # Final sigma = Same as sigma
    "τ": 300,
    "υ": 400,
    "φ": 500,
    "χ": 600,
    "ψ": 700,
    "ω": 800,
    "ϡ": 900,  # Sampi (archaic)
}

# Regex to keep only Greek letters (U+0370-U+03FF, archaic letters)
_GREEK_LETTERS = re.compile(r"[^\u0370-\u03FF]+", re.UNICODE)


def normalize_greek(text: str) -> str:
    """Normalize Greek text to canonical form for gematria calculation.

    Normalization pipeline (Rule G-001):
    1. Convert to lowercase (Isopsephy uses lowercase letters)
    2. NFKD normalization (decompose characters)
    3. Strip combining diacritics (polytonic accents, breathing marks)
    4. Remove punctuation and spaces
    5. NFC normalization (recompose)

    Args:
        text: Raw Greek text (may contain diacritics, punctuation, etc.)

    Returns:
        Normalized Greek text with only letters remaining.
        Returns empty string for None, empty input, or text with no Greek letters.

    Examples:
        >>> normalize_greek("Ἰησοῦς")  # Jesus with polytonic marks
        'ιησους'
        >>> normalize_greek("Χριστός")  # Christ with accent
        'χριστος'
        >>> normalize_greek("")
        ''
        >>> normalize_greek("Hello 123")
        ''
        >>> normalize_greek("α hello β")
        'αβ'
    """
    # Handle None and empty input
    if not text:
        return ""

    # Step 1: Convert to lowercase (Isopsephy uses lowercase)
    text = text.lower()

    # Step 2: NFKD normalization (decompose)
    nk = unicodedata.normalize("NFKD", text)

    # Step 3: Strip combining marks (diacritics, accents, breathing marks)
    no_marks = "".join(ch for ch in nk if not unicodedata.combining(ch))

    # Step 4: Remove all non-Greek characters (keep only Greek letters U+0370-U+03FF)
    no_punct = _GREEK_LETTERS.sub("", no_marks)

    # Step 5: NFC normalization (recompose)
    return unicodedata.normalize("NFC", no_punct)


def letters_from_text(text: str) -> list[str]:
    """Extract normalized Greek letters from the input text.

    First normalizes the text, then returns a list of individual letter characters
    suitable for gematria calculation.

    Args:
        text: Raw Greek text (may contain diacritics, punctuation, etc.)

    Returns:
        List of normalized Greek letter characters (one-character strings).
        Returns empty list for None, empty input, or text with no Greek letters.

    Examples:
        >>> letters_from_text("Ἰησοῦς")
        ['Ι', 'η', 'σ', 'ο', 'υ', 'ς']
        >>> letters_from_text("Χριστός")
        ['Χ', 'ρ', 'ι', 'σ', 'τ', 'ο', 'ς']
        >>> letters_from_text("")
        []
        >>> letters_from_text("Hello 123")
        []
    """
    normalized = normalize_greek(text)
    return [ch for ch in normalized if ch and len(ch) == 1]


def calculate_gematria(word: str) -> int:
    """Calculate the Isopsephy value of a Greek word.

    Args:
        word: Greek text (will be normalized per Rule G-001)

    Returns:
        Gematria value using 27-letter Isopsephy system.
        Returns 0 for empty input or unknown characters.

    Examples:
        >>> calculate_gematria("Ιησους")  # Jesus = 10+8+200+70+400+200 = 888
        888
        >>> calculate_gematria("Χριστος")  # Christ = 600+100+10+200+300+70+200 = 1480
        1480
        >>> calculate_gematria("")
        0
    """
    normalized = normalize_greek(word)
    return sum(MAP.get(ch, 0) for ch in normalized)


def calc_string(word: str) -> str:
    """Generate a human-readable calculation string for Greek gematria.

    Args:
        word: Greek text (will be normalized per Rule G-001)

    Returns:
        String showing the calculation breakdown.

    Examples:
        >>> calc_string("Ιησους")
        'Ι(10) + η(8) + σ(200) + ο(70) + υ(400) + ς(200) = 888'
    """
    normalized = normalize_greek(word)
    parts = [f"{ch}({MAP.get(ch, 0)})" for ch in normalized]
    return " + ".join(parts) + f" = {calculate_gematria(word)}"
