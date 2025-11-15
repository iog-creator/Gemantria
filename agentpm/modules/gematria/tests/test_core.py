from __future__ import annotations

import pytest

from agentpm.modules.gematria import core


def test_system_names_includes_default() -> None:
    """Test that mispar_hechrachi is in the list of supported systems."""
    assert "mispar_hechrachi" in core.system_names()
    assert len(core.system_names()) == 1


def test_gematria_value_adam_45() -> None:
    """Test gematria calculation for 'אדם' (Adam) = 45.

    Reference: tests/unit/test_hebrew_utils.py
    Breakdown: א=1, ד=4, ם=40 → 1+4+40 = 45
    """
    letters = ["א", "ד", "ם"]
    assert core.gematria_value(letters) == 45


def test_gematria_value_hevel_37() -> None:
    """Test gematria calculation for 'הבל' (Hevel/Abel) = 37.

    Reference: tests/unit/test_hebrew_utils.py
    Breakdown: ה=5, ב=2, ל=30 → 5+2+30 = 37
    """
    letters = ["ה", "ב", "ל"]
    assert core.gematria_value(letters) == 37


def test_gematria_value_empty_list() -> None:
    """Test that empty list returns 0."""
    assert core.gematria_value([]) == 0


def test_gematria_value_unsupported_system() -> None:
    """Test that unsupported system raises ValueError."""
    with pytest.raises(ValueError, match="Unsupported gematria system"):
        core.gematria_value(["א"], system="mispar_gadol")


def test_gematria_value_unknown_character() -> None:
    """Test that unknown characters are ignored (value 0)."""
    # Mix of known Hebrew letters and unknown characters
    letters = ["א", "X", "ב", "123"]
    # Only א=1 and ב=2 should count
    assert core.gematria_value(letters) == 3


def test_gematria_value_final_forms() -> None:
    """Test that final forms have same values as regular forms."""
    # Regular mem (מ) = 40
    assert core.gematria_value(["מ"]) == 40
    # Final mem (ם) = 40 (same value)
    assert core.gematria_value(["ם"]) == 40
    # Regular kaf (כ) = 20
    assert core.gematria_value(["כ"]) == 20
    # Final kaf (ך) = 20 (same value)
    assert core.gematria_value(["ך"]) == 20
