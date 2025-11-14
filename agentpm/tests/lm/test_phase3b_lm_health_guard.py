"""Tests for Phase-3B LM health guard."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import requests

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))


class TestLmHealthGuard:
    """Test LM health guard behavior."""

    @patch("scripts.guards.guard_lm_health.requests.post")
    @patch("scripts.guards.guard_lm_health.get_lm_studio_endpoint")
    def test_lm_off_connection_refused(self, mock_get_endpoint, mock_post):
        """Test guard returns lm_off when connection is refused."""
        from scripts.guards.guard_lm_health import check_lm_health

        mock_get_endpoint.return_value = "http://127.0.0.1:1234"
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")

        result = check_lm_health()

        assert result["ok"] is False
        assert result["mode"] == "lm_off"
        assert len(result["details"]["errors"]) > 0
        assert any("connection_refused" in err for err in result["details"]["errors"])

    @patch("scripts.guards.guard_lm_health.requests.post")
    @patch("scripts.guards.guard_lm_health.get_lm_studio_endpoint")
    def test_lm_off_timeout(self, mock_get_endpoint, mock_post):
        """Test guard returns lm_off when request times out."""
        from scripts.guards.guard_lm_health import check_lm_health

        mock_get_endpoint.return_value = "http://127.0.0.1:1234"
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")

        result = check_lm_health()

        assert result["ok"] is False
        assert result["mode"] == "lm_off"
        assert len(result["details"]["errors"]) > 0
        assert any("timeout" in err for err in result["details"]["errors"])

    @patch("scripts.guards.guard_lm_health.requests.post")
    @patch("scripts.guards.guard_lm_health.get_lm_studio_endpoint")
    def test_lm_ready_minimal_ok(self, mock_get_endpoint, mock_post):
        """Test guard returns lm_ready when endpoint responds correctly."""
        from scripts.guards.guard_lm_health import check_lm_health

        mock_get_endpoint.return_value = "http://127.0.0.1:1234"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"message": {"content": "hi", "role": "assistant"}}]}
        mock_post.return_value = mock_response

        result = check_lm_health()

        assert result["ok"] is True
        assert result["mode"] == "lm_ready"
        assert len(result["details"]["errors"]) == 0

    @patch("scripts.guards.guard_lm_health.requests.post")
    @patch("scripts.guards.guard_lm_health.get_lm_studio_endpoint")
    def test_invalid_response(self, mock_get_endpoint, mock_post):
        """Test guard returns lm_off when response is invalid."""
        from scripts.guards.guard_lm_health import check_lm_health

        mock_get_endpoint.return_value = "http://127.0.0.1:1234"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"unexpected": "structure"}
        mock_post.return_value = mock_response

        result = check_lm_health()

        assert result["ok"] is False
        assert result["mode"] == "lm_off"
        assert len(result["details"]["errors"]) > 0
        assert any("invalid_response" in err for err in result["details"]["errors"])

    @patch("scripts.guards.guard_lm_health.requests.post")
    @patch("scripts.guards.guard_lm_health.get_lm_studio_endpoint")
    def test_http_error(self, mock_get_endpoint, mock_post):
        """Test guard returns lm_off when HTTP error occurs."""
        from scripts.guards.guard_lm_health import check_lm_health

        mock_get_endpoint.return_value = "http://127.0.0.1:1234"
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

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
