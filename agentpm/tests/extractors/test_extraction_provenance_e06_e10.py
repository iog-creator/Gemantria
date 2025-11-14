import re

import pytest

from datetime import datetime, UTC

from agentpm.extractors.provenance import ensure_provenance, stamp_batch, guard_provenance


RFC3339_RX = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")


def test_e06_provenance_fields_present():
    """E06: Provenance present - every output has model, seed, ts_iso (RFC3339)."""
    output = ensure_provenance("qwen2.5", 42, "test analysis")
    
    assert "model" in output
    assert "seed" in output
    assert "ts_iso" in output
    assert output["model"] == "qwen2.5"
    assert output["seed"] == 42
    assert isinstance(output["ts_iso"], str)
    assert RFC3339_RX.match(output["ts_iso"]), f"ts_iso must match RFC3339: {output['ts_iso']}"


def test_e07_ts_iso_rfc3339():
    """E07: RFC3339 - ts_iso validates; within-batch monotonic."""
    items = [{"text": "item1"}, {"text": "item2"}, {"text": "item3"}]
    base_dt = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
    
    stamped = stamp_batch(items, "qwen2.5", 42, base_dt=base_dt)
    
    assert len(stamped) == 3
    timestamps = [s["ts_iso"] for s in stamped]
    
    # Validate RFC3339 format
    for ts in timestamps:
        assert RFC3339_RX.match(ts), f"ts_iso must match RFC3339: {ts}"
        # Validate it can be parsed
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        assert dt.tzinfo is not None
    
    # Validate monotonic (each timestamp should be 1 second later)
    for i in range(1, len(timestamps)):
        prev_dt = datetime.fromisoformat(timestamps[i-1].replace("Z", "+00:00"))
        curr_dt = datetime.fromisoformat(timestamps[i].replace("Z", "+00:00"))
        assert curr_dt > prev_dt, "timestamps must be monotonic within batch"


def test_e08_negative_missing_model_errors():
    """E08: Negative - missing model is guardable error."""
    # Test ensure_provenance raises on missing model
    with pytest.raises(ValueError, match="model is required"):
        ensure_provenance("", 42, None)
    
    with pytest.raises(ValueError, match="model is required"):
        ensure_provenance("   ", 42, None)
    
    # Test guard_provenance raises on missing model
    sample = {"seed": 42, "ts_iso": "2025-01-01T00:00:00Z"}
    with pytest.raises(ValueError, match="provenance guard: missing 'model'"):
        guard_provenance(sample)
    
    sample_empty = {"model": "", "seed": 42, "ts_iso": "2025-01-01T00:00:00Z"}
    with pytest.raises(ValueError, match="provenance guard: 'model' must be non-empty"):
        guard_provenance(sample_empty)


def test_e09_negative_seed_type():
    """E09: Negative - seed must be integer."""
    # Test ensure_provenance raises on non-integer seed
    with pytest.raises(ValueError, match="seed must be int"):
        ensure_provenance("qwen2.5", "forty-two", None)
    
    # Test guard_provenance raises on non-integer seed
    sample = {"model": "qwen2.5", "seed": "forty-two", "ts_iso": "2025-01-01T00:00:00Z"}
    with pytest.raises(ValueError, match="provenance guard: 'seed' must be integer"):
        guard_provenance(sample)


def test_e10_edge_empty_analysis_keeps_provenance():
    """E10: Edge - empty analysis still preserves provenance fields."""
    # Test with empty string
    output1 = ensure_provenance("qwen2.5", 42, "")
    assert "model" in output1
    assert "seed" in output1
    assert "ts_iso" in output1
    assert output1["analysis"] == ""
    
    # Test with whitespace-only
    output2 = ensure_provenance("qwen2.5", 42, "   ")
    assert "model" in output2
    assert "seed" in output2
    assert "ts_iso" in output2
    assert output2["analysis"] == "   "
    
    # Test with None (no analysis field added)
    output3 = ensure_provenance("qwen2.5", 42, None)
    assert "model" in output3
    assert "seed" in output3
    assert "ts_iso" in output3
    assert "analysis" not in output3
