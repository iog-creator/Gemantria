#!/usr/bin/env python3
"""
Tests for LM status HTML page (Phase-3D D3).

Verifies that the HTML status page exists and contains required elements.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
STATUS_HTML = REPO_ROOT / "docs" / "atlas" / "html" / "lm_status.html"


def test_lm_status_html_exists() -> None:
    """Test that LM status HTML page exists."""
    assert STATUS_HTML.exists(), f"LM status HTML missing: {STATUS_HTML}"


def test_lm_status_html_contains_title() -> None:
    """Test that LM status HTML contains 'Language Model Status' title."""
    content = STATUS_HTML.read_text(encoding="utf-8")
    assert "Language Model Status" in content, "Missing 'Language Model Status' title"


def test_lm_status_html_contains_lm_studio() -> None:
    """Test that LM status HTML contains 'LM Studio' reference."""
    content = STATUS_HTML.read_text(encoding="utf-8")
    assert "LM Studio" in content, "Missing 'LM Studio' reference"


def test_lm_status_html_contains_connection_status() -> None:
    """Test that LM status HTML contains connection status element."""
    content = STATUS_HTML.read_text(encoding="utf-8")
    assert (
        "connection-status" in content or "Connection Status" in content
    ), "Missing connection status"


def test_lm_status_html_contains_health_metrics() -> None:
    """Test that LM status HTML contains health metrics elements."""
    content = STATUS_HTML.read_text(encoding="utf-8")
    assert "health-score" in content or "Health Score" in content, "Missing health score"
    assert "success-rate" in content or "Success Rate" in content, "Missing success rate"
    assert "error-rate" in content or "Error Rate" in content, "Missing error rate"


def test_lm_status_html_contains_usage_metrics() -> None:
    """Test that LM status HTML contains usage metrics elements."""
    content = STATUS_HTML.read_text(encoding="utf-8")
    assert "total-calls" in content or "Total Calls" in content, "Missing total calls"
    assert "successful-calls" in content or "Successful" in content, "Missing successful calls"
    assert "failed-calls" in content or "Failed" in content, "Missing failed calls"


def test_lm_status_html_contains_db_off_handling() -> None:
    """Test that LM status HTML handles db_off gracefully."""
    content = STATUS_HTML.read_text(encoding="utf-8")
    assert (
        "db-offline" in content
        or "db_off" in content
        or "database is currently offline" in content.lower()
    ), "Missing db_off handling"


def test_lm_status_html_contains_backlink() -> None:
    """Test that LM status HTML contains backlink to Atlas."""
    content = STATUS_HTML.read_text(encoding="utf-8")
    assert "Back to Atlas" in content or "../index.html" in content, "Missing backlink to Atlas"
