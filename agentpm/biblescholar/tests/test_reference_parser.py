"""
Tests for reference_parser module.

Tests parsing of various Bible reference formats and book name normalization.
"""

from __future__ import annotations

import pytest

from agentpm.biblescholar.reference_parser import (
    ParsedReference,
    normalize_book_name,
    parse_reference,
)


class TestNormalizeBookName:
    """Tests for book name normalization."""

    def test_full_name_to_abbreviation(self) -> None:
        """Test full book names normalize to abbreviations."""
        assert normalize_book_name("Genesis") == "Gen"
        assert normalize_book_name("Exodus") == "Exo"
        assert normalize_book_name("Matthew") == "Mat"
        assert normalize_book_name("Revelation") == "Rev"

    def test_case_insensitive(self) -> None:
        """Test case-insensitive matching."""
        assert normalize_book_name("genesis") == "Gen"
        assert normalize_book_name("GENESIS") == "Gen"
        assert normalize_book_name("GeNeSiS") == "Gen"

    def test_abbreviation_variations(self) -> None:
        """Test common abbreviation variations."""
        assert normalize_book_name("Matt") == "Mat"
        assert normalize_book_name("Psalm") == "Psa"
        assert normalize_book_name("Psalms") == "Psa"

    def test_numbered_books(self) -> None:
        """Test numbered books (1 Corinthians, 2 Samuel, etc.)."""
        assert normalize_book_name("1 Corinthians") == "1Co"
        assert normalize_book_name("2 Samuel") == "2Sa"
        assert normalize_book_name("1John") == "1Jo"
        assert normalize_book_name("3 John") == "3Jo"

    def test_already_abbreviated(self) -> None:
        """Test that already abbreviated names return as-is."""
        assert normalize_book_name("Gen") == "Gen"
        assert normalize_book_name("Mat") == "Mat"

    def test_unrecognized_returns_as_is(self) -> None:
        """Test that unrecognized names return as-is."""
        assert normalize_book_name("UnknownBook") == "UnknownBook"
        assert normalize_book_name("XYZ") == "XYZ"


class TestParseReference:
    """Tests for parse_reference function."""

    def test_standard_format_single_verse(self) -> None:
        """Test standard format: Book Chapter:Verse."""
        result = parse_reference("John 3:16")
        assert result.book == "Joh"
        assert result.chapter == 3
        assert result.verse == 16
        assert result.end_verse is None
        assert result.translation == "KJV"

    def test_standard_format_verse_range(self) -> None:
        """Test standard format with verse range."""
        result = parse_reference("Gen 1:1-5")
        assert result.book == "Gen"
        assert result.chapter == 1
        assert result.verse == 1
        assert result.end_verse == 5

    def test_osis_format_single_verse(self) -> None:
        """Test OSIS format: Book.Chapter.Verse."""
        result = parse_reference("Gen.1.1")
        assert result.book == "Gen"
        assert result.chapter == 1
        assert result.verse == 1
        assert result.end_verse is None

    def test_osis_format_verse_range(self) -> None:
        """Test OSIS format with verse range."""
        result = parse_reference("Gen.1.1-5")
        assert result.book == "Gen"
        assert result.chapter == 1
        assert result.verse == 1
        assert result.end_verse == 5

    def test_chapter_only(self) -> None:
        """Test format without verse: Book Chapter."""
        result = parse_reference("Genesis 1")
        assert result.book == "Gen"
        assert result.chapter == 1
        assert result.verse is None
        assert result.end_verse is None

    def test_various_book_names(self) -> None:
        """Test parsing with various book name formats."""
        # Full names
        result = parse_reference("Genesis 1:1")
        assert result.book == "Gen"

        result = parse_reference("Matthew 5:3")
        assert result.book == "Mat"

        # Abbreviations
        result = parse_reference("Gen 1:1")
        assert result.book == "Gen"

        result = parse_reference("Matt 5:3")
        assert result.book == "Mat"

    def test_numbered_books(self) -> None:
        """Test parsing numbered books."""
        result = parse_reference("1 Corinthians 13:4")
        assert result.book == "1Co"
        assert result.chapter == 13
        assert result.verse == 4

        result = parse_reference("2 Samuel 5:1")
        assert result.book == "2Sa"
        assert result.chapter == 5
        assert result.verse == 1

    def test_whitespace_tolerance(self) -> None:
        """Test that whitespace is handled correctly."""
        result = parse_reference("  John  3:16  ")
        assert result.book == "Joh"
        assert result.chapter == 3
        assert result.verse == 16

        result = parse_reference("Gen. 1 . 1")
        assert result.book == "Gen"
        assert result.chapter == 1
        assert result.verse == 1

    def test_invalid_formats(self) -> None:
        """Test that invalid formats raise ValueError."""
        with pytest.raises(ValueError, match="Invalid reference format"):
            parse_reference("Invalid")

        with pytest.raises(ValueError, match="Invalid reference format"):
            parse_reference("John")

        with pytest.raises(ValueError, match="Invalid reference format"):
            parse_reference("John:")

        with pytest.raises(ValueError, match="Empty reference string"):
            parse_reference("")

        with pytest.raises(ValueError, match="Empty reference string"):
            parse_reference("   ")

    def test_parsed_reference_validation(self) -> None:
        """Test that ParsedReference validates values."""
        # Valid reference
        result = ParsedReference(book="Gen", chapter=1, verse=1)
        assert result.chapter == 1
        assert result.verse == 1

        # Invalid chapter
        with pytest.raises(ValueError, match="Chapter must be >= 1"):
            ParsedReference(book="Gen", chapter=0, verse=1)

        # Invalid verse
        with pytest.raises(ValueError, match="Verse must be >= 1"):
            ParsedReference(book="Gen", chapter=1, verse=0)

        # Invalid end_verse
        with pytest.raises(ValueError, match="End verse must be >= 1"):
            ParsedReference(book="Gen", chapter=1, verse=1, end_verse=0)

        # End verse before start verse
        with pytest.raises(ValueError, match=r"End verse.*must be >= start verse"):
            ParsedReference(book="Gen", chapter=1, verse=5, end_verse=3)

    def test_custom_translation(self) -> None:
        """Test that custom translation can be set."""
        result = parse_reference("John 3:16")
        assert result.translation == "KJV"  # Default

        # Note: parse_reference doesn't support custom translation yet,
        # but ParsedReference dataclass supports it
        result = ParsedReference(book="Joh", chapter=3, verse=16, translation="ESV")
        assert result.translation == "ESV"
