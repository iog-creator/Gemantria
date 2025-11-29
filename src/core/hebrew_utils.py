# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

from __future__ import annotations

# Finals mapped to regular values (Mispar Hechrachi)
MAP: dict[str, int] = {
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
    "ך": 20,
    "ל": 30,
    "מ": 40,
    "ם": 40,
    "נ": 50,
    "ן": 50,  # noqa: RUF001
    "ס": 60,  # noqa: RUF001
    "ע": 70,
    "פ": 80,
    "ף": 80,
    "צ": 90,
    "ץ": 90,
    "ק": 100,
    "ר": 200,
    "ש": 300,
    "ת": 400,
}


def calculate_gematria(word: str) -> int:
    """
    Calculate gematria value for Hebrew word using Mispar Hechrachi.

    Per ADR-002: This function uses the surface form (Ketiv) for calculations.
    If a noun has variants, the Ketiv (written form) should be passed here,
    not the Qere (read form).

    Args:
        word: Hebrew text (should be Ketiv if variant exists)

    Returns:
        Sum of letter values according to Mispar Hechrachi
    """
    return sum(MAP.get(ch, 0) for ch in word)


def calc_string(word: str) -> str:
    parts = [f"{ch}({MAP.get(ch, 0)})" for ch in word]
    return " + ".join(parts) + f" = {calculate_gematria(word)}"


def get_ketiv_for_gematria(noun: dict) -> str:
    """
    Get the Ketiv (written form) from a noun for gematria calculation.

    Per ADR-002 Ketiv-primary policy: gematria calculations must use
    the Ketiv (written form), not the Qere (read form).

    Args:
        noun: Noun dictionary with 'surface' and optional 'variant_surface', 'is_ketiv'

    Returns:
        Ketiv text to use for gematria calculation
    """
    surface = noun.get("surface", "")
    is_ketiv = noun.get("is_ketiv", True)

    # If surface is Ketiv (default), use it
    if is_ketiv:
        return surface

    # If surface is Qere, variant_surface should be Ketiv
    variant_surface = noun.get("variant_surface", "")
    if variant_surface:
        return variant_surface

    # Fallback: use surface (assume it's Ketiv if no variant info)
    return surface
