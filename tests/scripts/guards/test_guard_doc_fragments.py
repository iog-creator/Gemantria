"""Tests for scripts/guards/guard_doc_fragments.py"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from scripts.guards import guard_doc_fragments as mod


def test_guard_db_off_tolerant(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that guard is DB-off tolerant."""

    # Mock get_control_engine to raise an exception
    def mock_get_engine():
        raise RuntimeError("DB unavailable")

    monkeypatch.setattr("scripts.guards.guard_doc_fragments.get_control_engine", mock_get_engine)

    result = mod.main()
    # Should exit 0 (HINT mode) even when DB is off
    assert result == 0


def test_guard_strict_mode_fails_on_missing_fragments(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that STRICT mode fails when AGENTS docs have zero fragments."""
    # Mock DB connection
    mock_conn = MagicMock()
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn

    # Mock query results: 2 AGENTS docs, one with fragments, one without
    mock_conn.execute.return_value.fetchall.side_effect = [
        [("doc1", "AGENTS_ROOT"), ("doc2", "AGENTS::test")],  # AGENTS docs
        [(5,)],  # doc1 has 5 fragments
        [(0,)],  # doc2 has 0 fragments
    ]

    monkeypatch.setattr(
        "scripts.guards.guard_doc_fragments.get_control_engine", lambda: mock_engine
    )
    monkeypatch.setenv("STRICT_MODE", "1")

    result = mod.main()
    # Should exit 1 in STRICT mode when fragments are missing
    assert result == 1


def test_guard_hint_mode_passes_on_missing_fragments(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that HINT mode passes even when AGENTS docs have zero fragments."""
    # Mock DB connection
    mock_conn = MagicMock()
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn

    # Mock query results: 1 AGENTS doc with 0 fragments
    mock_conn.execute.return_value.fetchall.side_effect = [
        [("doc1", "AGENTS_ROOT")],  # AGENTS docs
        [(0,)],  # doc1 has 0 fragments
    ]

    monkeypatch.setattr(
        "scripts.guards.guard_doc_fragments.get_control_engine", lambda: mock_engine
    )
    # Don't set STRICT_MODE (defaults to HINT)

    result = mod.main()
    # Should exit 0 in HINT mode even when fragments are missing
    assert result == 0


def test_guard_outputs_json(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that guard outputs valid JSON."""
    # Mock DB connection
    mock_conn = MagicMock()
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn

    # Mock query results: no AGENTS docs
    mock_conn.execute.return_value.fetchall.return_value = []

    monkeypatch.setattr(
        "scripts.guards.guard_doc_fragments.get_control_engine", lambda: mock_engine
    )

    mod.main()
    output = capsys.readouterr().out
    # Should output valid JSON
    verdict = json.loads(output)
    assert "ok" in verdict
    assert "mode" in verdict
    assert "reason" in verdict
    assert "stats" in verdict
