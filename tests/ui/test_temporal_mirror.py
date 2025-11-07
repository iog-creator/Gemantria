import json, pathlib

def test_temporal_files_mirrored_and_parse():
    for p in ("ui/out/temporal_patterns.json","ui/out/pattern_forecast.json"):
        path=pathlib.Path(p)
        assert path.exists(), f"missing: {p}"
        json.load(open(path,"r",encoding="utf-8"))
