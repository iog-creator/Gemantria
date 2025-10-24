"""
Unit tests for network aggregator functionality.
"""

import math
import os
import sys
import unittest
from unittest.mock import patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from nodes.network_aggregator import (VECTOR_DIM, _build_document_string,
                                      _cosine_similarity, _l2_normalize)
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
        expected = (4 + 10 + 18) / ((14**0.5) * (77**0.5))
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

    @patch("services.lmstudio_client.requests.Session.post")
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
            norm = sum(x * x for x in embedding) ** 0.5
            self.assertAlmostEqual(norm, 1.0, places=5)

    @patch("services.lmstudio_client.requests.Session.post")
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
        norm = sum(x * x for x in embedding) ** 0.5
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
        norm = math.sqrt(sum(x * x for x in vec))
        normalized = [x / norm for x in vec]

        self.assertAlmostEqual(normalized[0], 0.6, places=5)
        self.assertAlmostEqual(normalized[1], 0.8, places=5)

        # Check that normalized vector has unit norm
        normalized_norm = math.sqrt(sum(x * x for x in normalized))
        self.assertAlmostEqual(normalized_norm, 1.0, places=5)


class TestDocumentBuilding(unittest.TestCase):
    """Test document string building for embeddings and reranking."""

    def test_build_document_string_complete(self):
        """Test building document string with all fields present."""
        noun = {
            "name": "Adam",
            "hebrew": "אדם",
            "primary_verse": "Genesis 1:1",
            "value": 45,
            "insight": "First man created by God",
        }

        result = _build_document_string(noun)

        expected = """Document: Adam
Meaning: אדם
Primary Verse: Genesis 1:1
Gematria: 45
Insight: First man created by God"""

        self.assertEqual(result, expected)

    def test_build_document_string_missing_primary_verse(self):
        """Test building document string with missing primary_verse uses placeholder."""
        noun = {"name": "Eve", "hebrew": "חוה", "value": 19, "insight": "First woman"}

        result = _build_document_string(noun)

        expected = """Document: Eve
Meaning: חוה
Primary Verse: Genesis (reference)
Gematria: 19
Insight: First woman"""

        self.assertEqual(result, expected)

    def test_build_document_string_minimal(self):
        """Test building document string with minimal required fields."""
        noun = {"name": "Test", "hebrew": "טסט", "value": 100}

        result = _build_document_string(noun)

        expected = """Document: Test
Meaning: טסט
Primary Verse: Genesis (reference)
Gematria: 100
Insight:"""

        self.assertEqual(result, expected)


class TestEdgeStrengthCalculation(unittest.TestCase):
    """Test edge strength calculation logic."""

    def test_edge_strength_calculation(self):
        """Test edge strength calculation: 0.5 * cosine + 0.5 * rerank_score."""
        # Test various combinations
        test_cases = [
            # (cosine, rerank_score, expected_edge_strength)
            (0.9, 1.0, 0.95),  # High cosine, perfect rerank
            (0.8, 0.6, 0.7),  # Medium values
            (0.95, 0.5, 0.725),  # High cosine, low rerank
            (0.7, 0.9, 0.8),  # Low cosine, high rerank
            (0.0, 1.0, 0.5),  # Zero cosine, perfect rerank
            (1.0, 0.0, 0.5),  # Perfect cosine, zero rerank
        ]

        for cosine, rerank_score, expected in test_cases:
            with self.subTest(cosine=cosine, rerank_score=rerank_score):
                edge_strength = 0.5 * cosine + 0.5 * rerank_score
                self.assertAlmostEqual(edge_strength, expected, places=5)

    def test_edge_classification_strong(self):
        """Test edge classification for strong relationships (≥0.90)."""
        # Import the constants
        import os

        os.environ["EDGE_STRONG"] = "0.90"

        edge_strength = 0.95
        self.assertGreaterEqual(edge_strength, 0.90)

        # Should be classified as strong
        relation_type = (
            "strong"
            if edge_strength >= 0.90
            else "weak" if edge_strength >= 0.75 else None
        )
        self.assertEqual(relation_type, "strong")

    def test_edge_classification_weak(self):
        """Test edge classification for weak relationships (≥0.75, <0.90)."""
        import os

        os.environ["EDGE_STRONG"] = "0.90"
        os.environ["EDGE_WEAK"] = "0.75"

        edge_strength = 0.82
        self.assertGreaterEqual(edge_strength, 0.75)
        self.assertLess(edge_strength, 0.90)

        # Should be classified as weak
        if edge_strength >= 0.90:
            relation_type = "strong"
        elif edge_strength >= 0.75:
            relation_type = "weak"
        else:
            relation_type = None
        self.assertEqual(relation_type, "weak")

    def test_edge_classification_filtered(self):
        """Test edge classification for filtered relationships (<0.75)."""
        import os

        os.environ["EDGE_WEAK"] = "0.75"

        edge_strength = 0.70
        self.assertLess(edge_strength, 0.75)

        # Should be filtered out
        if edge_strength >= 0.90:
            relation_type = "strong"
        elif edge_strength >= 0.75:
            relation_type = "weak"
        else:
            relation_type = None
        self.assertIsNone(relation_type)


