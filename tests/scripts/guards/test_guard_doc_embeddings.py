"""Tests for scripts/guards/guard_doc_embeddings.py"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from scripts.guards import guard_doc_embeddings as mod


def test_guard_db_off_tolerant(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that guard is DB-off tolerant."""

    # Mock get_control_engine to raise an exception
    def mock_get_engine():
        raise RuntimeError("DB unavailable")

    monkeypatch.setattr("scripts.guards.guard_doc_embeddings.get_control_engine", mock_get_engine)

    result = mod.main()
    # Should exit 0 (HINT mode) even when DB is off
    assert result == 0


def test_guard_strict_mode_fails_on_missing_embeddings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that STRICT mode fails when fragments lack embeddings."""

    # Mock DB connection
    mock_conn = MagicMock()
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn

    # Mock query result: 1 doc, 10 fragments, only 5 have embeddings
    mock_rows = [
        ("doc1", "AGENTS_ROOT", 10, 5),  # 10 fragments, 5 with embeddings
    ]
    mock_conn.execute.return_value.fetchall.return_value = mock_rows

    monkeypatch.setattr(
        "scripts.guards.guard_doc_embeddings.get_control_engine", lambda: mock_engine
    )
    monkeypatch.setenv("STRICT_MODE", "1")

    result = mod.main()
    # Should exit 1 in STRICT mode when embeddings are incomplete
    assert result == 1


def test_guard_hint_mode_allows_missing_embeddings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that HINT mode allows missing embeddings."""

    # Mock DB connection
    mock_conn = MagicMock()
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn

    # Mock query result: 1 doc, 10 fragments, only 5 have embeddings
    mock_rows = [
        ("doc1", "AGENTS_ROOT", 10, 5),  # 10 fragments, 5 with embeddings
    ]
    mock_conn.execute.return_value.fetchall.return_value = mock_rows

    monkeypatch.setattr(
        "scripts.guards.guard_doc_embeddings.get_control_engine", lambda: mock_engine
    )
    monkeypatch.delenv("STRICT_MODE", raising=False)

    result = mod.main()
    # Should exit 0 in HINT mode even when embeddings are incomplete
    assert result == 0


def test_guard_all_embeddings_present(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that guard passes when all fragments have embeddings."""

    # Mock DB connection
    mock_conn = MagicMock()
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn

    # Mock query result: 1 doc, 10 fragments, all 10 have embeddings
    mock_rows = [
        ("doc1", "AGENTS_ROOT", 10, 10),  # 10 fragments, 10 with embeddings
    ]
    mock_conn.execute.return_value.fetchall.return_value = mock_rows

    monkeypatch.setattr(
        "scripts.guards.guard_doc_embeddings.get_control_engine", lambda: mock_engine
    )

    result = mod.main()
    # Should exit 0 when all embeddings are present
    assert result == 0


def test_guard_no_agents_docs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that guard passes when no AGENTS docs exist."""

    # Mock DB connection
    mock_conn = MagicMock()
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn

    # Mock query result: no docs
    mock_conn.execute.return_value.fetchall.return_value = []

    monkeypatch.setattr(
        "scripts.guards.guard_doc_embeddings.get_control_engine", lambda: mock_engine
    )

    result = mod.main()
    # Should exit 0 when no docs to check
    assert result == 0
