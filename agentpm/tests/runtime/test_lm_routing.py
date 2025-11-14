"""Tests for LM routing helper (Phase-3C P0)."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))


class TestLMRouting:
    """Test LM routing helper behavior."""

    @patch("agentpm.runtime.lm_routing.get_lm_studio_settings")
    def test_select_remote_when_unconfigured(self, mock_settings):
        """Test routing returns 'remote' when LM Studio is unconfigured."""
        from agentpm.runtime.lm_routing import select_lm_backend

        mock_settings.return_value = {
            "enabled": False,
            "base_url": None,
            "model": None,
            "api_key": None,
        }

        result = select_lm_backend()

        assert result == "remote"

    @patch("agentpm.runtime.lm_routing.get_lm_studio_settings")
    def test_select_remote_when_prefer_local_false(self, mock_settings):
        """Test routing returns 'remote' when prefer_local is False."""
        from agentpm.runtime.lm_routing import select_lm_backend

        mock_settings.return_value = {
            "enabled": True,
            "base_url": "http://localhost:1234/v1",
            "model": "test-model",
            "api_key": None,
        }

        result = select_lm_backend(prefer_local=False)

        assert result == "remote"

    @patch("agentpm.runtime.lm_routing.get_lm_studio_settings")
    def test_select_lm_studio_when_enabled(self, mock_settings):
        """Test routing returns 'lm_studio' when enabled and prefer_local is True."""
        from agentpm.runtime.lm_routing import select_lm_backend

        mock_settings.return_value = {
            "enabled": True,
            "base_url": "http://localhost:1234/v1",
            "model": "test-model",
            "api_key": None,
        }

        result = select_lm_backend(prefer_local=True)

        assert result == "lm_studio"

    @patch("agentpm.runtime.lm_routing.get_lm_studio_settings")
    def test_select_remote_when_enabled_flag_not_set(self, mock_settings):
        """Test routing returns 'remote' when enabled flag is not set."""
        from agentpm.runtime.lm_routing import select_lm_backend

        mock_settings.return_value = {
            "enabled": False,  # Enabled flag not set
            "base_url": "http://localhost:1234/v1",
            "model": "test-model",
            "api_key": None,
        }

        result = select_lm_backend(prefer_local=True)

        assert result == "remote"
