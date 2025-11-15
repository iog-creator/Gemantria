from __future__ import annotations

from agentpm.modules.gematria import hebrew


def test_normalize_hebrew_strips_niqqud() -> None:
    """Test that normalization removes diacritics (niqqud).

    Reference: tests/unit/test_hebrew_utils.py
    """
    # "הֶבֶל" with niqqud should normalize to "הבל" without
    assert hebrew.normalize_hebrew("הֶבֶל") == "הבל"


def test_normalize_hebrew_preserves_letters() -> None:
    """Test that normalization preserves Hebrew letters."""
    assert hebrew.normalize_hebrew("אדם") == "אדם"
    assert hebrew.normalize_hebrew("בראשית") == "בראשית"


def test_normalize_hebrew_removes_punctuation() -> None:
    """Test that normalization removes punctuation and spaces."""
    assert hebrew.normalize_hebrew("א, ב, ג") == "אבג"
    assert hebrew.normalize_hebrew("א ב ג") == "אבג"
    assert hebrew.normalize_hebrew("א-ב-ג") == "אבג"


def test_letters_from_text_extracts_normalized_letters() -> None:
    """Test that letters_from_text extracts individual letters after normalization."""
    # With niqqud
    letters = hebrew.letters_from_text("הֶבֶל")
    assert letters == ["ה", "ב", "ל"]

    # Without niqqud
    letters = hebrew.letters_from_text("הבל")
    assert letters == ["ה", "ב", "ל"]

    # With punctuation
    letters = hebrew.letters_from_text("א, ד, ם")
    assert letters == ["א", "ד", "ם"]


def test_letters_to_value_integration() -> None:
    """Test integration: normalize → extract letters → calculate value.

    Reference: tests/unit/test_hebrew_utils.py
    """
    # "אדם" = 45
    letters = hebrew.letters_from_text("אדם")
    value = hebrew.letters_to_value(letters)
    assert value == 45

    # "הֶבֶל" normalizes to "הבל" = 37
    letters = hebrew.letters_from_text("הֶבֶל")
    value = hebrew.letters_to_value(letters)
    assert value == 37


def test_letters_from_text_empty_string() -> None:
    """Test that empty string returns empty list."""
    assert hebrew.letters_from_text("") == []


def test_letters_from_text_only_punctuation() -> None:
    """Test that text with only punctuation returns empty list."""
    assert hebrew.letters_from_text(".,!?") == []
    assert hebrew.letters_from_text("   ") == []
