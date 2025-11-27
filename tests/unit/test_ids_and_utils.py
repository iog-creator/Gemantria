from agentpm.modules.gematria.utils.hebrew_utils import calc_string
from src.core.ids import content_hash, normalize_hebrew, uuidv7_surrogate


def test_calc_string_format():
    """Test calc_string format for known words."""
    assert calc_string("אדם") == "א(1) + ד(4) + ם(40) = 45"
    assert calc_string("הבל") == "ה(5) + ב(2) + ל(30) = 37"


def test_normalize_hebrew_idempotent():
    """Test that normalize_hebrew is idempotent."""
    text = "הֶבֶל־;:"  # nikud + maqaf + punctuation
    first_pass = normalize_hebrew(text)
    second_pass = normalize_hebrew(first_pass)
    assert first_pass == second_pass == "הבל"


def test_uuidv7_surrogate_format():
    """Test uuidv7_surrogate returns properly formatted UUID."""
    uuid_str = uuidv7_surrogate()
    assert len(uuid_str) == 36  # Standard UUID format length
    assert uuid_str.count("-") == 4  # Standard UUID has 4 hyphens
    # Should be able to create another UUID that's different
    another_uuid = uuidv7_surrogate()
    assert uuid_str != another_uuid


def test_content_hash_sha256():
    """Test content_hash uses SHA-256 and produces consistent results."""
    payload = {"key": "value", "number": 42}
    keys = ["key", "number"]

    # Test that it produces a hash
    result = content_hash(payload, keys)
    assert len(result) == 64  # SHA-256 produces 64 character hex string
    assert result.isalnum()  # Should only contain alphanumeric characters

    # Test that same inputs produce same hash
    result2 = content_hash(payload, keys)
    assert result == result2

    # Test that different inputs produce different hash
    payload_diff = {"key": "different", "number": 42}
    result3 = content_hash(payload_diff, keys)
    assert result != result3
