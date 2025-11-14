"""Tests for Phase-3A DB loader module."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[3]


class TestLoaderWiring:
    """Test that loader functions use DSN loaders correctly."""

    @patch("agentpm.db.loader.get_rw_dsn")
    @patch("agentpm.db.loader.create_engine")
    def test_get_control_engine_uses_dsn_loader(self, mock_create_engine, mock_get_rw_dsn):
        """Test that get_control_engine() uses get_rw_dsn()."""
        from agentpm.db.loader import get_control_engine

        # Reset engine cache
        import agentpm.db.loader

        agentpm.db.loader._control_engine = None

        mock_get_rw_dsn.return_value = "postgresql://test:test@localhost/test"
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        engine = get_control_engine()

        mock_get_rw_dsn.assert_called_once()
        mock_create_engine.assert_called_once_with(
            "postgresql://test:test@localhost/test", pool_pre_ping=True, echo=False
        )
        assert engine == mock_engine

    @patch("agentpm.db.loader.get_bible_db_dsn")
    @patch("agentpm.db.loader.create_engine")
    def test_get_bible_engine_uses_dsn_loader(self, mock_create_engine, mock_get_bible_dsn):
        """Test that get_bible_engine() uses get_bible_db_dsn()."""
        from agentpm.db.loader import get_bible_engine

        # Reset engine cache
        import agentpm.db.loader

        agentpm.db.loader._bible_engine = None

        mock_get_bible_dsn.return_value = "postgresql://test:test@localhost/bible"
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        engine = get_bible_engine()

        mock_get_bible_dsn.assert_called_once()
        mock_create_engine.assert_called_once_with(
            "postgresql://test:test@localhost/bible", pool_pre_ping=True, echo=False
        )
        assert engine == mock_engine


class TestDbOffBehavior:
    """Test DB-off behavior (connection errors, missing DSNs)."""

    @patch("agentpm.db.loader.get_rw_dsn")
    def test_fetch_graph_head_db_unavailable_no_dsn(self, mock_get_rw_dsn):
        """Test fetch_graph_head raises DbUnavailableError when DSN is None."""
        from agentpm.db.loader import DbUnavailableError, fetch_graph_head

        # Reset engine cache
        import agentpm.db.loader

        agentpm.db.loader._control_engine = None

        mock_get_rw_dsn.return_value = None

        with pytest.raises(DbUnavailableError, match="GEMATRIA_DSN not set"):
            fetch_graph_head(limit=1)

    @patch("agentpm.db.loader.get_control_engine")
    def test_fetch_graph_head_operational_error(self, mock_get_engine):
        """Test fetch_graph_head raises DbUnavailableError on OperationalError."""

        # Create a mock OperationalError class
        class MockOperationalError(Exception):
            pass

        from agentpm.db.loader import DbUnavailableError, fetch_graph_head

        # Set the exception class in the loader module
        import agentpm.db.loader

        original_op_error = getattr(agentpm.db.loader, "OperationalError", None)
        agentpm.db.loader.OperationalError = MockOperationalError

        try:
            mock_engine = MagicMock()
            mock_conn = MagicMock()
            mock_engine.connect.return_value.__enter__.return_value = mock_conn
            mock_conn.execute.side_effect = MockOperationalError("Connection failed")

            mock_get_engine.return_value = mock_engine

            with pytest.raises(DbUnavailableError, match="Database connection failed"):
                fetch_graph_head(limit=1)
        finally:
            if original_op_error is not None:
                agentpm.db.loader.OperationalError = original_op_error
            elif hasattr(agentpm.db.loader, "OperationalError"):
                delattr(agentpm.db.loader, "OperationalError")

    @patch("agentpm.db.loader.get_control_engine")
    def test_fetch_graph_head_table_missing(self, mock_get_engine):
        """Test fetch_graph_head raises TableMissingError when tables don't exist."""

        # Create a mock ProgrammingError class
        class MockProgrammingError(Exception):
            pass

        from agentpm.db.loader import TableMissingError, fetch_graph_head

        # Set the exception class in the loader module
        import agentpm.db.loader

        original_prog_error = getattr(agentpm.db.loader, "ProgrammingError", None)
        agentpm.db.loader.ProgrammingError = MockProgrammingError

        try:
            mock_engine = MagicMock()
            mock_conn = MagicMock()
            mock_engine.connect.return_value.__enter__.return_value = mock_conn
            # Both queries fail with "does not exist"
            mock_conn.execute.side_effect = MockProgrammingError('relation "gematria.nodes" does not exist')

            mock_get_engine.return_value = mock_engine

            with pytest.raises(TableMissingError, match=r"Neither gematria\.nodes nor gematria\.concepts"):
                fetch_graph_head(limit=1)
        finally:
            if original_prog_error is not None:
                agentpm.db.loader.ProgrammingError = original_prog_error
            elif hasattr(agentpm.db.loader, "ProgrammingError"):
                delattr(agentpm.db.loader, "ProgrammingError")


class TestCliBehavior:
    """Test CLI script behavior."""

    @patch("scripts.db_head.fetch_graph_head")
    def test_cli_graph_success(self, mock_fetch, capsys):
        """Test CLI returns ok:true with graph rows when successful."""
        import scripts.db_head

        mock_fetch.return_value = [
            {"node_id": "123", "surface": "test", "gematria_value": 42},
        ]

        # Mock sys.argv
        with patch.object(sys, "argv", ["db_head.py", "graph", "--limit", "1"]):
            result = scripts.db_head.main()

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["ok"] is True
        assert data["kind"] == "graph"
        assert len(data["rows"]) == 1
        assert data["rows"][0]["surface"] == "test"

    @patch("scripts.db_head.fetch_graph_head")
    def test_cli_db_off(self, mock_fetch, capsys):
        """Test CLI returns ok:false with mode:db_off when DB unavailable."""
        import scripts.db_head
        from agentpm.db.loader import DbUnavailableError

        mock_fetch.side_effect = DbUnavailableError("GEMATRIA_DSN not set")

        # Mock sys.argv
        with patch.object(sys, "argv", ["db_head.py", "graph", "--limit", "1"]):
            result = scripts.db_head.main()

        assert result == 1
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["ok"] is False
        assert data["mode"] == "db_off"
        assert "error" in data

    @patch("scripts.db_head.fetch_graph_head")
    def test_cli_table_missing(self, mock_fetch, capsys):
        """Test CLI returns ok:false with mode:table_missing when table doesn't exist."""
        import scripts.db_head
        from agentpm.db.loader import TableMissingError

        mock_fetch.side_effect = TableMissingError("Table does not exist")

        # Mock sys.argv
        with patch.object(sys, "argv", ["db_head.py", "graph", "--limit", "1"]):
            result = scripts.db_head.main()

        assert result == 1
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["ok"] is False
        assert data["mode"] == "table_missing"
        assert "error" in data
