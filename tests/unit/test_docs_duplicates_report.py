#!/usr/bin/env python3
"""Tests for docs duplicates report script (DM-001)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch


from agentpm.scripts.docs_duplicates_report import generate_duplicates_report
from datetime import UTC


@patch("agentpm.scripts.docs_duplicates_report.psycopg", None)
@patch("agentpm.scripts.docs_duplicates_report.get_rw_dsn")
def test_generate_duplicates_report_db_off(mock_get_dsn, tmp_path):
    """Test duplicates report when DB is unavailable."""
    result = generate_duplicates_report(tmp_path / "report.md")

    assert result["ok"] is False
    assert result["db_off"] is True
    assert "psycopg not available" in result["error"]


@patch("agentpm.scripts.docs_duplicates_report.psycopg")
@patch("agentpm.scripts.docs_duplicates_report.get_rw_dsn")
def test_generate_duplicates_report_no_duplicates(mock_get_dsn, mock_psycopg, tmp_path):
    """Test duplicates report when no duplicates exist."""
    # Mock DB connection
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cur)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    # Mock table exists check
    mock_cur.fetchone.return_value = (1,)
    # Mock no duplicates query
    mock_cur.fetchall.return_value = []

    mock_psycopg.connect.return_value = mock_conn
    mock_get_dsn.return_value = "postgresql://test"

    output_path = tmp_path / "report.md"
    result = generate_duplicates_report(output_path)

    assert result["ok"] is True
    assert result["exact_duplicates"] == 0
    assert len(result["duplicate_groups"]) == 0
    assert output_path.exists()

    # Check report content
    content = output_path.read_text()
    assert "No exact duplicates found" in content


@patch("agentpm.scripts.docs_duplicates_report.psycopg")
@patch("agentpm.scripts.docs_duplicates_report.get_rw_dsn")
def test_generate_duplicates_report_with_duplicates(mock_get_dsn, mock_psycopg, tmp_path):
    """Test duplicates report with duplicate documents."""
    from datetime import datetime

    # Mock DB connection
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cur)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    # Mock table exists check
    mock_cur.fetchone.side_effect = [
        (1,),  # Table exists
    ]

    # Mock duplicate groups query
    hash1 = "abc123" * 10  # 60 chars, pad to 64
    hash1 = hash1[:64]
    mock_cur.fetchall.side_effect = [
        [(hash1, ["docs/test1.md", "docs/test2.md"], 2)],  # Duplicate group query
        [  # File details query
            ("docs/test1.md", "Test Document 1", "reference", 100, datetime.now(UTC), "unreviewed"),
            ("docs/test2.md", "Test Document 2", "reference", 100, datetime.now(UTC), "unreviewed"),
        ],
    ]

    mock_psycopg.connect.return_value = mock_conn
    mock_get_dsn.return_value = "postgresql://test"

    output_path = tmp_path / "report.md"
    result = generate_duplicates_report(output_path)

    assert result["ok"] is True
    assert result["exact_duplicates"] == 2
    assert len(result["duplicate_groups"]) == 1
    assert output_path.exists()

    # Check report content
    content = output_path.read_text()
    assert "Duplicate Group 1" in content
    assert "docs/test1.md" in content
    assert "docs/test2.md" in content
    assert hash1 in content
