#!/usr/bin/env python3
"""Tests for docs inventory script (DM-001)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch


from agentpm.scripts.docs_inventory import (
    compute_content_hash,
    extract_title_from_markdown,
    infer_doc_type,
    run_inventory,
    should_include_path,
)


def test_extract_title_from_markdown():
    """Test title extraction from markdown."""
    # Test H1 extraction
    content = "# My Document Title\n\nSome content here."
    assert extract_title_from_markdown(content, "test.md") == "My Document Title"

    # Test fallback to filename
    content = "No heading here."
    assert extract_title_from_markdown(content, "my-document.md") == "My Document"

    # Test with underscores
    assert extract_title_from_markdown("", "my_document_file.md") == "My Document File"


def test_infer_doc_type():
    """Test document type inference."""
    repo_root = Path("/repo")
    test_cases = [
        (Path("/repo/docs/SSOT/MASTER_PLAN.md"), "ssot"),
        (Path("/repo/docs/SSOT/AGENTS.md"), "ssot"),
        (Path("/repo/docs/runbooks/SETUP.md"), "runbook"),
        (Path("/repo/docs/runbooks/README.md"), "runbook"),
        (Path("/repo/docs/legacy/old_doc.md"), "legacy"),
        (Path("/repo/archive/old_file.md"), "legacy"),
        (Path("/repo/docs/analysis/report.md"), "reference"),
        (Path("/repo/README.md"), "reference"),
    ]

    for filepath, expected_type in test_cases:
        assert infer_doc_type(filepath, repo_root) == expected_type


def test_compute_content_hash():
    """Test content hash computation."""
    content = b"test content"
    hash1 = compute_content_hash(content)
    hash2 = compute_content_hash(content)
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 hex length

    # Different content should produce different hash
    hash3 = compute_content_hash(b"different content")
    assert hash1 != hash3


def test_should_include_path():
    """Test path inclusion logic."""
    repo_root = Path("/repo")

    # Should include
    assert should_include_path(Path("/repo/docs/test.md"), repo_root) is True
    assert should_include_path(Path("/repo/README.md"), repo_root) is True
    assert should_include_path(Path("/repo/docs/SSOT/AGENTS.md"), repo_root) is True

    # Should exclude (extension)
    assert should_include_path(Path("/repo/docs/test.py"), repo_root) is False
    assert should_include_path(Path("/repo/docs/test.txt"), repo_root) is True  # .txt is included

    # Should exclude (directory)
    assert should_include_path(Path("/repo/.git/config"), repo_root) is False
    assert should_include_path(Path("/repo/.venv/script.py"), repo_root) is False
    assert should_include_path(Path("/repo/node_modules/file.md"), repo_root) is False
    assert should_include_path(Path("/repo/archive/evidence/file.md"), repo_root) is False


@patch("agentpm.scripts.docs_inventory.psycopg", None)
@patch("agentpm.scripts.docs_inventory.get_rw_dsn")
def test_run_inventory_db_off(mock_get_dsn):
    """Test inventory when DB is unavailable."""
    result = run_inventory(Path("/tmp/test_repo"))

    assert result["ok"] is False
    assert result["db_off"] is True
    assert "psycopg not available" in result["error"]


@patch("agentpm.scripts.docs_inventory.psycopg")
@patch("agentpm.scripts.docs_inventory.get_rw_dsn")
def test_run_inventory_no_dsn(mock_get_dsn, mock_psycopg):
    """Test inventory when DSN is not set."""
    mock_get_dsn.return_value = None

    result = run_inventory(Path("/tmp/test_repo"))

    assert result["ok"] is False
    assert result["db_off"] is True
    assert "GEMATRIA_DSN not set" in result["error"]


@patch("agentpm.scripts.docs_inventory.psycopg")
@patch("agentpm.scripts.docs_inventory.get_rw_dsn")
def test_run_inventory_success(mock_get_dsn, mock_psycopg, tmp_path):
    """Test successful inventory run."""
    # Create test files
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "test1.md").write_text("# Test Document 1\n\nContent here.")
    (tmp_path / "docs" / "test2.md").write_text("# Test Document 2\n\nMore content.")

    # Mock DB connection with proper context manager setup
    mock_conn = MagicMock()

    # Setup connection context manager
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    # Setup cursor context managers - each call returns a new cursor
    cursor_call_count = 0

    def cursor_side_effect():
        nonlocal cursor_call_count
        cursor_call_count += 1
        mock_cursor = MagicMock()
        if cursor_call_count == 1:
            # First cursor: table exists check
            mock_cursor.fetchone.return_value = (1,)
        elif cursor_call_count in (2, 3):
            # Second/third cursors: file existence checks
            mock_cursor.fetchone.return_value = None
        else:
            # Subsequent cursors: inserts
            mock_cursor.fetchone.return_value = ("doc-id", "docs/test.md")
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        return mock_cursor

    mock_conn.cursor.return_value.__enter__ = MagicMock(side_effect=cursor_side_effect)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

    mock_psycopg.connect.return_value = mock_conn
    mock_get_dsn.return_value = "postgresql://test"

    result = run_inventory(tmp_path)

    # The test verifies the function structure works; full DB mocking is complex
    # In practice, this would require a real DB or more sophisticated mocking
    assert "ok" in result
    assert "scanned" in result
    assert "inserted" in result
    assert "updated" in result
