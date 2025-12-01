"""Tests for Phase-3B LM health guard (Phase-3C P1: updated to use adapter)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))


class TestLmHealthGuard:
    """Test LM health guard behavior (Phase-3C P1: uses LM Studio adapter)."""

    @patch("scripts.guards.guard_lm_health.lm_studio_chat")
    @patch("scripts.guards.guard_lm_health.get_lm_studio_settings")
    def test_lm_off_connection_refused(self, mock_settings, mock_chat):
        """Test guard returns lm_off when connection is refused."""
        from scripts.guards.guard_lm_health import check_lm_health

        mock_settings.return_value = {
            "enabled": True,
            "base_url": "http://127.0.0.1:1234/v1",
            "model": "test-model",
            "api_key": None,
        }
        mock_chat.return_value = {
            "ok": False,
            "mode": "lm_off",
            "reason": "connection_error: Connection refused",
            "response": None,
        }

        result = check_lm_health()

        assert result["ok"] is False
        assert result["mode"] == "lm_off"
        assert len(result["details"]["errors"]) > 0
        assert any("connection_error" in err for err in result["details"]["errors"])

    @patch("scripts.guards.guard_lm_health.lm_studio_chat")
    @patch("scripts.guards.guard_lm_health.get_lm_studio_settings")
    def test_lm_off_timeout(self, mock_settings, mock_chat):
        """Test guard returns lm_off when request times out."""
        from scripts.guards.guard_lm_health import check_lm_health

        mock_settings.return_value = {
            "enabled": True,
            "base_url": "http://127.0.0.1:1234/v1",
            "model": "test-model",
            "api_key": None,
        }
        mock_chat.return_value = {
            "ok": False,
            "mode": "lm_off",
            "reason": "timeout: Request timed out",
            "response": None,
        }

        result = check_lm_health()

        assert result["ok"] is False
        assert result["mode"] == "lm_off"
        assert len(result["details"]["errors"]) > 0
        assert any("timeout" in err for err in result["details"]["errors"])

    @patch("scripts.guards.guard_lm_health.lm_studio_chat")
    @patch("scripts.guards.guard_lm_health.get_lm_studio_settings")
    def test_lm_ready_minimal_ok(self, mock_settings, mock_chat):
        """Test guard returns lm_ready when endpoint responds correctly."""
        from scripts.guards.guard_lm_health import check_lm_health

        mock_settings.return_value = {
            "enabled": True,
            "base_url": "http://127.0.0.1:1234/v1",
            "model": "test-model",
            "api_key": None,
        }
        mock_chat.return_value = {
            "ok": True,
            "mode": "lm_on",
            "reason": None,
            "response": {"choices": [{"message": {"content": "hi", "role": "assistant"}}]},
        }

        result = check_lm_health()

        assert result["ok"] is True
        assert result["mode"] == "lm_ready"
        assert len(result["details"]["errors"]) == 0

    @patch("scripts.guards.guard_lm_health.get_lm_studio_settings")
    def test_lm_off_disabled(self, mock_settings):
        """Test guard returns lm_off when LM Studio is disabled."""
        from scripts.guards.guard_lm_health import check_lm_health

        mock_settings.return_value = {
            "enabled": False,
            "base_url": "http://127.0.0.1:1234/v1",
            "model": None,
            "api_key": None,
        }

        result = check_lm_health()

        assert result["ok"] is False
        assert result["mode"] == "lm_off"
        assert len(result["details"]["errors"]) > 0
        assert any(
            "lm_studio_disabled_or_unconfigured" in err for err in result["details"]["errors"]
        )

    @patch("scripts.guards.guard_lm_health.lm_studio_chat")
    @patch("scripts.guards.guard_lm_health.get_lm_studio_settings")
    def test_http_error(self, mock_settings, mock_chat):
        """Test guard returns lm_off when HTTP error occurs."""
        from scripts.guards.guard_lm_health import check_lm_health

        mock_settings.return_value = {
            "enabled": True,
            "base_url": "http://127.0.0.1:1234/v1",
            "model": "test-model",
            "api_key": None,
        }
        mock_chat.return_value = {
            "ok": False,
            "mode": "lm_off",
            "reason": "http_error: 500",
            "response": None,
        }

        result = check_lm_health()

        assert result["ok"] is False
        assert result["mode"] == "lm_off"
        assert len(result["details"]["errors"]) > 0
        assert any("http_error" in err for err in result["details"]["errors"])

    @patch("scripts.guards.guard_lm_health.check_lm_health")
    def test_main_outputs_json(self, mock_check_health, capsys):
        """Test main() outputs valid JSON and exits 0."""
        import scripts.guards.guard_lm_health

        mock_check_health.return_value = {
            "ok": True,
            "mode": "lm_ready",
            "details": {
                "endpoint": "http://127.0.0.1:1234",
                "errors": [],
            },
        }

        result = scripts.guards.guard_lm_health.main()

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["ok"] is True
        assert data["mode"] == "lm_ready"
