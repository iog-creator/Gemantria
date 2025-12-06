#!/usr/bin/env python3
"""
Tests for LM routing integration in enrichment pipeline.

Phase-3C P1b: Verifies that enrichment pipeline uses LM routing bridge
and control-plane logging correctly.
"""

from __future__ import annotations

from unittest.mock import patch
from types import SimpleNamespace

from src.services.lm_routing_bridge import chat_completion_with_routing


@patch("src.services.lm_routing_bridge.select_lm_backend")
@patch("src.services.lm_routing_bridge.lm_studio_chat_with_logging")
def test_chat_completion_with_routing_lm_studio_success(mock_logging, mock_select):
    """Test successful LM Studio routing with control-plane logging."""
    mock_select.return_value = "lm_studio"
    mock_logging.return_value = {
        "ok": True,
        "mode": "lm_on",
        "response": {
            "choices": [{"message": {"content": '{"insight": "test", "confidence": 0.95}'}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20},
        },
    }

    messages_batch = [[{"role": "user", "content": "test"}]]
    results = chat_completion_with_routing(messages_batch, model="test-model", temperature=0.0)

    assert len(results) == 1
    assert results[0].text == '{"insight": "test", "confidence": 0.95}'
    mock_select.assert_called_once_with(prefer_local=True)
    mock_logging.assert_called_once()


@patch("src.services.lm_routing_bridge.select_lm_backend")
@patch("src.services.lm_routing_bridge.lm_studio_chat_with_logging")
@patch("src.services.lmstudio_client.chat_completion")
def test_chat_completion_with_routing_lm_studio_fallback(mock_legacy, mock_logging, mock_select):
    """Test fallback to legacy chat_completion when LM Studio unavailable."""
    mock_select.return_value = "lm_studio"
    mock_logging.return_value = {
        "ok": False,
        "mode": "lm_off",
        "reason": "connection_error",
        "response": None,
    }
    mock_legacy.return_value = [SimpleNamespace(text='{"insight": "fallback", "confidence": 0.90}')]

    messages_batch = [[{"role": "user", "content": "test"}]]
    results = chat_completion_with_routing(messages_batch, model="test-model", temperature=0.0)

    assert len(results) == 1
    assert results[0].text == '{"insight": "fallback", "confidence": 0.90}'
    mock_select.assert_called_once_with(prefer_local=True)
    mock_logging.assert_called_once()
    mock_legacy.assert_called_once()


@patch("src.services.lm_routing_bridge.select_lm_backend")
@patch("src.services.lmstudio_client.chat_completion")
def test_chat_completion_with_routing_remote_backend(mock_legacy, mock_select):
    """Test remote backend routing falls back to legacy chat_completion."""
    mock_select.return_value = "remote"
    mock_legacy.return_value = [SimpleNamespace(text='{"insight": "remote", "confidence": 0.85}')]

    messages_batch = [[{"role": "user", "content": "test"}]]
    results = chat_completion_with_routing(messages_batch, model="test-model", temperature=0.0)

    assert len(results) == 1
    assert results[0].text == '{"insight": "remote", "confidence": 0.85}'
    mock_select.assert_called_once_with(prefer_local=True)
    mock_legacy.assert_called_once()


@patch("src.services.lm_routing_bridge.select_lm_backend")
@patch("src.services.lm_routing_bridge.lm_studio_chat_with_logging")
def test_chat_completion_with_routing_batch(mock_logging, mock_select):
    """Test batch processing with multiple messages."""
    mock_select.return_value = "lm_studio"
    mock_logging.side_effect = [
        {
            "ok": True,
            "mode": "lm_on",
            "response": {
                "choices": [{"message": {"content": '{"insight": "test1", "confidence": 0.95}'}}],
            },
        },
        {
            "ok": True,
            "mode": "lm_on",
            "response": {
                "choices": [{"message": {"content": '{"insight": "test2", "confidence": 0.90}'}}],
            },
        },
    ]

    messages_batch = [
        [{"role": "user", "content": "test1"}],
        [{"role": "user", "content": "test2"}],
    ]
    results = chat_completion_with_routing(messages_batch, model="test-model", temperature=0.0)

    assert len(results) == 2
    assert results[0].text == '{"insight": "test1", "confidence": 0.95}'
    assert results[1].text == '{"insight": "test2", "confidence": 0.90}'
    assert mock_logging.call_count == 2
