from __future__ import annotations

"""
Core Gematria value logic.

Real implementations extracted from the Gemantria.v2 numerics pipeline.
See docs/SSOT/AGENTPM_GEMATRIA_MODULE_PLAN.md and
docs/SSOT/GEMATRIA_NUMERICS_INTAKE.md for migration details.

Reference implementations:
- src/core/hebrew_utils.py (MAP and calculate_gematria)
- scripts/gematria_verify.py (gematria function)
"""

from typing import Iterable

DEFAULT_SYSTEM_NAME = "mispar_hechrachi"

# Mispar Hechrachi: Hebrew letter-to-value mapping
# Finals mapped to regular values (ך=20, ם=40, ן=50, ף=80, ץ=90)
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
    "ן": 50,  # final nun
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


def gematria_value(letters: Iterable[str], system: str = DEFAULT_SYSTEM_NAME) -> int:
    """Compute gematria value for a normalized sequence of Hebrew letters.

    Args:
        letters: Iterable of Hebrew letter characters (normalized, no diacritics).
        system: Gematria system name (currently only "mispar_hechrachi" supported).

    Returns:
        Sum of letter values according to the specified system.

    Raises:
        ValueError: If system is not supported.

    Examples:
        >>> gematria_value(["א", "ד", "ם"])
        45
        >>> gematria_value(["ה", "ב", "ל"])
        37
    """
    if system != DEFAULT_SYSTEM_NAME:
        raise ValueError(f"Unsupported gematria system: {system}. Supported: {DEFAULT_SYSTEM_NAME}")

    return sum(_MISPAR_HECHRACHI_MAP.get(letter, 0) for letter in letters)


def system_names() -> list[str]:
    """Return the supported Gematria systems in this module.

    Returns:
        List of supported system names. Currently only "mispar_hechrachi".

    Examples:
        >>> "mispar_hechrachi" in system_names()
        True
    """
    return [DEFAULT_SYSTEM_NAME]
