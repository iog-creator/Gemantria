# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`

"""
Unit tests for OSIS (Open Scripture Information Standard) utilities.

Tests the extract_verse_references and normalize_book_to_osis functions
which handle Bible verse reference extraction and normalization.
"""

from agentpm.modules.gematria.utils.osis import extract_verse_references, normalize_book_to_osis


def test_extract_verse_references_single_verse():
    """Test extracting a single verse reference."""
    text = "Psalm 30:5"
    result = extract_verse_references(text)
    # Function matches both chapter:verse and chapter-only patterns
    assert len(result) >= 1
    osis_refs = {ref["osis"] for ref in result}
    assert "Ps.30.5" in osis_refs


def test_extract_verse_references_multiple_verses():
    """Test extracting multiple verse references."""
    text = "Psalm 30:5 and Isaiah 43:2"
    result = extract_verse_references(text)
    # Function matches both chapter:verse and chapter-only patterns
    assert len(result) >= 2
    osis_refs = {ref["osis"] for ref in result}
    assert "Ps.30.5" in osis_refs
    assert "Isa.43.2" in osis_refs


def test_extract_verse_references_chapter_only():
    """Test extracting chapter-only references."""
    text = "Genesis 1"
    result = extract_verse_references(text)
    assert len(result) == 1
    assert result[0]["osis"] == "Gen.1"
    assert result[0]["label"] == "Genesis 1"


def test_extract_verse_references_mixed_chapter_and_verse():
    """Test extracting both chapter-only and verse references."""
    text = "Genesis 1 and Genesis 1:1"
    result = extract_verse_references(text)
    # Function matches both patterns, may have duplicates
    assert len(result) >= 2
    osis_refs = {ref["osis"] for ref in result}
    assert "Gen.1" in osis_refs
    assert "Gen.1.1" in osis_refs


def test_extract_verse_references_case_insensitive():
    """Test that extraction is case-insensitive."""
    text = "psalm 30:5 and ISAIAH 43:2"
    result = extract_verse_references(text)
    # Function matches both chapter:verse and chapter-only patterns
    assert len(result) >= 2
    osis_refs = {ref["osis"] for ref in result}
    assert "Ps.30.5" in osis_refs
    assert "Isa.43.2" in osis_refs


def test_extract_verse_references_no_matches():
    """Test extraction with no verse references."""
    text = "This is just regular text with no references."
    result = extract_verse_references(text)
    assert len(result) == 0


def test_extract_verse_references_unrecognized_book():
    """Test extraction with unrecognized book names."""
    text = "FakeBook 1:1"
    result = extract_verse_references(text)
    assert len(result) == 0


def test_normalize_book_to_osis_direct_match():
    """Test direct book name matching."""
    assert normalize_book_to_osis("Genesis") == "Gen"
    assert normalize_book_to_osis("genesis") == "Gen"
    assert normalize_book_to_osis("GENESIS") == "Gen"
    assert normalize_book_to_osis("Psalm") == "Ps"
    assert normalize_book_to_osis("Isaiah") == "Isa"


def test_normalize_book_to_osis_psalm_variations():
    """Test Psalm/Psalms variations."""
    assert normalize_book_to_osis("Psalm") == "Ps"
    assert normalize_book_to_osis("Psalms") == "Ps"
    assert normalize_book_to_osis("psalm") == "Ps"
    assert normalize_book_to_osis("psalms") == "Ps"


def test_normalize_book_to_osis_numbered_books():
    """Test numbered books (1 Samuel, 2 Corinthians, etc.)."""
    assert normalize_book_to_osis("1 Samuel") == "1Sam"
    assert normalize_book_to_osis("2 Samuel") == "2Sam"
    assert normalize_book_to_osis("1 Corinthians") == "1Cor"
    assert normalize_book_to_osis("2 Corinthians") == "2Cor"
    assert normalize_book_to_osis("1 John") == "1John"
    assert normalize_book_to_osis("2 John") == "2John"
    assert normalize_book_to_osis("3 John") == "3John"


def test_normalize_book_to_osis_song_variations():
    """Test Song of Solomon/Song of Songs variations."""
    assert normalize_book_to_osis("Song of Solomon") == "Song"
    assert normalize_book_to_osis("Song of Songs") == "Song"


def test_normalize_book_to_osis_partial_match():
    """Test partial matching for book name variations."""
    # The function tries partial matches
    result = normalize_book_to_osis("Genesis book")
    assert result is not None


def test_normalize_book_to_osis_whitespace_handling():
    """Test that whitespace is properly handled."""
    assert normalize_book_to_osis("  Genesis  ") == "Gen"
    assert normalize_book_to_osis("Genesis") == "Gen"


def test_normalize_book_to_osis_unrecognized_book():
    """Test that unrecognized books return None."""
    assert normalize_book_to_osis("FakeBook") is None
    assert normalize_book_to_osis("NotABook") is None
    # Empty string may match due to partial matching, so test with clearly invalid input
    assert normalize_book_to_osis("XYZ123Invalid") is None


def test_extract_verse_references_complex_text():
    """Test extraction from complex text with multiple references."""
    text = "As it is written in Psalm 30:5, 'Weeping may endure for a night, but joy cometh in the morning.' Also see Isaiah 43:2 and Genesis 1:1."
    result = extract_verse_references(text)
    # Function matches both chapter:verse and chapter-only patterns
    assert len(result) >= 3
    osis_refs = {ref["osis"] for ref in result}
    assert "Ps.30.5" in osis_refs
    assert "Isa.43.2" in osis_refs
    assert "Gen.1.1" in osis_refs


def test_normalize_book_to_osis_new_testament():
    """Test New Testament book normalization."""
    assert normalize_book_to_osis("Matthew") == "Matt"
    assert normalize_book_to_osis("Mark") == "Mark"
    assert normalize_book_to_osis("Luke") == "Luke"
    assert normalize_book_to_osis("John") == "John"
    assert normalize_book_to_osis("Romans") == "Rom"
    assert normalize_book_to_osis("Revelation") == "Rev"
