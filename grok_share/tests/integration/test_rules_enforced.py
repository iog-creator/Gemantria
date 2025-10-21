from src.core.ids import content_hash, normalize_hebrew, uuidv7_surrogate


def test_normalize_strips_marks_and_punct():
    s = "הֶבֶל־;:"  # nikud + maqaf + punctuation
    assert normalize_hebrew(s) == "הבל"

def test_content_hash_stable():
    p = {"hebrew":"הבל","value":37,"primary_verse":"Ecclesiastes 1:2"}
    h1 = content_hash(p, ["hebrew","value","primary_verse"])
    h2 = content_hash(
        {"primary_verse": "Ecclesiastes 1:2", "value": 37, "hebrew": "הבל"},
        ["hebrew", "value", "primary_verse"],
    )
    assert h1 == h2 and len(h1)==64

def test_uuidv7_surrogate():
    id1 = uuidv7_surrogate()
    id2 = uuidv7_surrogate()
    assert id1 != id2  # Should be unique
    assert len(id1) == 36  # UUID4 format
