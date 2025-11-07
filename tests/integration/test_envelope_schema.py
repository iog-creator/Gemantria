import json, pathlib

def test_unified_envelope_shape():
    p = pathlib.Path("share/exports/unified_envelope.json")
    assert p.exists(), "expected share/exports/unified_envelope.json"
    d = json.load(open(p,"r",encoding="utf-8"))
    for k in ("schema","book","generated_at","sources","ai_nouns","graph","stats","temporal","correlation"):
        assert k in d
