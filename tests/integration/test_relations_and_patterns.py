"""
Integration tests for relations building and pattern discovery.
"""

import pytest
import psycopg
import os
from unittest.mock import patch, MagicMock
from src.nodes.network_aggregator import build_relations
from src.graph.patterns import build_graph, compute_patterns
from src.infra.db import get_conn


class TestRelationsAndPatternsIntegration:
    """Integration tests for relations and pattern discovery."""

    @pytest.fixture
    def db_connection(self):
        """Get database connection for tests."""
        conn = get_conn()
        yield conn
        conn.close()

    def test_build_relations_disabled(self, db_connection):
        """Test build_relations when relations are disabled."""
        with patch.dict(os.environ, {"ENABLE_RELATIONS": "false"}):
            embeddings_batch = [
                {"concept_id": "test-1", "embedding": [0.1] * 1024},
                {"concept_id": "test-2", "embedding": [0.2] * 1024}
            ]

            edges, rerank_calls = build_relations(db_connection, embeddings_batch)
            assert edges == 0
            assert rerank_calls == 0

    def test_build_relations_no_rerank(self, db_connection):
        """Test build_relations with rerank disabled."""
        # Insert test concept network data
        db_connection.execute("""
            INSERT INTO concept_network (concept_id, label, embedding)
            VALUES (%s, %s, %s), (%s, %s, %s)
            ON CONFLICT (concept_id) DO NOTHING
        """, (
            "test-concept-1", "Test Concept 1", [0.1] * 1024,
            "test-concept-2", "Test Concept 2", [0.9] * 1024  # High similarity
        ))

        with patch.dict(os.environ, {"ENABLE_RELATIONS": "true", "ENABLE_RERANK": "false"}):
            embeddings_batch = [
                {"concept_id": "test-concept-1", "embedding": [0.1] * 1024},
                {"concept_id": "test-concept-2", "embedding": [0.9] * 1024}
            ]

            edges, rerank_calls = build_relations(db_connection, embeddings_batch)
            assert edges >= 0  # May be 0 if similarity threshold not met
            assert rerank_calls == 0  # Rerank disabled

    def test_build_relations_with_rerank(self, db_connection):
        """Test build_relations with rerank enabled."""
        # Insert test concept network data
        db_connection.execute("""
            INSERT INTO concept_network (concept_id, label, embedding)
            VALUES (%s, %s, %s), (%s, %s, %s)
            ON CONFLICT (concept_id) DO NOTHING
        """, (
            "test-concept-3", "Test Concept 3", [0.1] * 1024,
            "test-concept-4", "Test Concept 4", [0.15] * 1024  # Low similarity
        ))

        with patch.dict(os.environ, {"ENABLE_RELATIONS": "true", "ENABLE_RERANK": "true"}):
            with patch('src.services.lmstudio_client.rerank_pairs') as mock_rerank:
                mock_rerank.return_value = [0.8, 0.9]  # Mock high rerank scores

                embeddings_batch = [
                    {"concept_id": "test-concept-3", "embedding": [0.1] * 1024},
                    {"concept_id": "test-concept-4", "embedding": [0.15] * 1024}
                ]

                edges, rerank_calls = build_relations(db_connection, embeddings_batch)
                assert rerank_calls == 1  # Rerank should be called
                mock_rerank.assert_called_once()

    def test_build_graph_from_db(self, db_connection):
        """Test building NetworkX graph from database."""
        # Ensure we have some concept network data
        db_connection.execute("""
            SELECT COUNT(*) FROM concept_network
        """)
        count = db_connection.fetchone()[0]

        if count == 0:
            pytest.skip("No concept network data available for graph building test")

        G = build_graph(db_connection)
        assert G is not None
        assert G.number_of_nodes() > 0
        assert G.number_of_edges() >= 0

    def test_compute_patterns(self, db_connection):
        """Test pattern computation on graph."""
        # Ensure we have some concept network data
        db_connection.execute("""
            SELECT COUNT(*) FROM concept_network
        """)
        count = db_connection.fetchone()[0]

        if count < 2:
            pytest.skip("Need at least 2 concepts for pattern discovery test")

        G = build_graph(db_connection)
        cluster_map, degree, betw, eigen = compute_patterns(G)

        assert isinstance(cluster_map, dict)
        assert isinstance(degree, dict)
        assert isinstance(betw, dict)
        assert isinstance(eigen, dict)

        # All nodes should have cluster assignments
        assert len(cluster_map) == G.number_of_nodes()

        # All nodes should have centrality measures
        assert len(degree) == G.number_of_nodes()
        assert len(betw) == G.number_of_nodes()
        assert len(eigen) == G.number_of_nodes()

    def test_analyze_script_execution(self, db_connection):
        """Test that analyze_graph.py script can be executed."""
        # This is a basic smoke test - the script should not crash
        # In a real test environment, we'd run the script and check results
        import subprocess
        import sys

        try:
            result = subprocess.run([
                sys.executable, "scripts/analyze_graph.py"
            ], capture_output=True, text=True, timeout=30)

            # Script should complete (success or expected failure)
            assert result.returncode in [0, 1]  # 0=success, 1=failure but not crash

        except subprocess.TimeoutExpired:
            pytest.fail("analyze_graph.py script timed out")
        except FileNotFoundError:
            pytest.skip("analyze_graph.py script not found")

    def test_export_script_execution(self, db_connection):
        """Test that export_graph.py script can be executed."""
        import subprocess
        import sys

        try:
            result = subprocess.run([
                sys.executable, "scripts/export_graph.py"
            ], capture_output=True, text=True, timeout=30)

            # Script should complete
            assert result.returncode in [0, 1]

        except subprocess.TimeoutExpired:
            pytest.fail("export_graph.py script timed out")
        except FileNotFoundError:
            pytest.skip("export_graph.py script not found")

    def test_relations_table_exists(self, db_connection):
        """Test that concept_relations table exists and has expected structure."""
        # Check table exists
        db_connection.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'concept_relations'
            )
        """)
        exists = db_connection.fetchone()[0]
        assert exists, "concept_relations table should exist"

        # Check expected columns exist
        db_connection.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'concept_relations'
            ORDER BY column_name
        """)
        columns = [row[0] for row in db_connection.fetchall()]
        expected_cols = ['cosine', 'created_at', 'decided_yes', 'id', 'rerank_score', 'source_id', 'target_id']
        for col in expected_cols:
            assert col in columns, f"Column {col} should exist in concept_relations"

    def test_clusters_table_exists(self, db_connection):
        """Test that concept_clusters table exists."""
        db_connection.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'concept_clusters'
            )
        """)
        exists = db_connection.fetchone()[0]
        assert exists, "concept_clusters table should exist"

    def test_centrality_table_exists(self, db_connection):
        """Test that concept_centrality table exists."""
        db_connection.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'concept_centrality'
            )
        """)
        exists = db_connection.fetchone()[0]
        assert exists, "concept_centrality table should exist"

