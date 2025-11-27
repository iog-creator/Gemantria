from agentpm.modules.gematria.utils.osis import extract_verse_references


def test_extract_osis_psalm_isaiah():
    text = "… Psalm 30:5 … Isaiah 43:2 …"
    got = extract_verse_references(text)
    # Should return list of dicts with osis and label keys
    osis_refs = {ref["osis"]: ref["label"] for ref in got}
    assert "Ps.30.5" in osis_refs
    assert "Isa.43.2" in osis_refs
    assert osis_refs["Ps.30.5"] == "Psalm 30:5"
    assert osis_refs["Isa.43.2"] == "Isaiah 43:2"
    print("✅ OSIS extraction test passed")


if __name__ == "__main__":
    test_extract_osis_psalm_isaiah()
