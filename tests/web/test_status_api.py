#!/usr/bin/env python3
"""
Tests for system status API endpoint.

Phase-7G: Verifies /api/status/system endpoint returns correct DB + LM health snapshot.
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


@patch("src.services.api_server.get_system_status")
def test_status_api_returns_db_and_lm(mock_get_status):
    """Test that /api/status/system returns db and lm keys."""
    # Mock system status
    mock_get_status.return_value = {
        "db": {
            "reachable": True,
            "mode": "ready",
            "notes": "Database is ready and all checks passed",
        },
        "lm": {
            "slots": [
                {
                    "name": "local_agent",
                    "provider": "ollama",
                    "model": "granite4:tiny-h",
                    "service": "OK",
                },
                {
                    "name": "embedding",
                    "provider": "ollama",
                    "model": "bge-m3:latest",
                    "service": "OK",
                },
                {
                    "name": "reranker",
                    "provider": "ollama",
                    "model": "bge-reranker-v2-m3:latest",
                    "service": "OK",
                },
                {
                    "name": "theology",
                    "provider": "lmstudio",
                    "model": "Christian-Bible-Expert-v2.0-12B",
                    "service": "OK",
                },
            ],
            "notes": "Local-only providers (Ollama + LM Studio on 127.0.0.1).",
        },
    }

    response = client.get("/api/status/system")
    assert response.status_code == 200

    data = response.json()
    assert "db" in data
    assert "lm" in data


@patch("src.services.api_server.get_system_status")
def test_status_api_has_four_lm_slots(mock_get_status):
    """Test that /api/status/system returns four LM slots."""
    mock_get_status.return_value = {
        "db": {"reachable": False, "mode": "db_off", "notes": "Database unavailable"},
        "lm": {
            "slots": [
                {"name": "local_agent", "provider": "ollama", "model": "test", "service": "OK"},
                {"name": "embedding", "provider": "ollama", "model": "test", "service": "OK"},
                {"name": "reranker", "provider": "ollama", "model": "test", "service": "OK"},
                {"name": "theology", "provider": "lmstudio", "model": "test", "service": "OK"},
            ],
            "notes": "Local-only providers (Ollama + LM Studio on 127.0.0.1).",
        },
    }

    response = client.get("/api/status/system")
    assert response.status_code == 200

    data = response.json()
    assert len(data["lm"]["slots"]) == 4

    slot_names = {slot["name"] for slot in data["lm"]["slots"]}
    assert slot_names == {"local_agent", "embedding", "reranker", "theology"}


@patch("src.services.api_server.get_system_status")
def test_status_api_handles_exceptions(mock_get_status):
    """Test that /api/status/system handles exceptions gracefully."""
    # Reset mock to clear any previous side_effect
    mock_get_status.reset_mock()
    mock_get_status.side_effect = Exception("Test error")

    response = client.get("/api/status/system")
    # FastAPI exception handler should return 500
    assert response.status_code == 500

    data = response.json()
    assert "detail" in data


@patch("src.services.api_server.get_system_status")
def test_status_api_db_modes(mock_get_status):
    """Test that /api/status/system returns correct DB modes."""
    for mode in ["ready", "db_off", "partial"]:
        # Reset mock for each iteration
        mock_get_status.reset_mock()
        mock_get_status.return_value = {
            "db": {
                "reachable": mode == "ready",
                "mode": mode,
                "notes": f"Database mode: {mode}",
            },
            "lm": {"slots": [], "notes": "No LM slots"},
        }

        response = client.get("/api/status/system")
        assert response.status_code == 200

        data = response.json()
        assert data["db"]["mode"] == mode
        assert data["db"]["reachable"] == (mode == "ready")
