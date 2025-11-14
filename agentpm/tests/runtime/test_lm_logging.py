#!/usr/bin/env python3
"""Tests for LM Studio control-plane logging (Phase-3C P1)."""

from __future__ import annotations

from unittest.mock import patch

from agentpm.runtime.lm_logging import lm_studio_chat_with_logging


@patch("agentpm.runtime.lm_logging.lm_studio_chat")
@patch("agentpm.runtime.lm_logging._write_agent_run")
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


@patch("agentpm.runtime.lm_logging.lm_studio_chat")
@patch("agentpm.runtime.lm_logging._write_agent_run")
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


@patch("agentpm.runtime.lm_logging.lm_studio_chat")
@patch("agentpm.runtime.lm_logging._write_agent_run")
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


@patch("agentpm.runtime.lm_logging.lm_studio_chat")
@patch("agentpm.runtime.lm_logging.get_rw_dsn")
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
