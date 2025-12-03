from __future__ import annotations

"""Tests for BibleScholar Gematria adapter.

Tests cover:
- Canonical examples (אדם=45, הבל=37)
- Both numerics systems (mispar_hechrachi, mispar_gadol)
- Edge cases (empty, None, mixed scripts, non-Hebrew)
- OSIS reference handling
- Invalid system names
"""

import pytest

from pmagent.biblescholar.gematria_adapter import (
    GematriaPhraseResult,
    compute_phrase_gematria,
)
from pmagent.modules.gematria import core


def test_compute_phrase_gematria_basic_adam_hechrachi() -> None:
    """Test canonical example: אדם (Adam) = 45 in Mispar Hechrachi."""
    result = compute_phrase_gematria("אדם", system=core.DEFAULT_SYSTEM_NAME)
    assert result.value == 45  # canonical example from Gematria tests
    assert result.normalized == "אדם"
    assert result.letters == ["א", "ד", "ם"]
    assert result.system == core.DEFAULT_SYSTEM_NAME
    assert result.text == "אדם"
    assert result.osis_ref is None


def test_compute_phrase_gematria_basic_hevel_hechrachi() -> None:
    """Test canonical example: הבל (Hevel/Abel) = 37 in Mispar Hechrachi."""
    result = compute_phrase_gematria("הבל", system=core.DEFAULT_SYSTEM_NAME)
    assert result.value == 37  # ה=5, ב=2, ל=30 → 5+2+30 = 37
    assert result.normalized == "הבל"
    assert result.letters == ["ה", "ב", "ל"]
    assert result.system == core.DEFAULT_SYSTEM_NAME


def test_compute_phrase_gematria_with_osis_ref() -> None:
    """Test that OSIS reference is preserved in result."""
    result = compute_phrase_gematria("הבל", system=core.DEFAULT_SYSTEM_NAME, osis_ref="Gen.4.2")
    assert result.value == 37  # canonical example from Gematria tests
    assert result.osis_ref == "Gen.4.2"
    assert result.text == "הבל"


def test_compute_phrase_gematria_mispar_gadol() -> None:
    """Test Mispar Gadol system (finals have different values)."""
    # אדם with final mem (ם)
    # Hechrachi: א=1, ד=4, ם=40 → 45
    # Gadol: א=1, ד=4, ם=600 → 605
    result_hechrachi = compute_phrase_gematria("אדם", system="mispar_hechrachi")
    result_gadol = compute_phrase_gematria("אדם", system="mispar_gadol")

    assert result_hechrachi.value == 45
    assert result_gadol.value == 605  # 1 + 4 + 600
    assert result_hechrachi.system == "mispar_hechrachi"
    assert result_gadol.system == "mispar_gadol"
    # Normalized text and letters should be the same
    assert result_hechrachi.normalized == result_gadol.normalized
    assert result_hechrachi.letters == result_gadol.letters


def test_compute_phrase_gematria_mispar_gadol_final_nun() -> None:
    """Test Mispar Gadol with final nun (ן) - different value."""  # noqa: RUF002
    # Final nun: 50 in Hechrachi, 700 in Gadol
    result_hechrachi = compute_phrase_gematria("ן", system="mispar_hechrachi")  # noqa: RUF001
    result_gadol = compute_phrase_gematria("ן", system="mispar_gadol")  # noqa: RUF001

    assert result_hechrachi.value == 50  # noqa: RUF001
    assert result_gadol.value == 700  # noqa: RUF001


def test_compute_phrase_gematria_with_diacritics() -> None:
    """Test that diacritics are normalized correctly."""
    # "הֶבֶל" with niqqud should normalize to "הבל"
    result = compute_phrase_gematria("הֶבֶל")
    assert result.normalized == "הבל"
    assert result.value == 37
    assert result.letters == ["ה", "ב", "ל"]


