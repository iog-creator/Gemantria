import json
import os
from pathlib import Path

import psycopg
import pytest

from scripts.export_stats import export_forecast, export_temporal_patterns


def _dsn():
    dsn = os.getenv("GEMATRIA_DSN")
    if not dsn:
        pytest.skip("GEMATRIA_DSN not set")
    return dsn


def test_temporal_and_forecast_exports(tmp_path, monkeypatch):
    monkeypatch.setenv("EXPORT_DIR", str(tmp_path))
    with psycopg.connect(_dsn()) as conn:
        t = export_temporal_patterns(conn)
        f = export_forecast(conn)
    tp = Path(tmp_path) / "temporal_patterns.json"
    fp = Path(tmp_path) / "pattern_forecast.json"
    # The exporter writes in main(); in this test we validate structures only
    # Ensure returned structures are valid dicts with expected keys
    assert isinstance(t, dict) and "temporal_patterns" in t and "metadata" in t
    assert isinstance(f, dict) and "forecasts" in f and "metadata" in f
    # Optionally, write files here to simulate API consumption
    tp.write_text(json.dumps(t))
    fp.write_text(json.dumps(f))
    assert tp.exists() and fp.exists()
