#!/usr/bin/env python3
"""
Phase-6 LM Studio Budget Tests

Tests for LM usage budgets and budget enforcement in guarded_lm_call().
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

from pmagent.runtime import lm_budget
from pmagent.runtime.lm_logging import guarded_lm_call


def test_check_lm_budget_db_off_is_fail_open(monkeypatch):
    """If the DB/control-plane is unavailable, budget checks must not brick usage."""

    # Mock _query_usage_for_app to raise an error
    def _fake_query(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError("db_off")

    monkeypatch.setattr(lm_budget, "_query_usage_for_app", _fake_query, raising=False)

    # Should return True (fail-open) when DB is unavailable
    allowed = lm_budget.check_lm_budget("test-app", tokens=100)
    assert allowed is True


def test_check_lm_budget_no_budget_table_is_fail_open(monkeypatch):
    """If budget table doesn't exist, allow all (backward compatible)."""
    # Mock psycopg to be available
    mock_psycopg = Mock()
    monkeypatch.setattr("pmagent.runtime.lm_budget.psycopg", mock_psycopg)
    monkeypatch.setenv("GEMATRIA_DSN", "postgresql://test")

    # Mock connection context manager
    mock_cur = Mock()
    mock_cur.fetchone.return_value = None  # Table doesn't exist
    mock_conn = Mock()
    mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cur)
    mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
    mock_psycopg.connect.return_value.__enter__ = Mock(return_value=mock_conn)
    mock_psycopg.connect.return_value.__exit__ = Mock(return_value=None)

    allowed = lm_budget.check_lm_budget("test-app", tokens=100)
    assert allowed is True


def test_check_lm_budget_no_budget_configured_is_allow(monkeypatch):
    """If no budget configured for app, allow (no budgets = no limits)."""
    # Mock psycopg to be available
    mock_psycopg = Mock()
    monkeypatch.setattr("pmagent.runtime.lm_budget.psycopg", mock_psycopg)
    monkeypatch.setenv("GEMATRIA_DSN", "postgresql://test")

    # Mock connection context manager
    mock_cur = Mock()
    mock_cur.fetchone.side_effect = [(True,), None]  # Table exists, no budget row
    mock_conn = Mock()
    mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cur)
    mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
    mock_psycopg.connect.return_value.__enter__ = Mock(return_value=mock_conn)
    mock_psycopg.connect.return_value.__exit__ = Mock(return_value=None)

    allowed = lm_budget.check_lm_budget("test-app", tokens=100)
    assert allowed is True


def test_check_lm_budget_within_limits_returns_true(monkeypatch):
    """If usage is within budget limits, return True."""
    # Mock psycopg to be available
    mock_psycopg = Mock()
    monkeypatch.setattr("pmagent.runtime.lm_budget.psycopg", mock_psycopg)
    monkeypatch.setenv("GEMATRIA_DSN", "postgresql://test")

    # Mock connection context manager
    mock_cur = Mock()
    mock_cur.fetchone.side_effect = [
        (True,),  # Table exists
        (7, 100, 10000),  # window_days, max_requests, max_tokens
    ]
    mock_conn = Mock()
    mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cur)
    mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
    mock_psycopg.connect.return_value.__enter__ = Mock(return_value=mock_conn)
    mock_psycopg.connect.return_value.__exit__ = Mock(return_value=None)

    # Mock _query_usage_for_app to return low usage
    monkeypatch.setattr(lm_budget, "_query_usage_for_app", lambda app, days: (10, 1000))

    allowed = lm_budget.check_lm_budget("test-app", tokens=100)
    assert allowed is True


def test_check_lm_budget_exceeded_requests_returns_false(monkeypatch):
    """If request limit exceeded, return False."""
    # Mock psycopg to be available
    mock_psycopg = Mock()
    monkeypatch.setattr("pmagent.runtime.lm_budget.psycopg", mock_psycopg)
    monkeypatch.setenv("GEMATRIA_DSN", "postgresql://test")

    # Mock connection context manager
    mock_cur = Mock()
    mock_cur.fetchone.side_effect = [
        (True,),  # Table exists
        (7, 100, 10000),  # window_days, max_requests, max_tokens
    ]
    mock_conn = Mock()
    mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cur)
    mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
    mock_psycopg.connect.return_value.__enter__ = Mock(return_value=mock_conn)
    mock_psycopg.connect.return_value.__exit__ = Mock(return_value=None)

    # Mock _query_usage_for_app to return exceeded requests
    monkeypatch.setattr(lm_budget, "_query_usage_for_app", lambda app, days: (100, 1000))

    allowed = lm_budget.check_lm_budget("test-app", tokens=100)
    assert allowed is False


