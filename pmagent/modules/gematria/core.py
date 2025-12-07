"""
Core Gematria value logic.

Real implementations extracted from the Gemantria.v2 numerics pipeline.
See docs/SSOT/AGENTPM_GEMATRIA_MODULE_PLAN.md and
docs/SSOT/GEMATRIA_NUMERICS_INTAKE.md for migration details.

Reference implementations:
- src/core/hebrew_utils.py (MAP and calculate_gematria)
- scripts/gematria_verify.py (gematria function)
"""

from __future__ import annotations
from typing import Iterable

DEFAULT_SYSTEM_NAME = "mispar_hechrachi"

# Mispar Hechrachi: Hebrew letter-to-value mapping
# Finals mapped to regular values (ך=20, ם=40, ן=50, ף=80, ץ=90)  # noqa: RUF003
# Reference: src/core/hebrew_utils.py, scripts/gematria_verify.py
_MISPAR_HECHRACHI_MAP: dict[str, int] = {
    "א": 1,
    "ב": 2,
    "ג": 3,
    "ד": 4,
    "ה": 5,
    "ו": 6,  # noqa: RUF001
    "ז": 7,
    "ח": 8,
    "ט": 9,  # noqa: RUF001
    "י": 10,  # noqa: RUF001
    "כ": 20,
    "ך": 20,  # final kaf
    "ל": 30,
    "מ": 40,
    "ם": 40,  # final mem
    "נ": 50,
    "ן": 50,  # final nun  # noqa: RUF001
    "ס": 60,  # noqa: RUF001
    "ע": 70,
    "פ": 80,
    "ף": 80,  # final pe
    "צ": 90,
    "ץ": 90,  # final tsadi
    "ק": 100,
    "ר": 200,
    "ש": 300,
    "ת": 400,
}

# Mispar Gadol: Hebrew letter-to-value mapping
# Finals have different values (ך=500, ם=600, ן=700, ף=800, ץ=900)  # noqa: RUF003
# Reference: ADR-002 mentions Mispar Gadol as alternative system
_MISPAR_GADOL_MAP: dict[str, int] = {
    "א": 1,
    "ב": 2,
    "ג": 3,
    "ד": 4,
    "ה": 5,
    "ו": 6,  # noqa: RUF001
    "ז": 7,
    "ח": 8,
    "ט": 9,  # noqa: RUF001
    "י": 10,  # noqa: RUF001
    "כ": 20,
    "ך": 500,  # final kaf (different from Hechrachi)
    "ל": 30,
    "מ": 40,
    "ם": 600,  # final mem (different from Hechrachi)
    "נ": 50,
    "ן": 700,  # final nun (different from Hechrachi)  # noqa: RUF001
    "ס": 60,  # noqa: RUF001
    "ע": 70,
    "פ": 80,
    "ף": 800,  # final pe (different from Hechrachi)
    "צ": 90,
    "ץ": 900,  # final tsadi (different from Hechrachi)
    "ק": 100,
    "ר": 200,
    "ש": 300,
    "ת": 400,
}

# System name to map lookup
_SYSTEM_MAPS: dict[str, dict[str, int]] = {
    "mispar_hechrachi": _MISPAR_HECHRACHI_MAP,
    "mispar_gadol": _MISPAR_GADOL_MAP,
}


def gematria_value(letters: Iterable[str], system: str = DEFAULT_SYSTEM_NAME) -> int:
    """Compute gematria value for a normalized sequence of Hebrew letters.

    Args:
        letters: Iterable of Hebrew letter characters (normalized, no diacritics).
                 Unknown characters are ignored (value 0).
                 Empty iterables return 0.
        system: Gematria system name. Supported: "mispar_hechrachi" (default),
                "mispar_gadol".

    Returns:
        Sum of letter values according to the specified system.
        Returns 0 for empty input or if all characters are unknown.

    Raises:
        ValueError: If system is not supported.

    Examples:
        >>> gematria_value(["א", "ד", "ם"])
        45
        >>> gematria_value(["ה", "ב", "ל"])
        37
        >>> gematria_value(["א", "ד", "ם"], system="mispar_gadol")
        605  # א=1, ד=4, ם=600
        >>> gematria_value([])
        0
        >>> gematria_value(["X", "123"])
        0
    """
    if system not in _SYSTEM_MAPS:
        supported = ", ".join(sorted(_SYSTEM_MAPS.keys()))
        raise ValueError(f"Unsupported gematria system: {system}. Supported: {supported}")

    letter_map = _SYSTEM_MAPS[system]

    # Handle empty input gracefully
    if not letters:
        return 0

    # Sum values, ignoring unknown characters (they return 0 from .get())
    total = 0
    for letter in letters:
        # Handle None or empty strings gracefully
        if not letter:
            continue
        # Only process single-character strings (Hebrew letters)
        if len(letter) == 1:
            total += letter_map.get(letter, 0)
        # Multi-character strings are ignored (not valid Hebrew letters)

    return total


def system_names() -> list[str]:
    """Return the supported Gematria systems in this module.

    Returns:
        List of supported system names, sorted alphabetically.
        Currently: ["mispar_gadol", "mispar_hechrachi"]

    Examples:
        >>> "mispar_hechrachi" in system_names()
        True
        >>> "mispar_gadol" in system_names()
        True
        >>> len(system_names())
        2
    """
    return sorted(_SYSTEM_MAPS.keys())
