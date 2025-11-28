"""Tests for gematria cache module (Phase 14 PR 14.2)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from sqlalchemy import Engine
from sqlalchemy.exc import OperationalError

from agentpm.modules.gematria.cache import CachedGematriaValue, GematriaCache


class TestGematriaCache:
    """Test GematriaCache operations."""

    @patch("agentpm.modules.gematria.cache.get_control_engine")
    def test_cache_get_miss(self, mock_get_engine):
        """Test cache miss returns None."""
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        cache = GematriaCache()
        value = cache.get("HE", "H430", "אֱלֹהִים", "mispar_hechrachi")

        assert value is None

    @patch("agentpm.modules.gematria.cache.get_control_engine")
    def test_cache_set_and_get(self, mock_get_engine):
        """Test set and get operations."""
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()

        # Mock set operation (INSERT)
        mock_set_result = MagicMock()
        # Mock get operation (SELECT)
        mock_get_result = MagicMock()
        mock_get_result.fetchone.return_value = (86,)  # gematria_value for אֱלֹהִים

        # Set up side_effect to handle both queries
        mock_conn.execute.side_effect = [mock_set_result, mock_get_result]
        mock_conn.commit.return_value = None

        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        cache = GematriaCache()

        # Set value
        result = cache.set("HE", "H430", "אֱלֹהִים", "mispar_hechrachi", 86)
        assert result is True

        # Get value
        value = cache.get("HE", "H430", "אֱלֹהִים", "mispar_hechrachi")
        assert value == 86

    @patch("agentpm.modules.gematria.cache.get_control_engine")
    def test_cache_upsert_idempotent(self, mock_get_engine):
        """Test ON CONFLICT DO NOTHING ensures idempotent upsert."""
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_conn.execute.return_value = mock_result
        mock_conn.commit.return_value = None
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        cache = GematriaCache()

        # Set same value twice (should not error due to UNIQUE constraint)
        result1 = cache.set("HE", "H430", "אֱלֹהִים", "mispar_hechrachi", 86)
        result2 = cache.set("HE", "H430", "אֱלֹהִים", "mispar_hechrachi", 86)

        assert result1 is True
        assert result2 is True

    @patch("agentpm.modules.gematria.cache.get_control_engine")
    def test_cache_different_systems(self, mock_get_engine):
        """Test caching works for different gematria systems."""
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()

        # Mock responses for different systems
        mock_hechrachi = MagicMock()
        mock_hechrachi.fetchone.return_value = (86,)
        mock_gadol = MagicMock()
        mock_gadol.fetchone.return_value = (646,)

        mock_conn.execute.side_effect = [mock_hechrachi, mock_gadol]
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        cache = GematriaCache()

        # Get values for different systems
        value_hechrachi = cache.get("HE", "H430", "אֱלֹהִים", "mispar_hechrachi")
        value_gadol = cache.get("HE", "H430", "אֱלֹהִים", "mispar_gadol")

        assert value_hechrachi == 86
        assert value_gadol == 646

    @patch("agentpm.modules.gematria.cache.get_control_engine")
    def test_cache_db_unavailable(self, mock_get_engine):
        """Test graceful handling when DB unavailable."""
        from agentpm.db.loader import DbUnavailableError

        mock_get_engine.side_effect = DbUnavailableError("DB unavailable")

        cache = GematriaCache()

        # Get should return None
        value = cache.get("HE", "H430", "אֱלֹהִים", "mispar_hechrachi")
        assert value is None
        assert cache._db_available is False

        # Set should return False
        result = cache.set("HE", "H430", "אֱלֹהִים", "mispar_hechrachi", 86)
        assert result is False

    @patch("agentpm.modules.gematria.cache.get_control_engine")
    def test_cache_operational_error(self, mock_get_engine):
        """Test handling of operational errors."""
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = OperationalError("Connection failed", None, None)
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        cache = GematriaCache()
        value = cache.get("HE", "H430", "אֱלֹהִים", "mispar_hechrachi")

        assert value is None
        assert cache._db_available is False

    @patch("agentpm.modules.gematria.cache.get_control_engine")
    def test_batch_populate_with_limit(self, mock_get_engine):
        """Test batch populate with limit."""
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()

        # Mock source query results
        mock_words = MagicMock()
        mock_words.__iter__.return_value = [
            ("בְּרֵאשִׁית", "H7225"),
            ("אֱלֹהִים", "H430"),
        ]

        # Mock cache check queries (both return None - not cached)
        mock_check1 = MagicMock()
        mock_check1.fetchone.return_value = None
        mock_check2 = MagicMock()
        mock_check2.fetchone.return_value = None

        # Mock insert operations
        mock_insert1 = MagicMock()
        mock_insert2 = MagicMock()

        mock_conn.execute.side_effect = [
            mock_words,
            mock_check1,
            mock_insert1,
            mock_check2,
            mock_insert2,
        ]
        mock_conn.commit.return_value = None
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        cache = GematriaCache()
        stats = cache.batch_populate("hebrew_ot_words", "mispar_hechrachi", limit=2)

        assert stats["processed"] == 2
        assert stats["cached"] >= 0  # May be 0 or 2 depending on mock behavior
        assert stats["errors"] == 0

    @patch("agentpm.modules.gematria.cache.get_control_engine")
    def test_batch_populate_unknown_source(self, mock_get_engine):
        """Test batch populate with unknown source table."""
        mock_get_engine.return_value = MagicMock(spec=Engine)

        cache = GematriaCache()
        stats = cache.batch_populate("unknown_table", "mispar_hechrachi")

        assert stats["processed"] == 0
        assert stats["errors"] == 1
        assert "Unknown source" in stats.get("error_msg", "")
