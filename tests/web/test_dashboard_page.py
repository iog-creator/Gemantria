#!/usr/bin/env python3
"""
Tests for dashboard HTML page.

Phase-8D: Verifies /dashboard page renders correctly and contains required elements.
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


def test_dashboard_page_returns_200():
    """Test that /dashboard returns 200 OK."""
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def test_dashboard_page_contains_title():
    """Test that /dashboard contains 'System Dashboard' title."""
    response = client.get("/dashboard")
    assert response.status_code == 200
    content = response.text
    assert "System Dashboard" in content
    assert "Overview of system health" in content


def test_dashboard_page_contains_system_health_card():
    """Test that /dashboard contains System Health card."""
    response = client.get("/dashboard")
    assert response.status_code == 200
    content = response.text
    assert "System Health" in content
    assert "system-health-card" in content


def test_dashboard_page_contains_lm_insights_card():
    """Test that /dashboard contains LM Insights card."""
    response = client.get("/dashboard")
    assert response.status_code == 200
    content = response.text
    assert "LM Insights" in content
    assert "lm-insights-card" in content


def test_dashboard_page_fetches_system_status_api():
    """Test that /dashboard page JavaScript fetches /api/status/system."""
    response = client.get("/dashboard")
    assert response.status_code == 200
    content = response.text
    assert "/api/status/system" in content
    assert "fetch" in content.lower()


def test_dashboard_page_fetches_status_explain_api():
    """Test that /dashboard page JavaScript fetches /api/status/explain."""
    response = client.get("/dashboard")
    assert response.status_code == 200
    content = response.text
    assert "/api/status/explain" in content


def test_dashboard_page_fetches_lm_indicator_api():
    """Test that /dashboard page JavaScript fetches /api/lm/indicator."""
    response = client.get("/dashboard")
    assert response.status_code == 200
    content = response.text
    assert "/api/lm/indicator" in content


def test_dashboard_page_contains_view_details_links():
    """Test that /dashboard contains links to /status and /lm-insights."""
    response = client.get("/dashboard")
    assert response.status_code == 200
    content = response.text
    assert 'href="/status"' in content
    assert 'href="/lm-insights"' in content
    assert "View details" in content


def test_dashboard_page_contains_tailwind():
    """Test that /dashboard page uses Tailwind CSS."""
    response = client.get("/dashboard")
    assert response.status_code == 200
    content = response.text
    assert "tailwindcss.com" in content or "tailwind" in content.lower()


def test_dashboard_page_has_auto_refresh():
    """Test that /dashboard page has auto-refresh logic."""
    response = client.get("/dashboard")
    assert response.status_code == 200
    content = response.text
    assert "setInterval" in content
    assert "30000" in content


def test_dashboard_page_contains_rerank_metrics_tile():
    """Test that /dashboard contains Rerank / Edge Strength Metrics tile."""
    response = client.get("/dashboard")
    assert response.status_code == 200
    content = response.text
    assert "Rerank / Edge Strength Metrics" in content
    assert "rerank-metrics-card" in content


def test_dashboard_page_fetches_rerank_summary_api():
    """Test that /dashboard page JavaScript fetches /api/rerank/summary."""
    response = client.get("/dashboard")
    assert response.status_code == 200
    content = response.text
    assert "/api/rerank/summary" in content


def test_dashboard_page_contains_rerank_chart_container():
    """Test that /dashboard contains rerank chart container."""
    response = client.get("/dashboard")
    assert response.status_code == 200
    content = response.text
    assert "rerank-chart-container" in content
    assert "rerank-chart" in content
    assert "Edge Strength Distribution" in content


def test_dashboard_page_contains_rerank_explanatory_text():
    """Test that /dashboard contains explanatory text about edge_strength."""
    response = client.get("/dashboard")
    assert response.status_code == 200
    content = response.text
    assert "Edge Strength" in content
    # Check for edge strength formula components
    assert "0.5" in content and "cosine" in content and "rerank_score" in content
    assert "strong" in content.lower()
    assert "weak" in content.lower()
    assert "≥0.90" in content or "0.90" in content
    assert "≥0.75" in content or "0.75" in content