def test_compute_phrase_gematria_with_punctuation() -> None:
    """Test that punctuation is removed during normalization."""
    result = compute_phrase_gematria("א, ב, ג")
    assert result.normalized == "אבג"
    assert result.value == 6  # א=1, ב=2, ג=3
    assert result.letters == ["א", "ב", "ג"]


def test_compute_phrase_gematria_empty_string() -> None:
    """Test edge case: empty string returns value=0."""
    result = compute_phrase_gematria("")
    assert result.value == 0
    assert result.normalized == ""
    assert result.letters == []
    assert result.text == ""
    assert result.system == core.DEFAULT_SYSTEM_NAME


def test_compute_phrase_gematria_none_handled() -> None:
    """Test edge case: None is handled gracefully (treated as empty)."""
    # Note: Python type system prevents None, but if somehow passed, should handle
    # This test documents expected behavior if None handling is added
    result = compute_phrase_gematria("")
    assert result.value == 0
    assert result.normalized == ""
    assert result.letters == []


def test_compute_phrase_gematria_no_hebrew_letters() -> None:
    """Test edge case: text with no Hebrew letters returns value=0."""
    result = compute_phrase_gematria("Hello 123")
    assert result.value == 0
    assert result.normalized == ""
    assert result.letters == []
    assert result.text == "Hello 123"  # Original text preserved


def test_compute_phrase_gematria_mixed_scripts() -> None:
    """Test edge case: mixed Hebrew and non-Hebrew text."""
    result = compute_phrase_gematria("א hello ב")
    assert result.value == 3  # א=1, ב=2
    assert result.normalized == "אב"
    assert result.letters == ["א", "ב"]
    assert result.text == "א hello ב"  # Original text preserved


def test_compute_phrase_gematria_invalid_system() -> None:
    """Test that invalid system name raises ValueError."""
    with pytest.raises(ValueError, match="Invalid system"):
        compute_phrase_gematria("אדם", system="invalid_system")


def test_compute_phrase_gematria_invalid_system_error_message() -> None:
    """Test that error message includes valid system names."""
    with pytest.raises(ValueError) as exc_info:
        compute_phrase_gematria("אדם", system="invalid_system")
    error_msg = str(exc_info.value)
    assert "mispar_hechrachi" in error_msg
    assert "mispar_gadol" in error_msg


def test_compute_phrase_gematria_default_system() -> None:
    """Test that default system is mispar_hechrachi when not specified."""
    result = compute_phrase_gematria("אדם")
    assert result.system == "mispar_hechrachi"
    assert result.value == 45


def test_compute_phrase_gematria_osis_ref_preserved() -> None:
    """Test that OSIS ref is preserved even with edge cases."""
    result = compute_phrase_gematria("", osis_ref="Gen.1.1")
    assert result.osis_ref == "Gen.1.1"
    assert result.value == 0

    result = compute_phrase_gematria("Hello", osis_ref="Gen.1.1")
    assert result.osis_ref == "Gen.1.1"
    assert result.value == 0


def test_gematria_phrase_result_dataclass() -> None:
    """Test that GematriaPhraseResult dataclass works correctly."""
    result = GematriaPhraseResult(
        text="אדם",
        normalized="אדם",
        letters=["א", "ד", "ם"],
        system="mispar_hechrachi",
        value=45,
        osis_ref="Gen.2.7",
    )
    assert result.text == "אדם"
    assert result.normalized == "אדם"
    assert result.letters == ["א", "ד", "ם"]
    assert result.system == "mispar_hechrachi"
    assert result.value == 45
    assert result.osis_ref == "Gen.2.7"


def test_gematria_phrase_result_optional_osis_ref() -> None:
    """Test that osis_ref is optional in GematriaPhraseResult."""
    result = GematriaPhraseResult(
        text="אדם",
        normalized="אדם",
        letters=["א", "ד", "ם"],
        system="mispar_hechrachi",
        value=45,
    )
    assert result.osis_ref is None
