import re

import pytest

from datetime import datetime


pytestmark = pytest.mark.xfail(strict=False, reason="M2+ provenance TVs (E06-E10) not implemented yet")


RFC3339_RX = re.compile(r"^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d+)?Z$")


def test_e06_provenance_fields_present():
    sample = {"model": None, "seed": None, "ts_iso": None}

    assert all(k in sample for k in ("model", "seed", "ts_iso"))

    raise AssertionError("Wire extractor to populate provenance")


def test_e07_ts_iso_rfc3339():
    ts = "0000-00-00T00:00:00Z"  # invalid on purpose for xfail

    assert RFC3339_RX.match(ts), "ts_iso must match RFC3339"

    datetime.fromisoformat(ts.replace("Z", "+00:00"))


def test_e08_negative_missing_model_errors():
    sample = {"seed": 42, "ts_iso": "2025-01-01T00:00:00Z"}

    assert "model" in sample, "missing `model` should be guardable error"

    raise AssertionError("Guard should catch missing `model`")


def test_e09_negative_seed_type():
    sample = {"model": "qwen2.5", "seed": "forty-two", "ts_iso": "2025-01-01T00:00:00Z"}

    assert isinstance(sample.get("seed"), int), "`seed` must be an integer"


def test_e10_edge_empty_analysis_keeps_provenance():
    sample = {"model": "qwen2.5", "seed": 42, "ts_iso": "2025-01-01T00:00:00Z", "analysis": "   "}

    assert all(k in sample for k in ("model", "seed", "ts_iso"))

    raise AssertionError("Provenance must persist even with empty analysis")
