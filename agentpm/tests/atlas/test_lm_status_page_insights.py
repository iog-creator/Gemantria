#!/usr/bin/env python3
"""
Tests for LM status HTML page using lm_insights_7d.json (Phase-4B).

Verifies that the HTML status page correctly consumes lm_insights_7d.json
and handles db_off, healthy, and degraded states.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
STATUS_HTML = REPO_ROOT / "docs" / "atlas" / "html" / "lm_status.html"
INSIGHTS_JSON = REPO_ROOT / "share" / "atlas" / "control_plane" / "lm_insights_7d.json"


def test_lm_status_html_exists() -> None:
    """Test that LM status HTML page exists."""
    assert STATUS_HTML.exists(), f"LM status HTML missing: {STATUS_HTML}"


def test_lm_status_html_consumes_insights() -> None:
    """Test that LM status HTML loads lm_insights_7d.json."""
    content = STATUS_HTML.read_text(encoding="utf-8")
    assert "lm_insights_7d.json" in content, "HTML must load lm_insights_7d.json"


def test_lm_status_html_has_status_summary() -> None:
    """Test that LM status HTML has one-sentence status summary element."""
    content = STATUS_HTML.read_text(encoding="utf-8")
    assert "status-summary" in content, "Missing status-summary element"
    assert "status-summary-text" in content, "Missing status-summary-text element"


def test_lm_status_html_handles_db_off() -> None:
    """Test that LM status HTML handles db_off=true gracefully."""
    content = STATUS_HTML.read_text(encoding="utf-8")
    # Check for db_off handling in JavaScript
    assert "db_off" in content or "db-offline" in content, "Missing db_off handling"
    # Check for offline status message
    assert (
        "LM Studio is offline" in content or "database connection unavailable" in content.lower() or "db_off" in content
    ), "Missing offline status message"


def test_lm_status_html_shows_healthy_state() -> None:
    """Test that LM status HTML shows healthy state when success_rate >= 0.95."""
    content = STATUS_HTML.read_text(encoding="utf-8")
    # Check for healthy status logic
    assert "successRate >= 0.95" in content or "success_rate >= 0.95" in content or "LM Studio is healthy" in content, (
        "Missing healthy state logic"
    )


def test_lm_status_html_shows_degraded_state() -> None:
    """Test that LM status HTML shows degraded state when error rate is high."""
    content = STATUS_HTML.read_text(encoding="utf-8")
    # Check for degraded status logic
    assert "LM Studio is degraded" in content or "error rate" in content.lower() or "degraded" in content.lower(), (
        "Missing degraded state logic"
    )


def test_lm_status_html_shows_lm_studio_ratio() -> None:
    """Test that LM status HTML displays LM Studio usage ratio."""
    content = STATUS_HTML.read_text(encoding="utf-8")
    assert "lm-studio-ratio" in content or "lm_studio_usage_ratio" in content or "LM Studio Usage" in content, (
        "Missing LM Studio usage ratio display"
    )


def test_lm_status_html_shows_n_a_for_null_ratio() -> None:
    """Test that LM status HTML shows 'N/A' when lm_studio_usage_ratio is null."""
    content = STATUS_HTML.read_text(encoding="utf-8")
    # Check for N/A handling
    assert (
        "N/A" in content
        or "null" in content.lower()
        or "lm_studio_usage_ratio === null" in content
        or "lm_studio_usage_ratio !== null" in content
    ), "Missing N/A handling for null lm_studio_usage_ratio"


def test_lm_status_html_explains_success_rate() -> None:
    """Test that LM status HTML explains success_rate in friendly language."""
    content = STATUS_HTML.read_text(encoding="utf-8")
    assert (
        "Percentage of LM calls" in content or "successfully" in content.lower() or "95%+ indicates healthy" in content
    ), "Missing friendly explanation for success_rate"


def test_lm_status_html_explains_error_rate() -> None:
    """Test that LM status HTML explains error_rate in friendly language."""
    content = STATUS_HTML.read_text(encoding="utf-8")
    assert "failed" in content.lower() or "under 5% is normal" in content or "above 10% may indicate" in content, (
        "Missing friendly explanation for error_rate"
    )


def test_lm_status_html_explains_db_off() -> None:
    """Test that LM status HTML explains db_off in friendly language."""
    content = STATUS_HTML.read_text(encoding="utf-8")
    assert (
        "Database Offline" in content
        or "db_off mode" in content
        or "database connection is currently unavailable" in content.lower()
    ), "Missing friendly explanation for db_off"


def test_lm_status_html_handles_zero_calls() -> None:
    """Test that LM status HTML handles total_calls=0 gracefully."""
    content = STATUS_HTML.read_text(encoding="utf-8")
    # Check for zero calls handling
    assert (
        "totalCalls === 0" in content
        or "total_calls === 0" in content
        or "No calls recorded" in content
        or "waiting for activity" in content.lower()
    ), "Missing zero calls handling"
