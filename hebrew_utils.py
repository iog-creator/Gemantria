"""
Hebrew utilities for Gematria calculations and text processing.

Provides core functions for Hebrew text processing, gematria calculations,
and validation test cases for the Gematria system.
"""

import unicodedata
from typing import Dict, List, Optional


def calculate_gematria(hebrew_text: str) -> int:
    """
    Calculate gematria value using Mispar Hechrachi (standard method).

    Args:
        hebrew_text: Hebrew text (consonants only, no nikud/vowels)

    Returns:
        Gematria value as integer

    Note:
        Finals (sofiyot) use same values as regular forms:
        ך׳ = 20 (same as כ), ם׳ = 40 (same as מ), ן׳ = 50 (same as נ)
        ף׳ = 80 (same as פ), ץ׳ = 90 (same as צ)
    """
    # Mispar Hechrachi mapping
    gematria_map = {
        'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9, 'י': 10,
        'כ': 20, 'ך': 20, 'ל': 30, 'מ': 40, 'ם': 40, 'נ': 50, 'ן': 50, 'ס': 60, 'ע': 70,
        'פ': 80, 'ף': 80, 'צ': 90, 'ץ': 90, 'ק': 100, 'ר': 200, 'ש': 300, 'ת': 400
    }

    # Strip any remaining nikud/vowels and normalize
    clean_text = strip_nikud(hebrew_text)

    # Calculate sum
    total = 0
    for char in clean_text:
        if char in gematria_map:
            total += gematria_map[char]
        # Skip unknown characters (punctuation, etc.)

    return total


def strip_nikud(hebrew_text: str) -> str:
    """
    Strip nikud (vowel marks) and normalize Hebrew text.

    Uses NFKD normalization to decompose characters, removes combining marks,
    then recomposes to NFC. Also removes maqaf (־) and other punctuation.

    Args:
        hebrew_text: Hebrew text with potential nikud/vowels

    Returns:
        Clean Hebrew text with consonants only
    """
    # NFKD normalization (decompose)
    normalized = unicodedata.normalize('NFKD', hebrew_text)

    # Remove combining marks (nikud/vowels) and other diacritics
    # Unicode categories: Mn (nonspacing mark), Mc (spacing combining mark)
    clean_chars = []
    for char in normalized:
        category = unicodedata.category(char)
        # Keep Hebrew letters, skip marks and punctuation
        if category.startswith('Lo') or (char in 'כךמםנןפףצץ'):  # Hebrew letters + finals
            clean_chars.append(char)
        # Skip marks (Mn, Mc) and punctuation (Po, Pc, etc.)

    # NFC normalization (recompose)
    result = unicodedata.normalize('NFC', ''.join(clean_chars))

    return result


def get_primes(n: int) -> List[int]:
    """
    Get prime factorization of a number.

    Args:
        n: Number to factorize

    Returns:
        List of prime factors in ascending order
    """
    if n <= 1:
        return []

    primes = []
    # Check for 2
    while n % 2 == 0:
        primes.append(2)
        n //= 2

    # Check for odd factors
    i = 3
    while i * i <= n:
        while n % i == 0:
            primes.append(i)
            n //= i
        i += 2

    # If n is a prime number greater than 2
    if n > 1:
        primes.append(n)

    return primes


# Validation test cases for TDD
VALIDATION_TEST_CASES = [
    {
        "hebrew": "א",
        "expected_value": 1,
        "description": "Aleph (first letter)"
    },
    {
        "hebrew": "אדם",
        "expected_value": 45,
        "description": "Adam (א(1) + ד(4) + מ(40) = 45)"
    },
    {
        "hebrew": "הבל",
        "expected_value": 37,
        "description": "Hevel/Abel (ה(5) + ב(2) + ל(30) = 37)"
    },
    {
        "hebrew": "משיח",
        "expected_value": 358,
        "description": "Messiah (מ(40) + ש(300) + י(10) + ח(8) = 358)"
    },
    {
        "hebrew": "אלהים",
        "expected_value": 86,
        "description": "Elohim (א(1) + ל(30) + ה(5) + י(10) + מ(40) = 86)"
    },
    {
        "hebrew": "תורה",
        "expected_value": 611,
        "description": "Torah (ת(400) + ו(6) + ר(200) + ה(5) = 611)"
    }
]


def validate_gematria_calculation(hebrew_text: str, expected_value: int) -> bool:
    """
    Validate a gematria calculation against expected value.

    Args:
        hebrew_text: Hebrew text to calculate
        expected_value: Expected gematria value

    Returns:
        True if calculation matches expected value
    """
    calculated = calculate_gematria(hebrew_text)
    return calculated == expected_value


def run_validation_tests() -> Dict[str, bool]:
    """
    Run all validation test cases.

    Returns:
        Dictionary mapping test descriptions to pass/fail status
    """
    results = {}
    for test_case in VALIDATION_TEST_CASES:
        passed = validate_gematria_calculation(
            test_case["hebrew"],
            test_case["expected_value"]
        )
        results[test_case["description"]] = passed

    return results


# Export all functions
__all__ = [
    'calculate_gematria',
    'strip_nikud',
    'get_primes',
    'validate_gematria_calculation',
    'run_validation_tests',
    'VALIDATION_TEST_CASES'
]