def test_check_lm_budget_exceeded_tokens_returns_false(monkeypatch):
    """If token limit exceeded, return False."""
    # Mock psycopg to be available
    mock_psycopg = Mock()
    monkeypatch.setattr("pmagent.runtime.lm_budget.psycopg", mock_psycopg)
    monkeypatch.setenv("GEMATRIA_DSN", "postgresql://test")

    # Mock connection context manager
    mock_cur = Mock()
    mock_cur.fetchone.side_effect = [
        (True,),  # Table exists
        (7, 100, 10000),  # window_days, max_requests, max_tokens
    ]
    mock_conn = Mock()
    mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cur)
    mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
    mock_psycopg.connect.return_value.__enter__ = Mock(return_value=mock_conn)
    mock_psycopg.connect.return_value.__exit__ = Mock(return_value=None)

    # Mock _query_usage_for_app to return exceeded tokens
    monkeypatch.setattr(lm_budget, "_query_usage_for_app", lambda app, days: (10, 10000))

    # Try to use 100 more tokens (would exceed limit)
    allowed = lm_budget.check_lm_budget("test-app", tokens=100)
    assert allowed is False


def test_guarded_lm_call_respects_budget(monkeypatch):
    """If budget is exceeded, guarded_lm_call should skip LM Studio and use fallback."""
    # Mock budget check to return False (exceeded) - need to mock where it's imported
    monkeypatch.setattr("pmagent.runtime.lm_logging.check_lm_budget", lambda app_name, tokens=None: False)
    monkeypatch.setenv("LM_STUDIO_ENABLED", "true")

    # Mock _write_agent_run to avoid DB calls
    with patch("pmagent.runtime.lm_logging._write_agent_run", return_value=None):
        # Create a fallback function
        def fallback_fn(messages: list[dict[str, str]], kwargs: dict[str, Any]) -> dict[str, Any]:
            return {
                "ok": True,
                "response": {"model": "fallback", "content": "fallback response"},
            }

        # guarded_lm_call should call fallback when budget is exceeded
        result = guarded_lm_call(
            call_site="test.generate_text",
            messages=[{"role": "user", "content": "hello"}],
            fallback_fn=fallback_fn,
            app_name="test-app",
        )

        # When budget exceeded and fallback provided, mode is "budget_exceeded"
        assert result["mode"] == "budget_exceeded"
        assert result["ok"] is True  # Fallback succeeded
        assert result["reason"] == "budget_exceeded"


def test_guarded_lm_call_within_budget_uses_lm_studio(monkeypatch):
    """If budget is OK, guarded_lm_call should use LM Studio."""
    # Mock budget check to return True (within budget)
    monkeypatch.setattr(lm_budget, "check_lm_budget", lambda app_name, tokens=None: True)
    monkeypatch.setenv("LM_STUDIO_ENABLED", "true")

    # Mock lm_studio_chat_with_logging to return success
    mock_result = {
        "ok": True,
        "mode": "lm_on",
        "response": {"model": "lm_studio", "content": "LM response"},
    }

    with patch("pmagent.runtime.lm_logging.lm_studio_chat_with_logging", return_value=mock_result):
        result = guarded_lm_call(
            call_site="test.generate_text",
            messages=[{"role": "user", "content": "hello"}],
            app_name="test-app",
        )

        assert result["mode"] == "lm_on"
        assert result["ok"] is True
        assert result["call_site"] == "test.generate_text"


def test_lm_budget_export_file(tmp_path: Path, monkeypatch):
    """
    Smoke test: the budget export script should write a valid JSON file with
    the expected top-level shape (list or dict with budgets array).
    """
    output = tmp_path / "lm_budget_7d.json"

    def _fake_output_path() -> Path:
        return output

    # Import the export module
    import scripts.db.control_lm_budget_export as export_mod  # type: ignore[import]

    # Mock the output path
    monkeypatch.setattr(export_mod, "OUT_BUDGET_PATH", output)

    # Mock DB to return empty budgets (db_off behavior)
    monkeypatch.setattr(export_mod, "psycopg", None)

    # Run export
    export_mod.main()

    # Verify file exists and is valid JSON
    assert output.exists()
    data = json.loads(output.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert "schema" in data
    assert "budgets" in data
    assert isinstance(data["budgets"], list)
