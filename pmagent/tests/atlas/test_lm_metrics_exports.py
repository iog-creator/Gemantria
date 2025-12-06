#!/usr/bin/env python3
"""
Tests for LM metrics exports (Phase-3D D1).

Verifies that LM usage and health exports work correctly with db_off + LM-off tolerance.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

from scripts.db.control_lm_metrics_export import (
    db_off_health_payload,
    db_off_usage_payload,
    fetch_lm_health,
    fetch_lm_usage,
)


def test_fetch_lm_usage_db_off() -> None:
    """Test LM usage export when DB is unavailable (db_off tolerance)."""
    with patch("scripts.db.control_lm_metrics_export.get_rw_dsn", return_value=None):
        result = fetch_lm_usage(window_days=7)

        assert result.ok is False
        assert result.connection_ok is False
        assert result.total_calls == 0
        assert result.error is not None
        assert "GEMATRIA_DSN not set" in result.error


def test_fetch_lm_usage_psycopg_unavailable() -> None:
    """Test LM usage export when psycopg is not available."""
    with patch("scripts.db.control_lm_metrics_export.psycopg", None):
        result = fetch_lm_usage(window_days=7)

        assert result.ok is False
        assert result.connection_ok is False
        assert result.total_calls == 0
        assert result.error is not None
        assert "psycopg not available" in result.error


def test_fetch_lm_health_db_off() -> None:
    """Test LM health export when DB is unavailable (db_off tolerance)."""
    with patch("scripts.db.control_lm_metrics_export.get_rw_dsn", return_value=None):
        result = fetch_lm_health(window_days=7)

        assert result.ok is False
        assert result.connection_ok is False
        assert result.health_score == 0.0
        assert result.success_rate == 0.0
        assert result.error is not None
        assert "GEMATRIA_DSN not set" in result.error


def test_fetch_lm_health_psycopg_unavailable() -> None:
    """Test LM health export when psycopg is not available."""
    with patch("scripts.db.control_lm_metrics_export.psycopg", None):
        result = fetch_lm_health(window_days=7)

        assert result.ok is False
        assert result.connection_ok is False
        assert result.health_score == 0.0
        assert result.error is not None
        assert "psycopg not available" in result.error


def test_fetch_lm_usage_empty_table() -> None:
    """Test LM usage export when control.agent_run table doesn't exist."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=None)
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cur)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=None)
    mock_cur.fetchone.return_value = None  # Table doesn't exist

    with patch("scripts.db.control_lm_metrics_export.get_rw_dsn", return_value="postgresql://test"):
        with patch("scripts.db.control_lm_metrics_export.psycopg.connect", return_value=mock_conn):
            result = fetch_lm_usage(window_days=7)

            assert result.ok is False
            assert result.connection_ok is False
            assert result.total_calls == 0
            assert result.error is not None
            assert "table not found" in result.error.lower()


def test_fetch_lm_health_empty_table() -> None:
    """Test LM health export when control.agent_run table doesn't exist."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=None)
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cur)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=None)
    mock_cur.fetchone.return_value = None  # Table doesn't exist

    with patch("scripts.db.control_lm_metrics_export.get_rw_dsn", return_value="postgresql://test"):
        with patch("scripts.db.control_lm_metrics_export.psycopg.connect", return_value=mock_conn):
            result = fetch_lm_health(window_days=7)

            assert result.ok is False
            assert result.connection_ok is False
            assert result.health_score == 0.0
            assert result.error is not None
            assert "table not found" in result.error.lower()


def test_fetch_lm_usage_with_data() -> None:
    """Test LM usage export with mock data."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=None)
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cur)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=None)

    # Mock table exists check
    mock_cur.fetchone.return_value = (1,)  # Table exists
    mock_cur.fetchall.return_value = [
        (
            datetime.now(UTC) - timedelta(days=1),
            "true",
            "100",
            "50",
            "30",
        ),
        (
            datetime.now(UTC) - timedelta(days=2),
            "false",
            "200",
            "100",
            "60",
        ),
    ]

    with patch("scripts.db.control_lm_metrics_export.get_rw_dsn", return_value="postgresql://test"):
        with patch("scripts.db.control_lm_metrics_export.psycopg.connect", return_value=mock_conn):
            result = fetch_lm_usage(window_days=7)

            assert result.ok is True
            assert result.connection_ok is True
            assert result.total_calls == 2
            assert result.successful_calls == 1
            assert result.failed_calls == 1
            assert result.total_tokens_prompt == 150  # 50 + 100
            assert result.total_tokens_completion == 90  # 30 + 60
            assert result.total_latency_ms == 300  # 100 + 200
            assert result.avg_latency_ms == 150.0


def test_fetch_lm_health_with_data() -> None:
    """Test LM health export with mock data."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=None)
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cur)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=None)

    # Mock table exists check
    mock_cur.fetchone.return_value = (1,)  # Table exists
    mock_cur.fetchall.return_value = [
        (
            datetime.now(UTC) - timedelta(days=1),
            "true",
            "100",
            None,
        ),
        (
            datetime.now(UTC) - timedelta(days=2),
            "false",
            "200",
            [{"type": "lm_studio_error", "reason": "connection_error"}],
        ),
    ]

    with patch("scripts.db.control_lm_metrics_export.get_rw_dsn", return_value="postgresql://test"):
        with patch("scripts.db.control_lm_metrics_export.psycopg.connect", return_value=mock_conn):
            result = fetch_lm_health(window_days=7)

            assert result.ok is True
            assert result.connection_ok is True
            assert result.success_rate == 0.5  # 1 success / 2 total
            assert result.error_rate == 0.5  # 1 failure / 2 total
            assert result.avg_latency_ms == 150.0  # (100 + 200) / 2
            assert "lm_studio_error" in result.error_types
            assert result.error_types["lm_studio_error"] == 1
            assert len(result.recent_errors) == 1


def test_db_off_payloads() -> None:
    """Test db_off payload generation."""
    usage_payload = db_off_usage_payload("test error", window_days=7)
    assert usage_payload.ok is False
    assert usage_payload.error == "test error"
    assert usage_payload.total_calls == 0

    health_payload = db_off_health_payload("test error", window_days=7)
    assert health_payload.ok is False
    assert health_payload.error == "test error"
    assert health_payload.health_score == 0.0
