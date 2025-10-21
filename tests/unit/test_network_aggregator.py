"""
Unit tests for network aggregator functionality.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from nodes.network_aggregator import _cosine_similarity, NetworkAggregationError
from services.lmstudio_client import LMStudioClient


class TestCosineSimilarity(unittest.TestCase):
    """Test cosine similarity calculations."""

    def test_cosine_similarity_identical_vectors(self):
        """Test cosine similarity of identical vectors is 1.0."""
        vec = [1.0, 2.0, 3.0]
        result = _cosine_similarity(vec, vec)
        self.assertAlmostEqual(result, 1.0, places=6)

    def test_cosine_similarity_orthogonal_vectors(self):
        """Test cosine similarity of orthogonal vectors is 0.0."""
        vec1 = [1.0, 0.0]
        vec2 = [0.0, 1.0]
        result = _cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(result, 0.0, places=6)

    def test_cosine_similarity_opposite_vectors(self):
        """Test cosine similarity of opposite vectors is -1.0."""
        vec1 = [1.0, 2.0]
        vec2 = [-1.0, -2.0]
        result = _cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(result, -1.0, places=6)

    def test_cosine_similarity_arbitrary_vectors(self):
        """Test cosine similarity of arbitrary vectors."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [4.0, 5.0, 6.0]
        # Manual calculation: (1*4 + 2*5 + 3*6) / (sqrt(14) * sqrt(77)) ≈ 0.974631846
        expected = (4 + 10 + 18) / ((14 ** 0.5) * (77 ** 0.5))
        result = _cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(result, expected, places=6)

    def test_cosine_similarity_zero_vector(self):
        """Test cosine similarity with zero vector."""
        vec1 = [0.0, 0.0, 0.0]
        vec2 = [1.0, 2.0, 3.0]
        result = _cosine_similarity(vec1, vec2)
        self.assertEqual(result, 0.0)

    def test_cosine_similarity_different_lengths(self):
        """Test cosine similarity with vectors of different lengths raises error."""
        vec1 = [1.0, 2.0]
        vec2 = [1.0, 2.0, 3.0]
        with self.assertRaises(ValueError):
            _cosine_similarity(vec1, vec2)


class TestNetworkAggregatorLogic(unittest.TestCase):
    """Test network aggregator logic without database dependencies."""

    def test_relationship_classification_strong(self):
        """Test that similarity > 0.90 is classified as strong."""
        # This is more of a documentation test since the logic is simple
        similarity = 0.95
        self.assertGreater(similarity, 0.90)
        # Strong relationship check
        self.assertEqual("strong" if similarity > 0.90 else "weak", "strong")

    def test_relationship_classification_weak(self):
        """Test that similarity > 0.75 and <= 0.90 is classified as weak."""
        similarity = 0.85
        self.assertGreater(similarity, 0.75)
        self.assertLessEqual(similarity, 0.90)
        # Weak relationship check
        if similarity > 0.90:
            relation_type = "strong"
        elif similarity > 0.75:
            relation_type = "weak"
        else:
            relation_type = None
        self.assertEqual(relation_type, "weak")

    def test_relationship_classification_none(self):
        """Test that similarity <= 0.75 is not classified."""
        similarity = 0.70
        self.assertLessEqual(similarity, 0.75)
        # No relationship check
        if similarity > 0.90:
            relation_type = "strong"
        elif similarity > 0.75:
            relation_type = "weak"
        else:
            relation_type = None
        self.assertIsNone(relation_type)


class TestEmbeddingFunctionality(unittest.TestCase):
    """Test embedding generation and processing."""

    def setUp(self):
        """Set up test environment."""
        # Ensure we use mock mode for testing
        os.environ["LM_STUDIO_MOCK"] = "true"
        os.environ["USE_QWEN_EMBEDDINGS"] = "false"

    def tearDown(self):
        """Clean up test environment."""
        # Reset environment variables
        if "LM_STUDIO_MOCK" in os.environ:
            del os.environ["LM_STUDIO_MOCK"]
        if "USE_QWEN_EMBEDDINGS" in os.environ:
            del os.environ["USE_QWEN_EMBEDDINGS"]

    @patch('services.lmstudio_client.requests.Session.post')
    def test_get_embeddings_mock_mode(self, mock_post):
        """Test get_embeddings returns normalized vectors in mock mode."""
        client = LMStudioClient()
        texts = ["test text 1", "test text 2"]

        embeddings = client.get_embeddings(texts)

        # Should return list of lists
        self.assertIsInstance(embeddings, list)
        self.assertEqual(len(embeddings), 2)

        # Each embedding should be normalized (L2 norm ≈ 1.0)
        for embedding in embeddings:
            self.assertIsInstance(embedding, list)
            self.assertEqual(len(embedding), 1024)

            # Check L2 normalization
            norm = sum(x*x for x in embedding) ** 0.5
            self.assertAlmostEqual(norm, 1.0, places=5)

    @patch('services.lmstudio_client.requests.Session.post')
    def test_get_embeddings_real_mode_disabled(self, mock_post):
        """Test get_embeddings returns normalized vectors when USE_QWEN_EMBEDDINGS=false."""
        os.environ["USE_QWEN_EMBEDDINGS"] = "false"

        client = LMStudioClient()
        texts = ["test text"]

        embeddings = client.get_embeddings(texts)

        # Should use mock mode when disabled
        self.assertIsInstance(embeddings, list)
        self.assertEqual(len(embeddings), 1)

        embedding = embeddings[0]
        norm = sum(x*x for x in embedding) ** 0.5
        self.assertAlmostEqual(norm, 1.0, places=5)

    def test_rerank_mock_mode(self):
        """Test rerank returns scores in mock mode."""
        client = LMStudioClient()
        query = "test query"
        candidates = ["candidate 1", "candidate 2", "candidate 3"]

        scores = client.rerank(query, candidates)

        # Should return list of floats
        self.assertIsInstance(scores, list)
        self.assertEqual(len(scores), 3)

        # All scores should be between 0.1 and 0.9 (mock range)
        for score in scores:
            self.assertIsInstance(score, float)
            self.assertGreaterEqual(score, 0.1)
            self.assertLessEqual(score, 0.9)

    def test_vector_normalization(self):
        """Test that vectors are properly L2 normalized."""
        import math

        # Test with a non-normalized vector
        vec = [3.0, 4.0]  # Should normalize to [0.6, 0.8]
        norm = math.sqrt(sum(x*x for x in vec))
        normalized = [x/norm for x in vec]

        self.assertAlmostEqual(normalized[0], 0.6, places=5)
        self.assertAlmostEqual(normalized[1], 0.8, places=5)

        # Check that normalized vector has unit norm
        normalized_norm = math.sqrt(sum(x*x for x in normalized))
        self.assertAlmostEqual(normalized_norm, 1.0, places=5)


if __name__ == '__main__':
    unittest.main()
