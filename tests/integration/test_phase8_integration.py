import os
import json

def _j(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def test_temporal_patterns_export_exists():
    p = "exports/temporal_patterns.json"
    assert os.path.exists(p), "temporal_patterns.json missing"
    data = _j(p)
    assert "rolling_statistics" in data and isinstance(data["rolling_statistics"], list)

def test_forecast_export_exists():
    p = "exports/pattern_forecast.json"
    assert os.path.exists(p), "pattern_forecast.json missing"
