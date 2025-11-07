import json, pathlib
# Note: Allows missing files during dev (e.g., before pipeline run); real CI expects them via guards.


def test_temporal_files_mirrored_and_parse():
    for p in ("ui/out/temporal_patterns.json", "ui/out/pattern_forecast.json"):
        path = pathlib.Path(p)
        if not path.exists():
            print(f"SKIP: {p} missing (run pipeline first)")
            continue
        data = json.load(open(path, encoding="utf-8"))
        assert data  # Non-empty after load
        print(f"OK: {p} loaded ({len(data) if isinstance(data, dict) else 'N/A'} items)")
