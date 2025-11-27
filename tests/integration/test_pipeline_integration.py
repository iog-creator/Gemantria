"""
Integration tests for the complete integrated pipeline.

Tests the full workflow from noun extraction through analysis and exports.
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch

from src.infra.env_loader import ensure_env_loaded
from src.graph.graph import PipelineState

# Load environment for tests
ensure_env_loaded()

# Check if we have required environment for integration tests
GEMATRIA_DSN_AVAILABLE = bool(os.getenv("GEMATRIA_DSN"))
BIBLE_DB_DSN_AVAILABLE = bool(os.getenv("BIBLE_DB_DSN"))


class TestPipelineIntegration:
    """Test the integrated pipeline components."""

    def test_pipeline_orchestrator_imports(self):
        """Test that pipeline orchestrator can be imported."""
        try:
            from scripts.pipeline_orchestrator import (
                run_full_pipeline,
                run_book_processing,
                run_analysis,
                run_embeddings_backfill,
            )

            assert callable(run_full_pipeline)
            assert callable(run_book_processing)
            assert callable(run_analysis)
            assert callable(run_embeddings_backfill)
        except ImportError as e:
            pytest.skip(f"Pipeline orchestrator not available: {e}")

    def test_schema_validator_node(self):
        """Test schema validator node integration."""
        from src.nodes.schema_validator import schema_validator_node

        # Test with empty state (no schemas to validate)
        state = {"run_id": "test-123", "book_name": "Genesis"}

        result = schema_validator_node(state)

        # Should return state unchanged if no validation files exist
        assert result == state
        assert "run_id" in result

    @patch("src.infra.db.get_gematria_rw")
    def test_analysis_runner_node_no_data(self, mock_db):
        """Test analysis runner with no data."""
        from src.nodes.analysis_runner import analysis_runner_node

        # Mock empty database
        mock_db.return_value.execute.return_value.fetchall.return_value = []

        state = {
            "run_id": "test-123",
            "book_name": "Genesis",
            "network_summary": {"total_nodes": 0},
        }

        result = analysis_runner_node(state)

        # Should handle empty data gracefully
        assert result["run_id"] == "test-123"
        assert "analysis_results" in result

    @patch("src.graph.graph.discover_nouns_for_book")
    @pytest.mark.skipif(not GEMATRIA_DSN_AVAILABLE, reason="GEMATRIA_DSN not available")
    def test_pipeline_creation(self, mock_discover_nouns):
        """Test pipeline creation and basic structure."""

        # Mock noun discovery to return minimal valid data
        mock_discover_nouns.return_value = [
            {
                "noun_id": "test-1",
                "surface": "אלהים",
                "letters": ["א", "ל", "ה", "י", "ם"],  # noqa: RUF001
                "gematria": 86,
                "class": "person",
                "sources": [],
            }
        ]

        # Test pipeline run with provided nouns to avoid full discovery
        from src.graph.graph import run_pipeline

        test_nouns = [
            {
                "noun_id": "test-1",
                "surface": "אלהים",
                "letters": ["א", "ל", "ה", "י", "ם"],  # noqa: RUF001
                "gematria": 86,
                "class": "person",
                "sources": [],
            }
        ]

        result = run_pipeline(book="Genesis", mode="START", nouns=test_nouns)

        # Should return a result dictionary
        assert isinstance(result, dict)
        assert "run_id" in result
        assert "book" in result
        assert "success" in result

    def test_book_processing_integration(self):
        """Test book processing can be called."""
        try:
            from scripts.run_book import DEFAULT_CFG

            # Should have default configuration
            assert "book" in DEFAULT_CFG
            assert "chapters" in DEFAULT_CFG
            assert DEFAULT_CFG["book"] == "Genesis"
            assert len(DEFAULT_CFG["chapters"]) == 50  # Genesis chapters
        except ImportError:
            pytest.skip("Book processing not available")

    def test_embeddings_backfill_structure(self):
        """Test embeddings backfill script structure."""
        try:
            from scripts.backfill_noun_embeddings import backfill_noun_embeddings

            # Should be callable
            assert callable(backfill_noun_embeddings)

            # Should require DSN parameter
            with pytest.raises(TypeError):
                backfill_noun_embeddings()

        except ImportError:
            pytest.skip("Embeddings backfill not available")

    @pytest.mark.skipif(not GEMATRIA_DSN_AVAILABLE, reason="GEMATRIA_DSN not available")
    def test_analysis_scripts_structure(self):
        """Test analysis scripts can be imported."""
        try:
            from scripts.analyze_graph import main as analyze_main
            from scripts.export_graph import main as export_main
            from scripts.export_stats import main as stats_main

            assert callable(analyze_main)
            assert callable(export_main)
            assert callable(stats_main)

        except ImportError:
            pytest.skip("Analysis scripts not available")

    def test_makefile_targets_exist(self):
        """Test that key Makefile targets are defined."""
        makefile_path = Path("Makefile")

        if not makefile_path.exists():
            pytest.skip("Makefile not found")

        content = makefile_path.read_text()

        # Check for key targets
        assert "book.plan:" in content
        assert "book.dry:" in content
        assert "book.go:" in content
        assert "schema.validate:" in content
        assert "analyze.graph:" in content
        assert "analyze.export:" in content
        assert "orchestrator.pipeline:" in content
        assert "orchestrator.full:" in content

    def test_orchestrator_cli_structure(self):
        """Test orchestrator CLI structure."""
        try:
            # Test that we can import the orchestrator module
            import sys
            import os

            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

            from scripts.pipeline_orchestrator import main

            # Should be callable
            assert callable(main)

            # Just test that the module can be imported without errors
            assert True

        except ImportError:
            pytest.skip("Orchestrator CLI not available in this environment")

    def test_pipeline_state_structure(self):
        """Test PipelineState type structure."""
        # Test that we can create a basic pipeline state
        state: PipelineState = {
            "run_id": "test-123",
            "book_name": "Genesis",
            "mode": "START",
            "nouns": [],
            "enriched_nouns": [],
            "conflicts": [],
            "metadata": {},
        }

        assert state["run_id"] == "test-123"
        assert state["book_name"] == "Genesis"
        assert len(state["nouns"]) == 0

    @pytest.mark.skipif(
        not (GEMATRIA_DSN_AVAILABLE and BIBLE_DB_DSN_AVAILABLE),
        reason="Database DSNs not available",
    )
    def test_integration_components_coexist(self):
        """Test that all integration components can be imported together."""
        # This tests that our integration didn't break existing imports
        try:
            from src.graph.graph import run_pipeline, get_graph
            from agentpm.modules.gematria.utils.collect_nouns_db import collect_nouns_for_book
            from src.nodes.enrichment import enrichment_node
            from src.nodes.network_aggregator import network_aggregator_node
            from src.nodes.confidence_validator import confidence_validator_node
            from src.nodes.schema_validator import schema_validator_node
            from src.nodes.analysis_runner import analysis_runner_node

            # All should be callable
            assert callable(run_pipeline)
            assert callable(get_graph)
            assert callable(collect_nouns_for_book)
            assert callable(enrichment_node)
            assert callable(network_aggregator_node)
            assert callable(confidence_validator_node)
            assert callable(schema_validator_node)
            assert callable(analysis_runner_node)

        except ImportError as e:
            pytest.fail(f"Integration components not importable: {e}")
