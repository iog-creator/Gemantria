"""
Unit tests for confidence gates functionality.
"""

import os
from unittest.mock import MagicMock, patch

from src.nodes.enrichment import HARD, SOFT, evaluate_confidence


class TestConfidenceGates:
    """Test confidence gate evaluation logic."""

    def test_soft_hard_constants(self):
        """Test that soft/hard constants are properly set."""
        assert SOFT == 0.90
        assert HARD == 0.95

    @patch("src.nodes.enrichment.get_metrics_client")
    def test_evaluate_confidence_pass(self, mock_get_client):
        """Test confidence evaluation for passing scores."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Score above hard threshold - should pass
        result = evaluate_confidence(0.96)
        assert result == "pass"
        mock_client.emit.assert_not_called()

    @patch("src.nodes.enrichment.get_metrics_client")
    def test_evaluate_confidence_soft_warn(self, mock_get_client):
        """Test confidence evaluation for soft warning."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Score below soft but above hard - should warn
        result = evaluate_confidence(0.92)
        assert result == "warn"
        mock_client.emit.assert_called_once_with({"event": "ai_conf_soft_warn"})

    @patch("src.nodes.enrichment.get_metrics_client")
    def test_evaluate_confidence_hard_fail(self, mock_get_client):
        """Test confidence evaluation for hard failure."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Score below hard threshold - should fail
        result = evaluate_confidence(0.85)
        assert result == "fail"
        # Should emit both soft warn and hard fail
        assert mock_client.emit.call_count == 2
        calls = mock_client.emit.call_args_list
        assert calls[0][0][0]["event"] == "ai_conf_soft_warn"
        assert calls[1][0][0]["event"] == "ai_conf_hard_fail"

    @patch("src.nodes.enrichment.get_metrics_client")
    def test_evaluate_confidence_boundary_soft(self, mock_get_client):
        """Test confidence evaluation at soft threshold boundary."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Score exactly at soft threshold - should warn
        result = evaluate_confidence(0.90)
        assert result == "warn"
        mock_client.emit.assert_called_once_with({"event": "ai_conf_soft_warn"})

    @patch("src.nodes.enrichment.get_metrics_client")
    def test_evaluate_confidence_boundary_hard(self, mock_get_client):
        """Test confidence evaluation at hard threshold boundary."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Score exactly at hard threshold - should warn (not fail)
        result = evaluate_confidence(0.95)
        assert result == "warn"
        mock_client.emit.assert_called_once_with({"event": "ai_conf_soft_warn"})

    @patch.dict(
        os.environ, {"AI_CONFIDENCE_SOFT": "0.85", "AI_CONFIDENCE_HARD": "0.92"}
    )
    def test_custom_thresholds(self):
        """Test with custom environment thresholds."""
        # Reload module to pick up new env vars
        import importlib  # noqa: E402

        import src.nodes.enrichment  # noqa: E402

        importlib.reload(src.nodes.enrichment)
        from src.nodes.enrichment import HARD as new_hard  # noqa: E402
        from src.nodes.enrichment import SOFT as new_soft  # noqa: E402

        assert new_soft == 0.85
        assert new_hard == 0.92
