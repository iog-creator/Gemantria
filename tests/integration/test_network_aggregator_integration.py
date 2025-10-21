"""
Integration tests for network aggregator with database operations.
"""

import os
import unittest
import uuid
import tempfile
import psycopg
from pgvector.psycopg import register_vector

# Set up mock environment to avoid LM Studio dependencies
os.environ["LM_STUDIO_MOCK"] = "true"
os.environ["GEMATRIA_DSN"] = "postgresql://mccoy@/gematria_db?host=/var/run/postgresql"
os.environ["VECTOR_DIM"] = "1024"

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from nodes.network_aggregator import network_aggregator_node, NetworkAggregationError


class TestNetworkAggregatorIntegration(unittest.TestCase):
    """Integration tests for network aggregator with database."""

    def setUp(self):
        """Set up test database connection."""
        self.dsn = os.getenv("GEMATRIA_DSN")
        if not self.dsn:
            self.skipTest("GEMATRIA_DSN not configured")

        # Verify pgvector extension is available
        try:
            with psycopg.connect(self.dsn) as conn:
                with conn.cursor() as cur:
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
                "insights": "Adam represents humanity's first relationship with God, symbolizing creation and stewardship."
            },
            {
                "noun_id": str(uuid.uuid4()),
                "name": "hevel",
                "hebrew": "הֶבֶל",
                "gematria": 37,
                "gematria_confidence": 1.0,
                "confidence": 0.92,
                "insights": "Abel represents innocence and the first martyr, showing the contrast between righteousness and evil."
            }
        ]

        state = {
            "enriched_nouns": sample_nouns,
            "run_id": str(uuid.uuid4())
        }

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
                cur.execute("SELECT COUNT(*) FROM concept_network WHERE concept_id = %s",
                          (sample_nouns[0]["noun_id"],))
                count = cur.fetchone()[0]
                self.assertEqual(count, 1)

                # Check concept_relations table (should have at least one relation)
                cur.execute("SELECT COUNT(*) FROM concept_relations")
                relation_count = cur.fetchone()[0]
                # With 2 nodes, we expect 1 bidirectional relation (stored as 1 record)
                self.assertGreaterEqual(relation_count, 1)

    def test_network_aggregator_empty_input(self):
        """Test network aggregator with empty enriched nouns."""
        state = {
            "enriched_nouns": [],
            "run_id": str(uuid.uuid4())
        }

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
                "insights": "Adam represents humanity's first relationship with God."
            }
        ]

        state = {
            "enriched_nouns": sample_nouns,
            "run_id": str(uuid.uuid4())
        }

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
                "insights": "Test concept for embedding verification."
            }
        ]

        state = {
            "enriched_nouns": sample_nouns,
            "run_id": str(uuid.uuid4())
        }

        network_aggregator_node(state)

        # Verify embedding was stored and can be retrieved
        with psycopg.connect(self.dsn) as conn:
            register_vector(conn)
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT embedding FROM concept_network
                    WHERE concept_id = %s
                """, (sample_nouns[0]["noun_id"],))

                result = cur.fetchone()
                self.assertIsNotNone(result)

                embedding = result[0]
                self.assertIsInstance(embedding, list)
                self.assertEqual(len(embedding), 1024)  # VECTOR_DIM

                # Verify it's a list of floats
                self.assertTrue(all(isinstance(x, float) for x in embedding))


if __name__ == '__main__':
    unittest.main()
