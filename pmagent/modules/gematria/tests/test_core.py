from __future__ import annotations

import pytest

from pmagent.modules.gematria import core


def test_system_names_includes_both_systems() -> None:
    """Test that both mispar_hechrachi and mispar_gadol are in the list of supported systems."""
    systems = core.system_names()
    assert "mispar_hechrachi" in systems
    assert "mispar_gadol" in systems
    assert len(systems) == 2
    # Should be sorted alphabetically
    assert systems == ["mispar_gadol", "mispar_hechrachi"]


def test_gematria_value_adam_45() -> None:
    """Test gematria calculation for 'אדם' (Adam) = 45 in Mispar Hechrachi.

    Reference: tests/unit/test_hebrew_utils.py
    Breakdown: א=1, ד=4, ם=40 → 1+4+40 = 45
    """
    letters = ["א", "ד", "ם"]
    assert core.gematria_value(letters) == 45
    assert core.gematria_value(letters, system="mispar_hechrachi") == 45


def test_gematria_value_adam_mispar_gadol() -> None:
    """Test gematria calculation for 'אדם' (Adam) in Mispar Gadol.

    Breakdown: א=1, ד=4, ם=600 → 1+4+600 = 605
    """
    letters = ["א", "ד", "ם"]
    assert core.gematria_value(letters, system="mispar_gadol") == 605


def test_gematria_value_hevel_37() -> None:
    """Test gematria calculation for 'הבל' (Hevel/Abel) = 37.

    Reference: tests/unit/test_hebrew_utils.py
    Breakdown: ה=5, ב=2, ל=30 → 5+2+30 = 37
    Same in both systems (no final forms).
    """
    letters = ["ה", "ב", "ל"]
    assert core.gematria_value(letters) == 37
    assert core.gematria_value(letters, system="mispar_hechrachi") == 37
    assert core.gematria_value(letters, system="mispar_gadol") == 37


def test_gematria_value_empty_list() -> None:
    """Test that empty list returns 0."""
    assert core.gematria_value([]) == 0
    assert core.gematria_value([], system="mispar_hechrachi") == 0
    assert core.gematria_value([], system="mispar_gadol") == 0


def test_gematria_value_unsupported_system() -> None:
    """Test that unsupported system raises ValueError."""
    with pytest.raises(ValueError, match="Unsupported gematria system"):
        core.gematria_value(["א"], system="mispar_ketan")
    with pytest.raises(ValueError, match="Unsupported gematria system"):
        core.gematria_value(["א"], system="unknown_system")


def test_gematria_value_unknown_character() -> None:
    """Test that unknown characters are ignored (value 0)."""
    # Mix of known Hebrew letters and unknown characters
    letters = ["א", "X", "ב", "123"]
    # Only א=1 and ב=2 should count
    assert core.gematria_value(letters) == 3
    assert core.gematria_value(letters, system="mispar_gadol") == 3


def test_gematria_value_final_forms_hechrachi() -> None:
    """Test that final forms have same values as regular forms in Mispar Hechrachi."""
    # Regular mem (מ) = 40
    assert core.gematria_value(["מ"], system="mispar_hechrachi") == 40
    # Final mem (ם) = 40 (same value)
    assert core.gematria_value(["ם"], system="mispar_hechrachi") == 40
    # Regular kaf (כ) = 20
    assert core.gematria_value(["כ"], system="mispar_hechrachi") == 20
    # Final kaf (ך) = 20 (same value)
    assert core.gematria_value(["ך"], system="mispar_hechrachi") == 20


def test_gematria_value_final_forms_gadol() -> None:
    """Test that final forms have different values in Mispar Gadol."""
    # Regular mem (מ) = 40
    assert core.gematria_value(["מ"], system="mispar_gadol") == 40
    # Final mem (ם) = 600 (different from regular)
    assert core.gematria_value(["ם"], system="mispar_gadol") == 600
    # Regular kaf (כ) = 20
    assert core.gematria_value(["כ"], system="mispar_gadol") == 20
    # Final kaf (ך) = 500 (different from regular)
    assert core.gematria_value(["ך"], system="mispar_gadol") == 500


def test_gematria_value_final_forms_comparison() -> None:
    """Test that final forms differ between systems."""
    # Final mem: 40 in Hechrachi, 600 in Gadol
    assert core.gematria_value(["ם"], system="mispar_hechrachi") == 40
    assert core.gematria_value(["ם"], system="mispar_gadol") == 600

    # Final kaf: 20 in Hechrachi, 500 in Gadol
    assert core.gematria_value(["ך"], system="mispar_hechrachi") == 20
    assert core.gematria_value(["ך"], system="mispar_gadol") == 500

    # Final nun: 50 in Hechrachi, 700 in Gadol
    assert core.gematria_value(["ן"], system="mispar_hechrachi") == 50  # noqa: RUF001
    assert core.gematria_value(["ן"], system="mispar_gadol") == 700  # noqa: RUF001

    # Final pe: 80 in Hechrachi, 800 in Gadol
    assert core.gematria_value(["ף"], system="mispar_hechrachi") == 80
    assert core.gematria_value(["ף"], system="mispar_gadol") == 800

    # Final tsadi: 90 in Hechrachi, 900 in Gadol
    assert core.gematria_value(["ץ"], system="mispar_hechrachi") == 90
    assert core.gematria_value(["ץ"], system="mispar_gadol") == 900


def test_gematria_value_none_or_empty_strings() -> None:
    """Test that None or empty strings in the iterable are ignored."""
    # Empty strings are ignored
    assert core.gematria_value(["א", "", "ב"]) == 3
    # None would cause a type error, but empty strings are handled
    assert core.gematria_value(["א", "ב", ""]) == 3


def test_gematria_value_multi_character_strings() -> None:
    """Test that multi-character strings are ignored (not valid Hebrew letters)."""
    # Multi-character strings are ignored
    assert core.gematria_value(["א", "ב", "גד"]) == 3  # Only א=1, ב=2 count
    assert core.gematria_value(["אב", "ג"]) == 3  # Only ג=3 counts


def test_gematria_value_all_unknown_characters() -> None:
    """Test that all unknown characters return 0."""
    assert core.gematria_value(["X", "Y", "123", "!@#"]) == 0
    assert core.gematria_value(["X", "Y", "123"], system="mispar_gadol") == 0


def test_gematria_value_mixed_known_unknown() -> None:
    """Test mixed known and unknown characters."""
    # Mix of Hebrew letters, unknown chars, empty strings, multi-char
    letters = ["א", "X", "ב", "", "ג", "123", "דד"]
    # Only א=1, ב=2, ג=3 should count = 6 (multi-char "דד" is ignored)
    assert core.gematria_value(letters) == 6
    assert core.gematria_value(letters, system="mispar_gadol") == 6
