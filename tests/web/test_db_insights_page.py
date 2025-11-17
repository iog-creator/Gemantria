#!/usr/bin/env python3
"""
Tests for DB insights HTML page.

Phase-8E: Verifies /db-insights page renders correctly and contains required elements.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from src.services.api_server import app  # noqa: E402

client = TestClient(app)


def test_db_insights_page_returns_200():
    """Test that /db-insights returns 200 OK."""
    response = client.get("/db-insights")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def test_db_insights_page_contains_title():
    """Test that /db-insights contains 'DB Health Timeline' title."""
    response = client.get("/db-insights")
    assert response.status_code == 200
    content = response.text
    assert "DB Health Timeline" in content
    assert "Recent database health" in content


def test_db_insights_page_contains_chart_canvas():
    """Test that /db-insights contains chart canvas element."""
    response = client.get("/db-insights")
    assert response.status_code == 200
    content = response.text
    assert "dbHealthChart" in content
    assert "<canvas" in content
    assert 'id="dbHealthChart"' in content


def test_db_insights_page_contains_chart_library():
    """Test that /db-insights includes Chart.js library."""
    response = client.get("/db-insights")
    assert response.status_code == 200
    content = response.text
    assert "chart.js" in content.lower() or "chartjs" in content.lower()
    assert "cdn.jsdelivr.net" in content or "cdnjs.cloudflare.com" in content


def test_db_insights_page_fetches_api_endpoint():
    """Test that /db-insights page JavaScript fetches /api/db/health_timeline."""
    response = client.get("/db-insights")
    assert response.status_code == 200
    content = response.text
    assert "/api/db/health_timeline" in content
    assert "fetch" in content.lower()


def test_db_insights_page_contains_summary_sections():
    """Test that /db-insights contains summary sections."""
    response = client.get("/db-insights")
    assert response.status_code == 200
    content = response.text
    assert "Current Status" in content
    assert "Health Mode Over Time" in content
    assert "Summary" in content
    assert "latest-mode" in content
    assert "latest-status" in content
    assert "latest-generated" in content
    assert "latest-notes" in content


def test_db_insights_page_has_auto_refresh():
    """Test that /db-insights page has auto-refresh logic."""
    response = client.get("/db-insights")
    assert response.status_code == 200
    content = response.text
    assert "setInterval" in content
    assert "30000" in content
