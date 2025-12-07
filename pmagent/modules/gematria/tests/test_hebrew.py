from __future__ import annotations

from pmagent.modules.gematria import hebrew


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


def test_normalize_hebrew_removes_maqaf_and_sof_pasuq() -> None:
    """Test that normalization removes Hebrew maqaf and sof pasuq."""
    # Maqaf (U+05BE) is removed
    assert hebrew.normalize_hebrew("א־ב") == "אב"
    # Sof pasuq (U+05C3) is removed
    assert hebrew.normalize_hebrew("א׃ב") == "אב"  # noqa: RUF001


def test_normalize_hebrew_empty_string() -> None:
    """Test that empty string returns empty string."""
    assert hebrew.normalize_hebrew("") == ""


def test_normalize_hebrew_no_hebrew_letters() -> None:
    """Test that text with no Hebrew letters returns empty string."""
    assert hebrew.normalize_hebrew("Hello 123") == ""
    assert hebrew.normalize_hebrew(".,!?") == ""
    assert hebrew.normalize_hebrew("   ") == ""


def test_normalize_hebrew_mixed_scripts() -> None:
    """Test that normalization extracts only Hebrew letters from mixed scripts."""
    assert hebrew.normalize_hebrew("א hello ב") == "אב"
    assert hebrew.normalize_hebrew("א123ב456ג") == "אבג"
    assert hebrew.normalize_hebrew("א, ב, ג!") == "אבג"


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


def test_letters_from_text_empty_string() -> None:
    """Test that empty string returns empty list."""
    assert hebrew.letters_from_text("") == []


def test_letters_from_text_only_punctuation() -> None:
    """Test that text with only punctuation returns empty list."""
    assert hebrew.letters_from_text(".,!?") == []
    assert hebrew.letters_from_text("   ") == []


def test_letters_from_text_mixed_scripts() -> None:
    """Test that letters_from_text extracts only Hebrew letters from mixed scripts."""
    letters = hebrew.letters_from_text("א hello ב")
    assert letters == ["א", "ב"]

    letters = hebrew.letters_from_text("א123ב456ג")
    assert letters == ["א", "ב", "ג"]

    letters = hebrew.letters_from_text("א, ב, ג!")
    assert letters == ["א", "ב", "ג"]


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


def test_letters_to_value_empty_list() -> None:
    """Test that empty list returns 0."""
    assert hebrew.letters_to_value([]) == 0


def test_letters_to_value_unknown_characters() -> None:
    """Test that unknown characters in letters list are ignored."""
    # Unknown characters are ignored
    assert hebrew.letters_to_value(["א", "X", "ב"]) == 3


def test_letters_to_value_full_pipeline_mixed_text() -> None:
    """Test full pipeline: mixed text → normalize → extract → calculate."""
    # Mixed Hebrew and English text
    text = "א hello ב world ג"
    letters = hebrew.letters_from_text(text)
    value = hebrew.letters_to_value(letters)
    # א=1, ב=2, ג=3 = 6
    assert value == 6


def test_letters_to_value_full_pipeline_with_niqqud() -> None:
    """Test full pipeline with niqqud: text with diacritics → normalize → extract → calculate."""
    # Text with niqqud
    text = "הֶבֶל"
    letters = hebrew.letters_from_text(text)
    value = hebrew.letters_to_value(letters)
    # ה=5, ב=2, ל=30 = 37
    assert value == 37


def test_letters_to_value_full_pipeline_with_punctuation() -> None:
    """Test full pipeline with punctuation: text with punctuation → normalize → extract → calculate."""
    # Text with punctuation
    text = "א, ד, ם"
    letters = hebrew.letters_from_text(text)
    value = hebrew.letters_to_value(letters)
    # א=1, ד=4, ם=40 = 45
    assert value == 45
