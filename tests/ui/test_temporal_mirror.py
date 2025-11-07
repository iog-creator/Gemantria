import json, os, pathlib, pytest

SKIP_DEV = os.getenv("ALLOW_UI_TEMPORAL_SKIP") == "1"


@pytest.mark.skipif(SKIP_DEV, reason="dev skip enabled via ALLOW_UI_TEMPORAL_SKIP=1")
def test_temporal_files_mirrored_and_parse():
    for p in ("ui/out/temporal_patterns.json", "ui/out/pattern_forecast.json"):
        path = pathlib.Path(p)
        assert path.exists(), f"missing: {p}"
        json.load(open(path, "r", encoding="utf-8"))
