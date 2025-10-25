import json
import subprocess
import time


def test_api_temporal_and_forecast_smoke(tmp_path, monkeypatch):
    # Minimal valid payloads per SSOT
    (tmp_path / "temporal_patterns.json").write_text(
        json.dumps(
            {
                "temporal_patterns": [
                    {
                        "series_id": "concept_1",
                        "unit": "chapter",
                        "window": 5,
                        "start_index": 1,
                        "end_index": 5,
                        "metric": "frequency",
                        "values": [1, 1, 2],
                        "method": "rolling_mean",
                        "book": "Genesis",
                        "change_points": [],
                    }
                ],
                "metadata": {
                    "generated_at": "2025-01-01T00:00:00Z",
                    "analysis_parameters": {
                        "default_unit": "chapter",
                        "default_window": 5,
                        "min_series_length": 3,
                    },
                    "total_series": 1,
                    "books_analyzed": ["Genesis"],
                },
            }
        )
    )
    (tmp_path / "pattern_forecast.json").write_text(
        json.dumps(
            {
                "forecasts": [
                    {
                        "series_id": "concept_1",
                        "book": "Genesis",
                        "horizon": 3,
                        "model": "sma",
                        "predictions": [1, 1, 1],
                    }
                ],
                "metadata": {
                    "generated_at": "2025-01-01T00:00:00Z",
                    "forecast_parameters": {
                        "default_horizon": 3,
                        "default_model": "sma",
                        "min_training_length": 3,
                    },
                    "total_forecasts": 1,
                    "books_forecasted": ["Genesis"],
                },
            }
        )
    )
    monkeypatch.setenv("EXPORT_DIR", str(tmp_path))
    proc = subprocess.Popen(["python", "-m", "src.services.api_server"])
    try:
        time.sleep(1.5)
        import urllib.request  # noqa: E402

        with urllib.request.urlopen(
            "http://127.0.0.1:8000/api/v1/temporal?unit=chapter&window=5"
        ) as r:
            data = json.loads(r.read().decode("utf-8"))
            assert data.get("result_count", 0) >= 1
        with urllib.request.urlopen(
            "http://127.0.0.1:8000/api/v1/forecast?horizon=3"
        ) as r:
            data = json.loads(r.read().decode("utf-8"))
            assert data.get("result_count", 0) >= 1
    finally:
        proc.terminate()
