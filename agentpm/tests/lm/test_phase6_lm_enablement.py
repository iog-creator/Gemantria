#!/usr/bin/env python3
"""
Phase-6 LM Studio Enablement Tests

Tests for LM_STUDIO_ENABLED flag and guarded_lm_call() wrapper.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from agentpm.runtime.lm_helpers import generate_text
from agentpm.runtime.lm_logging import guarded_lm_call
from scripts.config.env import get_lm_studio_enabled


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("true", True),
        ("TRUE", True),
        ("1", True),
        ("yes", True),
        ("false", False),
        ("FALSE", False),
        ("0", False),
        ("", False),
        (None, False),
    ],
)
def test_lm_studio_enabled_env(monkeypatch, value, expected):
    """Test that get_lm_studio_enabled() correctly parses LM_STUDIO_ENABLED env var."""
    if value is None:
        monkeypatch.delenv("LM_STUDIO_ENABLED", raising=False)
    else:
        monkeypatch.setenv("LM_STUDIO_ENABLED", value)

    result = get_lm_studio_enabled()
    assert result is expected


def test_guarded_lm_call_uses_fallback_when_disabled(monkeypatch):
    """Test that guarded_lm_call() uses fallback when LM_STUDIO_ENABLED=false."""
    monkeypatch.setenv("LM_STUDIO_ENABLED", "false")

    fallback_client = Mock()
    fallback_client.return_value = {"ok": True, "response": {"text": "fallback response"}}

    def fallback_fn(messages, kwargs):
        return {"ok": True, "response": {"text": "fallback response"}}

    result = guarded_lm_call(
        call_site="test.feature",
        messages=[{"role": "user", "content": "hello"}],
        fallback_fn=fallback_fn,
    )

    assert result["mode"] == "fallback"
    assert result["reason"] == "lm_studio_disabled"
    assert result["ok"] is True
    assert result["response"]["text"] == "fallback response"
    assert result["call_site"] == "test.feature"


@patch("agentpm.runtime.lm_logging.lm_studio_chat_with_logging")
def test_guarded_lm_call_uses_lm_studio_when_enabled(mock_logging, monkeypatch):
    """Test that guarded_lm_call() uses LM Studio when LM_STUDIO_ENABLED=true."""
    monkeypatch.setenv("LM_STUDIO_ENABLED", "true")

    mock_logging.return_value = {
        "ok": True,
        "mode": "lm_on",
        "response": {
            "choices": [{"message": {"content": "lm-studio response"}}],
        },
    }

    def fallback_fn(messages, kwargs):
        return {"ok": False, "response": None}

    result = guarded_lm_call(
        call_site="test.feature",
        messages=[{"role": "user", "content": "hello"}],
        fallback_fn=fallback_fn,
    )

    mock_logging.assert_called_once()
    assert result["ok"] is True
    assert result["mode"] == "lm_on"
    assert result["call_site"] == "test.feature"


@patch("agentpm.runtime.lm_logging.lm_studio_chat_with_logging")
def test_guarded_lm_call_fallback_on_lm_studio_failure(mock_logging, monkeypatch):
    """Test that guarded_lm_call() falls back when LM Studio call fails."""
    monkeypatch.setenv("LM_STUDIO_ENABLED", "true")

    mock_logging.return_value = {
        "ok": False,
        "mode": "lm_off",
        "reason": "connection_error",
    }

    def fallback_fn(messages, kwargs):
        return {"ok": True, "response": {"text": "fallback on error"}}

    result = guarded_lm_call(
        call_site="test.feature",
        messages=[{"role": "user", "content": "hello"}],
        fallback_fn=fallback_fn,
    )

    mock_logging.assert_called_once()
    assert result["mode"] == "fallback"
    assert result["reason"] == "connection_error"
    assert result["ok"] is True
    assert result["response"]["text"] == "fallback on error"


def test_generate_text_disabled(monkeypatch):
    """Test generate_text() when LM_STUDIO_ENABLED=false."""
    monkeypatch.setenv("LM_STUDIO_ENABLED", "false")

    result = generate_text("test prompt")

    # When disabled, guarded_lm_call() uses fallback, which returns mode="fallback"
    assert result["ok"] is False
    assert result["mode"] == "fallback"
    assert result["text"] is None
    assert result["call_site"] == "lm_helpers.generate_text"


@patch("agentpm.runtime.lm_logging.lm_studio_chat_with_logging")
def test_generate_text_enabled(mock_logging, monkeypatch):
    """Test generate_text() when LM_STUDIO_ENABLED=true."""
    monkeypatch.setenv("LM_STUDIO_ENABLED", "true")

    mock_logging.return_value = {
        "ok": True,
        "mode": "lm_on",
        "response": {
            "choices": [{"message": {"content": "generated text"}}],
        },
    }

    result = generate_text("test prompt", max_tokens=128, temperature=0.5)

    mock_logging.assert_called_once()
    assert result["ok"] is True
    assert result["mode"] == "lm_on"
    assert result["text"] == "generated text"
    assert result["call_site"] == "lm_helpers.generate_text"