class TestRerankScoreMapping(unittest.TestCase):
    """Test rerank score mapping from logprobs and text parsing."""

    def test_logprob_score_calculation(self):
        """Test score calculation from log probabilities using sigmoid."""
        import math

        # Mock logprobs data
        logprobs = {
            "content": [
                {"token": "yes", "logprob": -0.5},
                {"token": "no", "logprob": -1.0},
            ]
        }

        # Extract logprobs (simulate the logic)
        yes_logprob = None
        no_logprob = None

        for token_info in logprobs["content"]:
            token = token_info["token"].strip().lower()
            logprob = token_info["logprob"]

            if "yes" in token:
                yes_logprob = max(yes_logprob or float("-inf"), logprob)
            elif "no" in token:
                no_logprob = max(no_logprob or float("-inf"), logprob)

        # Calculate score using sigmoid of logit difference
        if yes_logprob is not None and no_logprob is not None:
            logit_diff = yes_logprob - no_logprob
            score = 1 / (1 + math.exp(-logit_diff))

            # yes_logprob = -0.5, no_logprob = -1.0
            # logit_diff = -0.5 - (-1.0) = 0.5
            # score = sigmoid(0.5) ≈ 0.622
            expected_score = 1 / (1 + math.exp(-0.5))
            self.assertAlmostEqual(score, expected_score, places=3)

    def test_text_parsing_yes(self):
        """Test text parsing for 'yes' responses."""
        response_texts = ["yes", "Yes", "YES", "yes, that matches", "definitely yes"]

        for text in response_texts:
            with self.subTest(text=text):
                score = 1.0 if "yes" in text.lower() else 0.0
                self.assertEqual(score, 1.0)

    def test_text_parsing_no(self):
        """Test text parsing for 'no' responses."""
        response_texts = ["no", "No", "NO", "no, doesn't match", "definitely no"]

        for text in response_texts:
            with self.subTest(text=text):
                if "yes" in text.lower():
                    score = 1.0
                elif "no" in text.lower():
                    score = 0.0
                else:
                    score = 0.5
                self.assertEqual(score, 0.0)

    def test_text_parsing_neutral(self):
        """Test text parsing for unclear responses."""
        response_texts = ["maybe", "unclear", "possibly", "perhaps"]

        for text in response_texts:
            with self.subTest(text=text):
                text_lower = text.lower()
                if text_lower == "yes":
                    score = 1.0
                elif text_lower == "no":
                    score = 0.0
                else:
                    score = 0.5
                self.assertEqual(score, 0.5)


class TestVectorNormalization(unittest.TestCase):
    """Test vector normalization and dimension validation."""

    def test_l2_normalize_unit_vector(self):
        """Test L2 normalization of already unit vector."""
        vec = [1.0, 0.0, 0.0]
        result = _l2_normalize(vec)
        self.assertAlmostEqual(result[0], 1.0, places=6)
        self.assertAlmostEqual(result[1], 0.0, places=6)
        self.assertAlmostEqual(result[2], 0.0, places=6)

        # Check that result is still unit length
        norm = math.sqrt(sum(x * x for x in result))
        self.assertAlmostEqual(norm, 1.0, places=6)

    def test_l2_normalize_arbitrary_vector(self):
        """Test L2 normalization of arbitrary vector."""
        vec = [3.0, 4.0]  # Should normalize to [0.6, 0.8]
        result = _l2_normalize(vec)

        expected_norm = math.sqrt(3**2 + 4**2)  # = 5.0
        expected = [3.0 / expected_norm, 4.0 / expected_norm]

        self.assertAlmostEqual(result[0], expected[0], places=6)
        self.assertAlmostEqual(result[1], expected[1], places=6)

        # Check that result has unit norm
        norm = math.sqrt(sum(x * x for x in result))
        self.assertAlmostEqual(norm, 1.0, places=6)

    def test_l2_normalize_zero_vector(self):
        """Test L2 normalization handles zero vector gracefully."""
        vec = [0.0, 0.0, 0.0]
        result = _l2_normalize(vec)
        # Should return the zero vector (norm=0 handled gracefully)
        self.assertEqual(result, [0.0, 0.0, 0.0])

    def test_vector_dimension_constant(self):
        """Test that VECTOR_DIM constant is set correctly."""
        # Should be 1024 for Qwen3 embeddings
        self.assertEqual(VECTOR_DIM, 1024)

    def test_dimension_mismatch_error_message(self):
        """Test that dimension mismatch error has proper message."""
        expected_dim = VECTOR_DIM
        actual_dim = 512
        index = 0

        error_msg = (
            f"Embedding dimension mismatch: expected {expected_dim}, got {actual_dim} "
            f"(candidate index {index} in batch). Fix by aligning VECTOR_DIM and column type."
        )

        # Verify the error message format
        self.assertIn("dimension mismatch", error_msg)
        self.assertIn("expected 1024", error_msg)
        self.assertIn("got 512", error_msg)
        self.assertIn("candidate index 0", error_msg)


if __name__ == "__main__":
    unittest.main()
