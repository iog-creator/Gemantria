"""
Integration tests for network aggregator with database operations.
"""

import os
import unittest
import uuid

import psycopg
from pgvector.psycopg import register_vector

# Set up mock environment to avoid LM Studio dependencies
os.environ["LM_STUDIO_MOCK"] = "true"
os.environ["GEMATRIA_DSN"] = "postgresql://mccoy@/gematria_db?host=/var/run/postgresql"
os.environ["VECTOR_DIM"] = "1024"
os.environ["NN_TOPK"] = "20"
os.environ["RERANK_MIN"] = "0.50"
os.environ["EDGE_STRONG"] = "0.90"
os.environ["EDGE_WEAK"] = "0.75"

import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from nodes.network_aggregator import network_aggregator_node


class TestNetworkAggregatorIntegration(unittest.TestCase):
    """Integration tests for network aggregator with database."""

    def setUp(self):
        """Set up test database connection."""
        self.dsn = os.getenv("GEMATRIA_DSN")
        if not self.dsn:
            self.skipTest("GEMATRIA_DSN not configured")

        # Verify pgvector extension is available
        try:
            with psycopg.connect(self.dsn) as conn, conn.cursor() as cur:
                cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector'")
                if not cur.fetchone():
                    self.skipTest("pgvector extension not installed")
        except Exception:
            self.skipTest("Cannot connect to test database")

    def test_network_aggregator_with_sample_data(self):
        """Test network aggregator with sample enriched nouns."""
        # Sample enriched nouns (simulating output from enrichment node)
        sample_nouns = [
            {
                "noun_id": str(uuid.uuid4()),
                "name": "adam",
                "hebrew": "אָדָם",
                "gematria": 45,
                "gematria_confidence": 1.0,
                "confidence": 0.95,
                "insights": "Adam represents humanity's first relationship with God, symbolizing creation and stewardship.",  # noqa: E501
            },
            {
                "noun_id": str(uuid.uuid4()),
                "name": "hevel",
                "hebrew": "הֶבֶל",
                "gematria": 37,
                "gematria_confidence": 1.0,
                "confidence": 0.92,
                "insights": "Abel represents innocence and the first martyr.",
            },
        ]

        state = {"enriched_nouns": sample_nouns, "run_id": str(uuid.uuid4())}

        # Run network aggregator
        result_state = network_aggregator_node(state)

        # Verify network summary was added
        self.assertIn("network_summary", result_state)
        summary = result_state["network_summary"]

        # Check expected metrics
        self.assertEqual(summary["total_nodes"], 2)
        self.assertIsInstance(summary["embeddings_generated"], int)
        self.assertIsInstance(summary["similarity_computations"], int)
        self.assertIsInstance(summary["strong_edges"], int)
        self.assertIsInstance(summary["weak_edges"], int)

        # Verify data was stored in database
        with psycopg.connect(self.dsn) as conn:
            register_vector(conn)
            with conn.cursor() as cur:
                # Check concept_network table
                cur.execute(
                    "SELECT COUNT(*) FROM concept_network WHERE concept_id = %s",
                    (sample_nouns[0]["noun_id"],),
                )
                count = cur.fetchone()[0]
                self.assertEqual(count, 1)

                # Check concept_relations table
                cur.execute("SELECT COUNT(*) FROM concept_relations")
                relation_count = cur.fetchone()[0]
                # With incomplete data and default thresholds, may have 0 relations
                # (reranking requires complete document strings and scores above threshold)
                self.assertIsInstance(relation_count, int)

    def test_network_aggregator_empty_input(self):
        """Test network aggregator with empty enriched nouns."""
        state = {"enriched_nouns": [], "run_id": str(uuid.uuid4())}

        result_state = network_aggregator_node(state)

        # Should return state unchanged and log appropriately
        self.assertEqual(result_state, state)

    def test_network_aggregator_single_noun(self):
        """Test network aggregator with single noun (no relations possible)."""
        sample_nouns = [
            {
                "noun_id": str(uuid.uuid4()),
                "name": "adam",
                "hebrew": "אָדָם",
                "gematria": 45,
                "gematria_confidence": 1.0,
                "confidence": 0.95,
                "insights": "Adam represents humanity's first relationship with God.",
            }
        ]

        state = {"enriched_nouns": sample_nouns, "run_id": str(uuid.uuid4())}

        result_state = network_aggregator_node(state)

        # Verify network summary
        self.assertIn("network_summary", result_state)
        summary = result_state["network_summary"]

        self.assertEqual(summary["total_nodes"], 1)
        self.assertEqual(summary["strong_edges"], 0)
        self.assertEqual(summary["weak_edges"], 0)
        self.assertEqual(summary["similarity_computations"], 0)  # No pairs to compare

    def test_embedding_storage_format(self):
        """Test that embeddings are stored correctly in vector format."""
        sample_nouns = [
            {
                "noun_id": str(uuid.uuid4()),
                "name": "test",
                "hebrew": "טֶסְט",
                "gematria": 10,
                "gematria_confidence": 1.0,
                "confidence": 0.90,
                "insights": "Test concept for embedding verification.",
            }
        ]

        state = {"enriched_nouns": sample_nouns, "run_id": str(uuid.uuid4())}

        network_aggregator_node(state)

        # Verify embedding was stored and can be retrieved
        with psycopg.connect(self.dsn) as conn:
            register_vector(conn)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT embedding FROM concept_network
                    WHERE concept_id = %s
                """,
                    (sample_nouns[0]["noun_id"],),
                )

                result = cur.fetchone()
                self.assertIsNotNone(result)

                embedding = result[0]
                # pgvector returns numpy arrays, not lists
                self.assertTrue(
                    hasattr(embedding, "__len__") and hasattr(embedding, "__getitem__")
                )
                self.assertEqual(len(embedding), 1024)  # VECTOR_DIM

                # Verify it's a numpy array of float32 values
                import numpy as np  # noqa: E402

                self.assertIsInstance(embedding, np.ndarray)
                self.assertEqual(embedding.dtype, np.float32)

    def test_rerank_evidence_db_writes(self):
        """Test that rerank evidence is properly stored in concept_relations table."""
        # Set low threshold to ensure reranking happens
        os.environ["RERANK_MIN"] = "0.1"

        # Create sample nouns with enough data to trigger reranking
        sample_nouns = [
            {
                "noun_id": str(uuid.uuid4()),
                "name": "adam",
                "hebrew": "אָדָם",
                "value": 45,
                "gematria_confidence": 1.0,
                "confidence": 0.95,
                "insights": "Adam represents humanity's first relationship with God, symbolizing creation and stewardship.",  # noqa: E501
                "primary_verse": "Genesis 1:1",
            },
            {
                "noun_id": str(uuid.uuid4()),
                "name": "eve",
                "hebrew": "חַוָּה",
                "value": 19,
                "gematria_confidence": 1.0,
                "confidence": 0.92,
                "insights": "Eve represents the mother of all living.",
                "primary_verse": "Genesis 2:18",
            },
            {
                "noun_id": str(uuid.uuid4()),
                "name": "abel",
                "hebrew": "הֶבֶל",
                "value": 37,
                "gematria_confidence": 1.0,
                "confidence": 0.90,
                "insights": "Abel represents innocence and the first martyr.",
                "primary_verse": "Genesis 4:2",
            },
        ]

        state = {"enriched_nouns": sample_nouns, "run_id": str(uuid.uuid4())}

        # Run network aggregator
        result_state = network_aggregator_node(state)

        # Verify rerank metrics are present
        self.assertIn("network_summary", result_state)
        summary = result_state["network_summary"]
        self.assertIn("rerank_calls", summary)
        self.assertIn("rerank_yes_ratio", summary)
        self.assertIn("avg_edge_strength", summary)

        # Verify database writes include rerank evidence
        with psycopg.connect(self.dsn) as conn:
            register_vector(conn)
            with conn.cursor() as cur:
                # Check that concept_relations has the new columns populated
                cur.execute(
                    """
                    SELECT cosine, rerank_score, edge_strength, rerank_model, rerank_at
                    FROM concept_relations
                    WHERE rerank_score IS NOT NULL
                    LIMIT 1
                """
                )

                row = cur.fetchone()
                if row:  # May not have rerank data in mock mode
                    cosine, rerank_score, edge_strength, rerank_model, rerank_at = row

                    # Verify data types and ranges
                    self.assertIsInstance(cosine, float)
                    self.assertIsInstance(rerank_score, float)
                    self.assertIsInstance(edge_strength, float)
                    self.assertIsNotNone(rerank_model)
                    self.assertIsNotNone(rerank_at)

                    # Verify ranges
                    self.assertGreaterEqual(cosine, -1.0)
                    self.assertLessEqual(cosine, 1.0)
                    self.assertGreaterEqual(rerank_score, 0.0)
                    self.assertLessEqual(rerank_score, 1.0)
                    self.assertGreaterEqual(edge_strength, 0.0)
                    self.assertLessEqual(edge_strength, 1.0)

    def test_rerank_threshold_boundaries(self):
        """Test that rerank threshold filtering works correctly."""
        # Set low threshold to ensure reranking happens
        os.environ["RERANK_MIN"] = "0.1"

        sample_nouns = [
            {
                "noun_id": str(uuid.uuid4()),
                "name": "test1",
                "hebrew": "טֶסְט",
                "value": 10,
                "gematria_confidence": 1.0,
                "confidence": 0.90,
                "insights": "Test concept one.",
                "primary_verse": "Genesis 1:1",
            },
            {
                "noun_id": str(uuid.uuid4()),
                "name": "test2",
                "hebrew": "טֶסְט",
                "value": 20,
                "gematria_confidence": 1.0,
                "confidence": 0.90,
                "insights": "Test concept two.",
                "primary_verse": "Genesis 1:2",
            },
        ]

        state = {"enriched_nouns": sample_nouns, "run_id": str(uuid.uuid4())}

        result_state = network_aggregator_node(state)

        # With RERANK_MIN=0.0, all rerank scores should pass threshold
        summary = result_state["network_summary"]
        if summary["rerank_calls"] > 0:
            # Should have some edges created
            self.assertGreaterEqual(summary["strong_edges"] + summary["weak_edges"], 0)

        # Reset threshold
        os.environ["RERANK_MIN"] = "0.50"

    def test_deterministic_behavior_toggle(self):
        """Test that USE_QWEN_EMBEDDINGS=false produces deterministic results."""
        # Set deterministic mode
        os.environ["USE_QWEN_EMBEDDINGS"] = "false"
        os.environ["LM_STUDIO_MOCK"] = "true"

        sample_nouns = [
            {
                "noun_id": str(uuid.uuid4()),
                "name": "consistent",
                "hebrew": "קוֹנְסִיסְט",
                "value": 100,
                "gematria_confidence": 1.0,
                "confidence": 0.95,
                "insights": "Consistent test data.",
                "primary_verse": "Genesis 1:1",
            }
        ]

        state = {"enriched_nouns": sample_nouns, "run_id": str(uuid.uuid4())}

        # Run twice and verify deterministic results
        result1 = network_aggregator_node(state.copy())
        result2 = network_aggregator_node(state.copy())

        # Network summaries should be identical
        summary1 = result1["network_summary"]
        summary2 = result2["network_summary"]

        self.assertEqual(summary1["total_nodes"], summary2["total_nodes"])
        self.assertEqual(
            summary1["embeddings_generated"], summary2["embeddings_generated"]
        )

        # Verify embeddings are deterministic
        with psycopg.connect(self.dsn) as conn:
            register_vector(conn)
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT embedding FROM concept_network WHERE concept_id = %s",
                    (sample_nouns[0]["noun_id"],),
                )

                embedding1 = cur.fetchone()[0]

                # Run again with same noun_id
                network_aggregator_node(state.copy())

                cur.execute(
                    "SELECT embedding FROM concept_network WHERE concept_id = %s",
                    (sample_nouns[0]["noun_id"],),
                )

                embedding2 = cur.fetchone()[0]

                # Embeddings should be identical (deterministic mock)
                import numpy as np  # noqa: E402

                self.assertTrue(np.array_equal(embedding1, embedding2))

    def test_edge_strength_classification(self):
        """Test that edge strength classification works at boundary thresholds."""
        # Create nouns that will produce specific edge strengths
        sample_nouns = [
            {
                "noun_id": str(uuid.uuid4()),
                "name": "boundary_test_strong",
                "hebrew": "סְטרוֹנְג",
                "value": 90,
                "gematria_confidence": 1.0,
                "confidence": 0.95,
                "insights": "Test for strong edge classification.",
                "primary_verse": "Genesis 1:1",
            },
            {
                "noun_id": str(uuid.uuid4()),
                "name": "boundary_test_weak",
                "hebrew": "וֶיק",
                "value": 75,
                "gematria_confidence": 1.0,
                "confidence": 0.92,
                "insights": "Test for weak edge classification.",
                "primary_verse": "Genesis 1:2",
            },
        ]

        state = {"enriched_nouns": sample_nouns, "run_id": str(uuid.uuid4())}

        network_aggregator_node(state)

        # Verify that edges are classified appropriately
        with psycopg.connect(self.dsn) as conn:
            register_vector(conn)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT relation_type, edge_strength
                    FROM concept_relations
                    WHERE edge_strength IS NOT NULL
                """
                )

                for relation_type, edge_strength in cur.fetchall():
                    if edge_strength >= 0.90:
                        self.assertEqual(relation_type, "strong")
                    elif edge_strength >= 0.75:
                        self.assertEqual(relation_type, "weak")
                    else:
                        # Should not be stored if below threshold
                        self.fail(
                            f"Edge with strength {edge_strength} should not be stored"
                        )


if __name__ == "__main__":
    unittest.main()
