import re

import pytest
from agentpm.extractors.provenance import ensure_provenance, stamp_batch


RFC3339_RX = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def test_e06_provenance_fields_present():
    rec = ensure_provenance("qwen2.5", 42, "note")
    assert all(k in rec for k in ("model", "seed", "ts_iso"))
    assert rec["model"] == "qwen2.5" and isinstance(rec["seed"], int)


def test_e07_ts_iso_rfc3339_monotonic_batch():
    batch = stamp_batch([{}, {}, {}], "qwen2.5", 7)
    ts = [r["ts_iso"] for r in batch]
    assert all(RFC3339_RX.match(t) for t in ts)
    assert ts == sorted(ts)  # monotonic


def test_e08_negative_missing_model_errors():
    with pytest.raises(ValueError):
        ensure_provenance("", 42, "x")


def test_e09_negative_seed_type():
    with pytest.raises(ValueError):
        ensure_provenance("qwen2.5", "forty-two", "x")


def test_e10_edge_empty_analysis_keeps_provenance():
    rec = ensure_provenance("qwen2.5", 42, "   ")
    assert all(k in rec for k in ("model", "seed", "ts_iso"))
    assert "analysis" in rec  # preserved even if whitespace
