#!/usr/bin/env python3
"""
Tests for system status HTML page.

Phase-7G: Verifies /status page renders correctly and contains required elements.
AgentPM-Next:M4: Verifies KB doc metrics elements are present.
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
    assert "System Status" in response.text


@patch("agentpm.status.snapshot.get_system_snapshot")
def test_status_page_contains_doc_metrics_elements(mock_get_snapshot):
    """Test that /status contains KB Doc Metrics elements (AgentPM-Next:M4)."""
    mock_get_snapshot.return_value = {
        "db": {"reachable": True, "mode": "ready", "notes": "Database is ready"},
        "lm": {"slots": [], "notes": "No LM slots"},
        "kb_doc_health": {
            "available": True,
            "metrics": {
                "kb_fresh_ratio": {"overall": 0.95},
                "kb_fixes_applied_last_7d": 12,
                "kb_missing_count": 1,
            },
        },
    }

    response = client.get("/status")
    assert response.status_code == 200
    # Check for new elements
    assert 'id="doc-metrics-container"' in response.text
    assert 'id="doc-freshness-val"' in response.text
    assert 'id="doc-fixes-val"' in response.text
    assert 'id="doc-missing-val"' in response.text
    assert "Freshness" in response.text
    assert "Fixes (7d)" in response.text
