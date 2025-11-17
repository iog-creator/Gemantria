#!/usr/bin/env python3
"""
Tests for DB health timeline API endpoint.

Phase-8E: Verifies /api/db/health_timeline endpoint returns correct data shape.
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


def test_db_health_timeline_returns_200_when_file_exists():
    """Test that /api/db/health_timeline returns 200 OK when file exists."""
    mock_data = {
        "ok": True,
        "mode": "ready",
        "checks": {"driver_available": True, "connection_ok": True, "graph_stats_ready": True},
        "details": {"errors": []},
    }

    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.read_text", return_value=json.dumps(mock_data)):
            response = client.get("/api/db/health_timeline")
            assert response.status_code == 200
            data = response.json()
            assert "snapshots" in data
            assert len(data["snapshots"]) == 1
            assert data["snapshots"][0]["mode"] == "ready"
            assert data["snapshots"][0]["ok"] is True


def test_db_health_timeline_returns_empty_when_file_missing():
    """Test that /api/db/health_timeline returns empty snapshots when file is missing."""
    with patch("pathlib.Path.exists", return_value=False):
        response = client.get("/api/db/health_timeline")
        assert response.status_code == 200
        data = response.json()
        assert "snapshots" in data
        assert data["snapshots"] == []
        assert "note" in data


def test_db_health_timeline_handles_partial_mode():
    """Test that /api/db/health_timeline correctly handles partial mode."""
    mock_data = {
        "ok": False,
        "mode": "partial",
        "checks": {"driver_available": True, "connection_ok": True, "graph_stats_ready": False},
        "details": {"errors": ["graph_stats_table_missing: table does not exist"]},
    }

    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.read_text", return_value=json.dumps(mock_data)):
            response = client.get("/api/db/health_timeline")
            assert response.status_code == 200
            data = response.json()
            assert len(data["snapshots"]) == 1
            assert data["snapshots"][0]["mode"] == "partial"
            assert data["snapshots"][0]["ok"] is False
            assert "partial" in data["snapshots"][0]["notes"].lower()


def test_db_health_timeline_handles_db_off_mode():
    """Test that /api/db/health_timeline correctly handles db_off mode."""
    mock_data = {
        "ok": False,
        "mode": "db_off",
        "checks": {"driver_available": False, "connection_ok": False, "graph_stats_ready": False},
        "details": {"errors": ["driver_missing: Postgres driver not available"]},
    }

    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.read_text", return_value=json.dumps(mock_data)):
            response = client.get("/api/db/health_timeline")
            assert response.status_code == 200
            data = response.json()
            assert len(data["snapshots"]) == 1
            assert data["snapshots"][0]["mode"] == "db_off"
            assert data["snapshots"][0]["ok"] is False
            assert "unavailable" in data["snapshots"][0]["notes"].lower()


def test_db_health_timeline_handles_invalid_json():
    """Test that /api/db/health_timeline returns 500 for invalid JSON."""
    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.read_text", return_value="invalid json"):
            response = client.get("/api/db/health_timeline")
            assert response.status_code == 500
            assert "Failed to parse" in response.json()["detail"]


def test_db_health_timeline_includes_generated_at():
    """Test that /api/db/health_timeline includes generated_at timestamp."""
    mock_data = {
        "ok": True,
        "mode": "ready",
        "generated_at": "2025-11-15T02:33:53.743825+00:00",
        "checks": {"driver_available": True, "connection_ok": True, "graph_stats_ready": True},
        "details": {"errors": []},
    }

    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.read_text", return_value=json.dumps(mock_data)):
            response = client.get("/api/db/health_timeline")
            assert response.status_code == 200
            data = response.json()
            assert "generated_at" in data["snapshots"][0]
            assert data["snapshots"][0]["generated_at"] == "2025-11-15T02:33:53.743825+00:00"
