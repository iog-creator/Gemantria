"""Tests for LM Studio adapter (Phase-3C P0)."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import requests

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))


class TestLMStudioAdapter:
    """Test LM Studio adapter behavior."""

    @patch("agentpm.adapters.lm_studio.get_lm_studio_settings")
    def test_lm_off_when_unconfigured(self, mock_settings):
        """Test adapter returns lm_off when LM Studio is unconfigured."""
        from agentpm.adapters.lm_studio import lm_studio_chat

        mock_settings.return_value = {
            "enabled": False,
            "base_url": None,
            "model": None,
            "api_key": None,
        }

        result = lm_studio_chat([{"role": "user", "content": "test"}])

        assert result["ok"] is False
        assert result["mode"] == "lm_off"
        assert result["reason"] == "lm_studio_disabled_or_unconfigured"
        assert result["response"] is None

    @patch("agentpm.adapters.lm_studio.get_lm_studio_settings")
    def test_lm_off_when_enabled_flag_not_set(self, mock_settings):
        """Test adapter returns lm_off when enabled flag is not set."""
        from agentpm.adapters.lm_studio import lm_studio_chat

        mock_settings.return_value = {
            "enabled": False,
            "base_url": "http://localhost:1234/v1",
            "model": "test-model",
            "api_key": None,
        }

        result = lm_studio_chat([{"role": "user", "content": "test"}])

        assert result["ok"] is False
        assert result["mode"] == "lm_off"
        assert result["reason"] == "lm_studio_disabled_or_unconfigured"

    @patch("agentpm.adapters.lm_studio.requests.post")
    @patch("agentpm.adapters.lm_studio.get_lm_studio_settings")
    def test_lm_on_success(self, mock_settings, mock_post):
        """Test adapter returns lm_on when call succeeds."""
        from agentpm.adapters.lm_studio import lm_studio_chat

        mock_settings.return_value = {
            "enabled": True,
            "base_url": "http://localhost:1234/v1",
            "model": "test-model",
            "api_key": None,
        }

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "test response"}}],
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        result = lm_studio_chat([{"role": "user", "content": "test"}])

        assert result["ok"] is True
        assert result["mode"] == "lm_on"
        assert result["reason"] is None
        assert result["response"] is not None
        assert "choices" in result["response"]

        # Verify request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "http://localhost:1234/v1/chat/completions"
        assert call_args[1]["json"]["model"] == "test-model"
        assert call_args[1]["json"]["messages"] == [{"role": "user", "content": "test"}]

    @patch("agentpm.adapters.lm_studio.requests.post")
    @patch("agentpm.adapters.lm_studio.get_lm_studio_settings")
    def test_lm_off_connection_error(self, mock_settings, mock_post):
        """Test adapter returns lm_off on connection error."""
        from agentpm.adapters.lm_studio import lm_studio_chat

        mock_settings.return_value = {
            "enabled": True,
            "base_url": "http://localhost:1234/v1",
            "model": "test-model",
            "api_key": None,
        }

        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")

        result = lm_studio_chat([{"role": "user", "content": "test"}])

        assert result["ok"] is False
        assert result["mode"] == "lm_off"
        assert "connection_error" in result["reason"]
        assert result["response"] is None

    @patch("agentpm.adapters.lm_studio.requests.post")
    @patch("agentpm.adapters.lm_studio.get_lm_studio_settings")
    def test_lm_off_timeout(self, mock_settings, mock_post):
        """Test adapter returns lm_off on timeout."""
        from agentpm.adapters.lm_studio import lm_studio_chat

        mock_settings.return_value = {
            "enabled": True,
            "base_url": "http://localhost:1234/v1",
            "model": "test-model",
            "api_key": None,
        }

        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")

        result = lm_studio_chat([{"role": "user", "content": "test"}])

        assert result["ok"] is False
        assert result["mode"] == "lm_off"
        assert "timeout" in result["reason"]
        assert result["response"] is None

    @patch("agentpm.adapters.lm_studio.requests.post")
    @patch("agentpm.adapters.lm_studio.get_lm_studio_settings")
    def test_lm_off_http_error(self, mock_settings, mock_post):
        """Test adapter returns lm_off on HTTP error."""
        from agentpm.adapters.lm_studio import lm_studio_chat

        mock_settings.return_value = {
            "enabled": True,
            "base_url": "http://localhost:1234/v1",
            "model": "test-model",
            "api_key": None,
        }

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_post.return_value = mock_response

        result = lm_studio_chat([{"role": "user", "content": "test"}])

        assert result["ok"] is False
        assert result["mode"] == "lm_off"
        assert "http_error" in result["reason"]
        assert result["response"] is None

    @patch("agentpm.adapters.lm_studio.requests.post")
    @patch("agentpm.adapters.lm_studio.get_lm_studio_settings")
    def test_base_url_normalization(self, mock_settings, mock_post):
        """Test that base_url is normalized correctly (adds /v1 if missing)."""
        from agentpm.adapters.lm_studio import lm_studio_chat

        mock_settings.return_value = {
            "enabled": True,
            "base_url": "http://localhost:1234",  # No /v1
            "model": "test-model",
            "api_key": None,
        }

        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": []}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        lm_studio_chat([{"role": "user", "content": "test"}])

        # Verify /v1 was added
        call_args = mock_post.call_args
        assert call_args[0][0] == "http://localhost:1234/v1/chat/completions"

    @patch("agentpm.adapters.lm_studio.requests.post")
    @patch("agentpm.adapters.lm_studio.get_lm_studio_settings")
    def test_api_key_in_headers(self, mock_settings, mock_post):
        """Test that API key is included in headers when provided."""
        from agentpm.adapters.lm_studio import lm_studio_chat

        mock_settings.return_value = {
            "enabled": True,
            "base_url": "http://localhost:1234/v1",
            "model": "test-model",
            "api_key": "test-api-key",
        }

        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": []}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        lm_studio_chat([{"role": "user", "content": "test"}])

        # Verify API key in headers
        call_args = mock_post.call_args
        assert call_args[1]["headers"]["Authorization"] == "Bearer test-api-key"
