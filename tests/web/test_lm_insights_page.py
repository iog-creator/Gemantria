#!/usr/bin/env python3
"""
Tests for LM insights HTML page.

Phase-8C: Verifies /lm-insights page renders correctly and contains required elements.
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


def test_lm_insights_page_returns_200():
    """Test that /lm-insights returns 200 OK."""
    response = client.get("/lm-insights")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def test_lm_insights_page_contains_title():
    """Test that /lm-insights contains 'LM Insights' title."""
    response = client.get("/lm-insights")
    assert response.status_code == 200
    content = response.text
    assert "LM Insights" in content
    assert "Recent local LM health" in content


def test_lm_insights_page_contains_chart_canvas():
    """Test that /lm-insights contains chart canvas element."""
    response = client.get("/lm-insights")
    assert response.status_code == 200
    content = response.text
    assert "lmIndicatorChart" in content
    assert "<canvas" in content
    assert 'id="lmIndicatorChart"' in content


def test_lm_insights_page_contains_chart_library():
    """Test that /lm-insights includes Chart.js library."""
    response = client.get("/lm-insights")
    assert response.status_code == 200
    content = response.text
    assert "chart.js" in content.lower() or "chartjs" in content.lower()
    assert "cdn.jsdelivr.net" in content or "cdnjs.cloudflare.com" in content


def test_lm_insights_page_fetches_api_endpoint():
    """Test that /lm-insights page JavaScript fetches /api/lm/indicator."""
    response = client.get("/lm-insights")
    assert response.status_code == 200
    content = response.text
    assert "/api/lm/indicator" in content
    assert "fetch" in content.lower()


def test_lm_insights_page_contains_metrics_sections():
    """Test that /lm-insights contains metrics summary sections."""
    response = client.get("/lm-insights")
    assert response.status_code == 200
    content = response.text
    assert "Current Status" in content
    assert "Success & Error Rates" in content
    assert "Metrics Summary" in content
    assert "total-calls" in content
    assert "success-rate" in content
    assert "error-rate" in content
