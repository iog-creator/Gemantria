#!/usr/bin/env python3
"""
Tests for status explanation API endpoint.

Phase-8B: Verifies /api/status/explain endpoint returns correct explanation dict.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from src.services.api_server import app  # noqa: E402

client = TestClient(app)


@patch("src.services.api_server.explain_system_status")
def test_status_explain_returns_explanation_dict(mock_explain):
    """Test that /api/status/explain returns level/headline/details."""
    mock_explain.return_value = {
        "level": "WARN",
        "headline": "Database is partially configured",
        "details": "Database is connected, but some tables or features are missing.",
    }

    response = client.get("/api/status/explain")
    assert response.status_code == 200

    data = response.json()
    assert "level" in data
    assert "headline" in data
    assert "details" in data
    assert data["level"] == "WARN"
    assert data["headline"] == "Database is partially configured"
    assert data["details"] == "Database is connected, but some tables or features are missing."


@patch("src.services.api_server.explain_system_status")
def test_status_explain_handles_exceptions(mock_explain):
    """Test that /api/status/explain handles exceptions gracefully."""
    mock_explain.reset_mock()
    mock_explain.side_effect = Exception("Test error")

    response = client.get("/api/status/explain")
    assert response.status_code == 500

    data = response.json()
    assert "detail" in data
    assert "Failed to compute status explanation" in data["detail"]


@patch("src.services.api_server.explain_system_status")
def test_status_explain_all_levels(mock_explain):
    """Test that /api/status/explain returns all valid levels."""
    for level in ["OK", "WARN", "ERROR"]:
        mock_explain.reset_mock()
        mock_explain.return_value = {
            "level": level,
            "headline": f"Test {level} headline",
            "details": f"Test {level} details",
        }

        response = client.get("/api/status/explain")
        assert response.status_code == 200

        data = response.json()
        assert data["level"] == level
