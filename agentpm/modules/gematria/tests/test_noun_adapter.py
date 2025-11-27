# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`

"""
Unit tests for noun_adapter module.

Tests the adapt_ai_noun function which converts AI-discovered nouns
to internal pipeline format.
"""

import uuid

from agentpm.modules.gematria.utils.noun_adapter import adapt_ai_noun


def test_adapt_ai_noun_complete_data():
    """Test adapt_ai_noun with all fields present."""
    ai_noun = {
        "noun_id": "test-noun-123",
        "hebrew": "אלהים",
        "letters": ["א", "ל", "ה", "י", "ם"],  # noqa: RUF001
        "gematria": 86,
        "classification": "deity",
        "meaning": "God, gods",
        "primary_verse": "Genesis 1:1",
        "freq": 2606,
        "book": "Genesis",
        "ai_discovered": True,
    }

    result = adapt_ai_noun(ai_noun)

    # Verify all fields are correctly mapped
    assert result["noun_id"] == "test-noun-123"
    assert result["surface"] == "אלהים"
    assert result["hebrew_text"] == "אלהים"
    assert result["letters"] == ["א", "ל", "ה", "י", "ם"]  # noqa: RUF001
    assert result["gematria_value"] == 86
    assert result["gematria"] == 86
    assert result["value"] == 86
    assert result["class"] == "deity"
    assert result["classification"] == "deity"
    assert result["meaning"] == "God, gods"
    assert result["primary_verse"] == "Genesis 1:1"
    assert result["freq"] == 2606
    assert result["book"] == "Genesis"
    assert result["ai_discovered"] is True
    assert result["sources"] == []


def test_adapt_ai_noun_minimal_data():
    """Test adapt_ai_noun with minimal required fields."""
    ai_noun = {
        "hebrew": "אדם",
        "gematria": 45,
    }

    result = adapt_ai_noun(ai_noun)

    # Verify defaults are applied
    assert result["surface"] == "אדם"
    assert result["hebrew_text"] == "אדם"
    assert result["gematria_value"] == 45
    assert result["gematria"] == 45
    assert result["value"] == 45
    assert result["class"] == "unknown"
    assert result["classification"] == "unknown"
    assert result["meaning"] == ""
    assert result["primary_verse"] == ""
    assert result["freq"] == 0
    assert result["book"] == ""
    assert result["ai_discovered"] is True
    assert result["sources"] == []
    assert result["letters"] == []


def test_adapt_ai_noun_generates_uuid_when_missing():
    """Test that adapt_ai_noun generates deterministic UUID when noun_id is missing."""
    ai_noun = {
        "hebrew": "אדם",
        "gematria": 45,
    }

    result = adapt_ai_noun(ai_noun)

    # Verify UUID was generated
    assert "noun_id" in result
    assert result["noun_id"] is not None
    assert len(result["noun_id"]) > 0

    # Verify UUID is deterministic (same input = same UUID)
    result2 = adapt_ai_noun(ai_noun)
    assert result["noun_id"] == result2["noun_id"]

    # Verify it's a valid UUID5
    expected_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, "noun:אדם"))
    assert result["noun_id"] == expected_uuid


def test_adapt_ai_noun_different_hebrew_different_uuid():
    """Test that different Hebrew text generates different UUIDs."""
    ai_noun1 = {"hebrew": "אדם", "gematria": 45}
    ai_noun2 = {"hebrew": "חוה", "gematria": 19}

    result1 = adapt_ai_noun(ai_noun1)
    result2 = adapt_ai_noun(ai_noun2)

    # Different Hebrew text should generate different UUIDs
    assert result1["noun_id"] != result2["noun_id"]


def test_adapt_ai_noun_preserves_existing_noun_id():
    """Test that existing noun_id is preserved and not regenerated."""
    custom_id = "custom-noun-id-456"
    ai_noun = {
        "noun_id": custom_id,
        "hebrew": "אדם",
        "gematria": 45,
    }

    result = adapt_ai_noun(ai_noun)

    # Should preserve the provided noun_id
    assert result["noun_id"] == custom_id


def test_adapt_ai_noun_empty_hebrew_generates_uuid():
    """Test UUID generation with empty Hebrew text."""
    ai_noun = {
        "hebrew": "",
        "gematria": 0,
    }

    result = adapt_ai_noun(ai_noun)

    # Should generate UUID even with empty Hebrew
    assert "noun_id" in result
    expected_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, "noun:"))
    assert result["noun_id"] == expected_uuid


def test_adapt_ai_noun_missing_hebrew_field():
    """Test adaptation when hebrew field is completely missing."""
    ai_noun = {
        "gematria": 100,
        "classification": "test",
    }

    result = adapt_ai_noun(ai_noun)

    # Should use empty string as default
    assert result["surface"] == ""
    assert result["hebrew_text"] == ""
    # Should still generate UUID
    expected_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, "noun:"))
    assert result["noun_id"] == expected_uuid


def test_adapt_ai_noun_compatibility_aliases():
    """Test that compatibility aliases (gematria, value, class) are set correctly."""
    ai_noun = {
        "hebrew": "test",
        "gematria": 123,
        "classification": "person",
    }

    result = adapt_ai_noun(ai_noun)

    # All three gematria fields should have the same value
    assert result["gematria_value"] == 123
    assert result["gematria"] == 123
    assert result["value"] == 123

    # Both classification fields should have the same value
    assert result["class"] == "person"
    assert result["classification"] == "person"


def test_adapt_ai_noun_ai_discovered_default():
    """Test that ai_discovered defaults to True when not provided."""
    ai_noun = {
        "hebrew": "test",
        "gematria": 50,
    }

    result = adapt_ai_noun(ai_noun)

    assert result["ai_discovered"] is True


def test_adapt_ai_noun_ai_discovered_false():
    """Test that ai_discovered can be set to False."""
    ai_noun = {
        "hebrew": "test",
        "gematria": 50,
        "ai_discovered": False,
    }

    result = adapt_ai_noun(ai_noun)

    assert result["ai_discovered"] is False


def test_adapt_ai_noun_sources_always_empty_list():
    """Test that sources is always initialized as empty list."""
    ai_noun = {
        "hebrew": "test",
        "gematria": 50,
    }

    result = adapt_ai_noun(ai_noun)

    # sources should always be an empty list (populated during enrichment)
    assert result["sources"] == []
    assert isinstance(result["sources"], list)


def test_adapt_ai_noun_letters_list():
    """Test that letters list is properly handled."""
    ai_noun = {
        "hebrew": "שלום",
        "letters": ["ש", "ל", "ו", "ם"],  # noqa: RUF001
        "gematria": 376,
    }

    result = adapt_ai_noun(ai_noun)

    assert result["letters"] == ["ש", "ל", "ו", "ם"]  # noqa: RUF001
    assert isinstance(result["letters"], list)
    assert len(result["letters"]) == 4


def test_adapt_ai_noun_zero_gematria():
    """Test handling of zero gematria value."""
    ai_noun = {
        "hebrew": "test",
        "gematria": 0,
    }

    result = adapt_ai_noun(ai_noun)

    assert result["gematria_value"] == 0
    assert result["gematria"] == 0
    assert result["value"] == 0


def test_adapt_ai_noun_zero_freq():
    """Test handling of zero frequency."""
    ai_noun = {
        "hebrew": "test",
        "gematria": 50,
        "freq": 0,
    }

    result = adapt_ai_noun(ai_noun)

    assert result["freq"] == 0
