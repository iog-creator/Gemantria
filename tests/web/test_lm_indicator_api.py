#!/usr/bin/env python3
"""
Tests for LM indicator API endpoint.

Phase-8C: Verifies /api/lm/indicator endpoint returns correct LM indicator data.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from src.services.api_server import app  # noqa: E402

client = TestClient(app)


@patch("src.services.api_server.INDICATOR_PATH", Path("share/atlas/control_plane/lm_indicator.json"))
@patch("pathlib.Path.exists")
@patch("pathlib.Path.read_text")
def test_lm_indicator_returns_snapshot(mock_read_text, mock_exists):
    """Test that /api/lm/indicator returns snapshot when file exists."""
    mock_exists.return_value = True
    mock_read_text.return_value = json.dumps(
        {
            "status": "healthy",
            "reason": "ok",
            "success_rate": 0.98,
            "error_rate": 0.02,
            "total_calls": 1000,
            "db_off": False,
            "top_error_reason": None,
            "window_days": 7,
            "generated_at": "2025-11-15T02:33:53.743825+00:00",
        }
    )

    response = client.get("/api/lm/indicator")
    assert response.status_code == 200

    data = response.json()
    assert "snapshot" in data
    assert data["snapshot"]["status"] == "healthy"
    assert data["snapshot"]["success_rate"] == 0.98
    assert data["snapshot"]["total_calls"] == 1000


@patch("src.services.api_server.INDICATOR_PATH", Path("share/atlas/control_plane/lm_indicator.json"))
@patch("pathlib.Path.exists")
def test_lm_indicator_handles_missing_file(mock_exists):
    """Test that /api/lm/indicator returns empty snapshot when file is missing."""
    mock_exists.return_value = False

    response = client.get("/api/lm/indicator")
    assert response.status_code == 200

    data = response.json()
    assert "snapshot" in data
    assert data["snapshot"] is None
    assert "note" in data
    assert "not available" in data["note"].lower()


@patch("src.services.api_server.INDICATOR_PATH", Path("share/atlas/control_plane/lm_indicator.json"))
@patch("pathlib.Path.exists")
@patch("pathlib.Path.read_text")
def test_lm_indicator_handles_invalid_json(mock_read_text, mock_exists):
    """Test that /api/lm/indicator handles invalid JSON gracefully."""
    mock_exists.return_value = True
    mock_read_text.return_value = "invalid json {"

    response = client.get("/api/lm/indicator")
    assert response.status_code == 500

    data = response.json()
    assert "detail" in data
    assert "parse" in data["detail"].lower() or "json" in data["detail"].lower()
