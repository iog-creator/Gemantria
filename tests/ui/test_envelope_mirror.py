import json, pathlib

def test_envelope_file_mirrored_and_parse():
    p = pathlib.Path("ui/out/unified_envelope.json")
    assert p.exists(), "missing: ui/out/unified_envelope.json"
    json.load(open(p,"r",encoding="utf-8"))
