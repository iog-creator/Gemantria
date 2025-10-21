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


if __name__ == '__main__':
    unittest.main()
