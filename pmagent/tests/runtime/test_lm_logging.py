#!/usr/bin/env python3
"""Tests for LM Studio control-plane logging (Phase-3C P1)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from pmagent.runtime.lm_logging import (
    _write_agent_run,
    guarded_lm_call,
    lm_studio_chat_with_logging,
)


@patch("pmagent.runtime.lm_logging.lm_studio_chat")
@patch("pmagent.runtime.lm_logging._write_agent_run")
def test_lm_logging_success_db_on(mock_write, mock_chat):
    """Test successful LM call with DB available (logs to control.agent_run)."""
    mock_chat.return_value = {
        "ok": True,
        "mode": "lm_on",
        "reason": None,
        "response": {
            "choices": [{"message": {"content": "Hello"}}],
            "usage": {"prompt_tokens": 5, "completion_tokens": 1},
        },
    }
    mock_write.return_value = "test-run-id-123"

    result = lm_studio_chat_with_logging(
        messages=[{"role": "user", "content": "hi"}],
        temperature=0.0,
        max_tokens=10,
    )

    assert result["ok"] is True
    assert result["mode"] == "lm_on"

    # Verify logging was called
    assert mock_write.called
    call_args = mock_write.call_args
    assert call_args[1]["tool"] == "lm_studio"
    assert call_args[1]["args_json"]["messages"] == [{"role": "user", "content": "hi"}]
    assert call_args[1]["result_json"]["ok"] is True
    assert call_args[1]["result_json"]["mode"] == "lm_on"
    assert "latency_ms" in call_args[1]["result_json"]
    assert call_args[1]["violations_json"] == []


@patch("pmagent.runtime.lm_logging.lm_studio_chat")
@patch("pmagent.runtime.lm_logging._write_agent_run")
def test_lm_logging_failure_db_on(mock_write, mock_chat):
    """Test failed LM call with DB available (logs error to control.agent_run)."""
    mock_chat.return_value = {
        "ok": False,
        "mode": "lm_off",
        "reason": "connection_error: Connection refused",
        "response": None,
    }
    mock_write.return_value = "test-run-id-456"

    result = lm_studio_chat_with_logging(
        messages=[{"role": "user", "content": "hi"}],
    )

    assert result["ok"] is False
    assert result["mode"] == "lm_off"

    # Verify logging was called with violations
    assert mock_write.called
    call_args = mock_write.call_args
    assert call_args[1]["result_json"]["ok"] is False
    assert len(call_args[1]["violations_json"]) > 0
    assert call_args[1]["violations_json"][0]["type"] == "lm_studio_error"


@patch("pmagent.runtime.lm_logging.lm_studio_chat")
@patch("pmagent.runtime.lm_logging._write_agent_run")
def test_lm_logging_db_off(mock_write, mock_chat):
    """Test LM call when DB is unavailable (graceful no-op, call still succeeds)."""
    mock_chat.return_value = {
        "ok": True,
        "mode": "lm_on",
        "reason": None,
        "response": {"choices": [{"message": {"content": "Hello"}}]},
    }
    mock_write.return_value = None  # DB unavailable

    result = lm_studio_chat_with_logging(
        messages=[{"role": "user", "content": "hi"}],
    )

    # LM call should still succeed even if logging fails
    assert result["ok"] is True
    assert result["mode"] == "lm_on"

    # Logging should have been attempted
    assert mock_write.called


@patch("pmagent.runtime.lm_logging.lm_studio_chat")
@patch("pmagent.runtime.lm_logging.get_rw_dsn")
def test_lm_logging_no_dsn(mock_dsn, mock_chat):
    """Test LM call when no DSN is available (no logging attempt)."""
    mock_chat.return_value = {
        "ok": True,
        "mode": "lm_on",
        "reason": None,
        "response": {"choices": [{"message": {"content": "Hello"}}]},
    }
    mock_dsn.return_value = None  # No DSN available

    result = lm_studio_chat_with_logging(
        messages=[{"role": "user", "content": "hi"}],
    )

    # LM call should still succeed
    assert result["ok"] is True
    assert result["mode"] == "lm_on"


@patch("builtins.__import__")
@patch("pmagent.runtime.lm_logging.get_rw_dsn")
def test_write_agent_run_db_on(mock_dsn, mock_import):
    """Test _write_agent_run when DB is available (returns run ID)."""
    mock_dsn.return_value = "postgresql://user:pass@localhost/db"
    # Mock psycopg import
    mock_psycopg = MagicMock()
    mock_psycopg.types.json.dumps = lambda x: x  # Simple passthrough
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = ("test-run-id-789",)
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cur)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    mock_psycopg.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
    mock_psycopg.connect.return_value.__exit__ = MagicMock(return_value=False)

    def import_side_effect(name, *args, **kwargs):
        if name == "psycopg":
            return mock_psycopg
        return __import__(name, *args, **kwargs)

    mock_import.side_effect = import_side_effect

    result = _write_agent_run(
        tool="test_tool",
        args_json={"arg1": "value1"},
        result_json={"ok": True},
        violations_json=None,
    )

    assert result == "test-run-id-789"
    mock_psycopg.connect.assert_called_once()
    mock_cur.execute.assert_called_once()


@patch("pmagent.runtime.lm_logging.get_rw_dsn")
def test_write_agent_run_db_off_no_dsn(mock_dsn):
    """Test _write_agent_run when no DSN is available (returns None)."""
    mock_dsn.return_value = None

    result = _write_agent_run(
        tool="test_tool",
        args_json={"arg1": "value1"},
        result_json={"ok": True},
    )

    assert result is None


@patch("builtins.__import__")
@patch("pmagent.runtime.lm_logging.get_rw_dsn")
def test_write_agent_run_db_off_no_psycopg(mock_dsn, mock_import):
    """Test _write_agent_run when psycopg is not available (returns None)."""
    mock_dsn.return_value = "postgresql://user:pass@localhost/db"

    # Simulate ImportError by raising ImportError when psycopg is imported
    def import_side_effect(name, *args, **kwargs):
        if name == "psycopg":
            raise ImportError("No module named 'psycopg'")
        return __import__(name, *args, **kwargs)

    mock_import.side_effect = import_side_effect

    result = _write_agent_run(
        tool="test_tool",
        args_json={"arg1": "value1"},
        result_json={"ok": True},
    )

    assert result is None


@patch("builtins.__import__")
@patch("pmagent.runtime.lm_logging.get_rw_dsn")
def test_write_agent_run_db_error_graceful(mock_dsn, mock_import):
    """Test _write_agent_run when DB write fails (returns None, no exception)."""
    mock_dsn.return_value = "postgresql://user:pass@localhost/db"
    # Mock psycopg import but make connect raise an exception
    mock_psycopg = MagicMock()
    mock_psycopg.connect.side_effect = Exception("Connection failed")

    def import_side_effect(name, *args, **kwargs):
        if name == "psycopg":
            return mock_psycopg
        return __import__(name, *args, **kwargs)

    mock_import.side_effect = import_side_effect

    # Should not raise exception, should return None
    result = _write_agent_run(
        tool="test_tool",
        args_json={"arg1": "value1"},
        result_json={"ok": True},
    )

    assert result is None


@patch("pmagent.runtime.lm_logging.check_lm_budget")
@patch("pmagent.runtime.lm_logging.get_lm_studio_enabled")
@patch("pmagent.runtime.lm_logging.lm_studio_chat_with_logging")
def test_guarded_lm_call_lm_on(mock_chat, mock_enabled, mock_budget):
    """Test guarded_lm_call when LM Studio is enabled and within budget."""
    mock_enabled.return_value = True
    mock_budget.return_value = True
    mock_chat.return_value = {
        "ok": True,
        "mode": "lm_on",
        "response": {"choices": [{"message": {"content": "Hello"}}]},
    }

    result = guarded_lm_call(
        call_site="test.app",
        messages=[{"role": "user", "content": "hi"}],
    )

    assert result["ok"] is True
    assert result["mode"] == "lm_on"
    assert result["call_site"] == "test.app"
    mock_chat.assert_called_once()


@patch("pmagent.runtime.lm_logging.get_lm_studio_enabled")
def test_guarded_lm_call_lm_off(mock_enabled):
    """Test guarded_lm_call when LM Studio is disabled."""
    mock_enabled.return_value = False

    result = guarded_lm_call(
        call_site="test.app",
        messages=[{"role": "user", "content": "hi"}],
    )

    assert result["ok"] is False
    assert result["mode"] == "lm_off"
    assert result["reason"] == "lm_studio_disabled"
    assert result["call_site"] == "test.app"


@patch("pmagent.runtime.lm_logging.check_lm_budget")
@patch("pmagent.runtime.lm_logging.get_lm_studio_enabled")
@patch("pmagent.runtime.lm_logging._write_agent_run")
def test_guarded_lm_call_budget_exceeded(mock_write, mock_enabled, mock_budget):
    """Test guarded_lm_call when budget is exceeded."""
    mock_enabled.return_value = True
    mock_budget.return_value = False  # Budget exceeded
    mock_write.return_value = "test-run-id"

    result = guarded_lm_call(
        call_site="test.app",
        messages=[{"role": "user", "content": "hi"}],
    )

    assert result["ok"] is False
    assert result["mode"] == "budget_exceeded"
    assert result["reason"] == "budget_exceeded"
    assert result["call_site"] == "test.app"
    # Verify budget violation was logged
    assert mock_write.called
    call_args = mock_write.call_args
    assert call_args[1]["violations_json"][0]["type"] == "budget_exceeded"


@patch("pmagent.runtime.lm_logging.check_lm_budget")
@patch("pmagent.runtime.lm_logging.get_lm_studio_enabled")
@patch("pmagent.runtime.lm_logging.lm_studio_chat_with_logging")
def test_guarded_lm_call_fallback(mock_chat, mock_enabled, mock_budget):
    """Test guarded_lm_call when LM Studio fails and fallback is provided."""
    mock_enabled.return_value = True
    mock_budget.return_value = True
    mock_chat.return_value = {
        "ok": False,
        "mode": "lm_off",
        "reason": "connection_error",
    }

    def fallback_fn(messages, kwargs):
        return {"ok": True, "response": {"text": "fallback response"}}

    result = guarded_lm_call(
        call_site="test.app",
        messages=[{"role": "user", "content": "hi"}],
        fallback_fn=fallback_fn,
    )

    assert result["ok"] is True
    assert result["mode"] == "fallback"
    assert result["reason"] == "connection_error"
    assert result["call_site"] == "test.app"
