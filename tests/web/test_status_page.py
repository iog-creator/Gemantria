#!/usr/bin/env python3
"""
Tests for system status HTML page.

Phase-7G: Verifies /status page renders correctly and contains required elements.
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
def test_status_page_returns_200(mock_get_status):
    """Test that /status returns 200 OK."""
    mock_get_status.return_value = {
        "db": {"reachable": True, "mode": "ready", "notes": "Database is ready"},
        "lm": {"slots": [], "notes": "No LM slots"},
    }

    response = client.get("/status")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


@patch("src.services.api_server.get_system_status")
def test_status_page_contains_system_status_title(mock_get_status):
    """Test that /status contains 'System Status' title."""
    mock_get_status.return_value = {
        "db": {"reachable": True, "mode": "ready", "notes": "Database is ready"},
        "lm": {"slots": [], "notes": "No LM slots"},
    }

    response = client.get("/status")
    assert response.status_code == 200
    content = response.text
    assert "System Status" in content


@patch("src.services.api_server.get_system_status")
def test_status_page_contains_db_status_section(mock_get_status):
    """Test that /status contains DB Status section."""
    mock_get_status.return_value = {
        "db": {"reachable": True, "mode": "ready", "notes": "Database is ready"},
        "lm": {"slots": [], "notes": "No LM slots"},
    }

    response = client.get("/status")
    assert response.status_code == 200
    content = response.text
    assert "DB Status" in content


@patch("src.services.api_server.get_system_status")
def test_status_page_contains_lm_slots_section(mock_get_status):
    """Test that /status contains LM Slots section."""
    mock_get_status.return_value = {
        "db": {"reachable": True, "mode": "ready", "notes": "Database is ready"},
        "lm": {"slots": [], "notes": "No LM slots"},
    }

    response = client.get("/status")
    assert response.status_code == 200
    content = response.text
    assert "LM Slots" in content


@patch("src.services.api_server.get_system_status")
def test_status_page_fetches_api_endpoint(mock_get_status):
    """Test that /status page JavaScript fetches /api/status/system."""
    mock_get_status.return_value = {
        "db": {"reachable": True, "mode": "ready", "notes": "Database is ready"},
        "lm": {"slots": [], "notes": "No LM slots"},
    }

    response = client.get("/status")
    assert response.status_code == 200
    content = response.text
    assert "/api/status/system" in content
    assert "fetch" in content.lower()


@patch("src.services.api_server.get_system_status")
def test_status_page_contains_tailwind(mock_get_status):
    """Test that /status page uses Tailwind CSS."""
    mock_get_status.return_value = {
        "db": {"reachable": True, "mode": "ready", "notes": "Database is ready"},
        "lm": {"slots": [], "notes": "No LM slots"},
    }

    response = client.get("/status")
    assert response.status_code == 200
    content = response.text
    assert "tailwindcss.com" in content or "tailwind" in content.lower()


@patch("src.services.api_server.get_system_status")
def test_status_page_contains_explanation_section(mock_get_status):
    """Test that /status page contains Explanation section."""
    mock_get_status.return_value = {
        "db": {"reachable": True, "mode": "ready", "notes": "Database is ready"},
        "lm": {"slots": [], "notes": "No LM slots"},
    }

    response = client.get("/status")
    assert response.status_code == 200
    content = response.text
    assert "Explanation" in content
    assert "explanation-headline" in content
    assert "explanation-details" in content
    assert "explanation-content" in content
    assert "explanation-error" in content
    assert "/api/status/explain" in content
