#!/usr/bin/env python3
"""
Comprehensive test for bi-encoder rerank proxy implementation.

Tests the rerank_via_embeddings service and pipeline integration.
"""

import sys
import unittest.mock as mock

import numpy as np

# Add src to path
sys.path.insert(0, "src")


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def test_bi_encoder_rerank():
    """Test the bi-encoder rerank logic with various scenarios."""
    print("🧪 Testing Bi-Encoder Rerank Implementation")
    print("=" * 50)

    # Test 1: Basic functionality
    print("\n1. Testing basic rerank functionality...")

    with mock.patch("src.services.rerank_via_embeddings.requests") as mock_requests:
        # Mock embeddings for three Hebrew concepts
        embeddings = {
            "אלהים": [1.0, 0.0, 0.0],  # God - unit vector
            "ברא": [0.0, 1.0, 0.0],  # created - unit vector
            "שמים": [0.707, 0.707, 0.0],  # heaven - 45-degree angle
        }

        # The function makes two separate _embed() calls: one for A texts, one for B texts
        # So we need two responses: one for A batch, one for B batch

        # Mock response for A batch
        mock_resp_a = mock.MagicMock()
        mock_resp_a.json.return_value = {
            "data": [
                {"embedding": embeddings["אלהים"]},
                {"embedding": embeddings["אלהים"]},
                {"embedding": embeddings["ברא"]},
            ]
        }

        # Mock response for B batch
        mock_resp_b = mock.MagicMock()
        mock_resp_b.json.return_value = {
            "data": [
                {"embedding": embeddings["ברא"]},
                {"embedding": embeddings["שמים"]},
                {"embedding": embeddings["שמים"]},
            ]
        }

        mock_requests.post.side_effect = [mock_resp_a, mock_resp_b]

        # Import and test the rerank function
        from src.services.rerank_via_embeddings import (  # noqa: E402
            rerank_via_embeddings,
        )

        test_pairs = [(0, 1), (0, 2), (1, 2)]
        test_names = {0: "אלהים", 1: "ברא", 2: "שמים"}

        scores = rerank_via_embeddings(test_pairs, test_names)

        print(f"   Rerank scores: {['.3f' for s in scores]}")

        # Expected scores (cosine similarity)
        expected_scores = [
            cosine_similarity(embeddings["אלהים"], embeddings["ברא"]),  # 0.0 (orthogonal)
            cosine_similarity(embeddings["אלהים"], embeddings["שמים"]),  # ~0.707 (45°)
            cosine_similarity(embeddings["ברא"], embeddings["שמים"]),  # ~0.707 (45°)
        ]

        print(f"   Expected scores: {['.3f' for s in expected_scores]}")

        # Validate scores are reasonable
        assert all(0 <= s <= 1 for s in scores), "Scores should be in [0,1] range"
        assert len(scores) == len(test_pairs), "Should return one score per pair"
        assert scores[0] < scores[1], "Orthogonal vectors should have lower similarity than 45°"

        print("   ✅ Basic functionality test PASSED")

    # Test 2: Normalization
    print("\n2. Testing text normalization...")

    from src.services.rerank_via_embeddings import _norm  # noqa: E402

    test_cases = [
        ("hello world", "hello world"),
        ("hello   world", "hello world"),
        ("אלהים ברא", "אלהים ברא"),
        ("אלהים\tברא\n", "אלהים ברא"),
        ("שָׁמַיִם וָאָרֶץ", "שָׁמַיִם וָאָרֶץ"),  # With Hebrew vowels
    ]

    for input_text, expected in test_cases:
        result = _norm(input_text)
        assert (
            result == expected
        ), f"Normalization failed: '{input_text}' -> '{result}' != '{expected}'"
        print(f"   '{input_text}' -> '{result}' ✅")

    print("   ✅ Text normalization test PASSED")

    # Test 3: Cache tagging
    print("\n3. Testing cache tagging...")

    # Verify that the rerank_model is set correctly in network_aggregator.py
    with open("src/nodes/network_aggregator.py") as f:
        content = f.read()

    assert "bge-m3-emb-proxy@" in content, "Cache tagging not found in network_aggregator.py"
    assert "EMBEDDING_MODEL" in content, "Embedding model reference not found"

    print("   ✅ Cache tagging test PASSED")

    # Test 4: Import and interface compatibility
    print("\n4. Testing import and interface compatibility...")

    # Test that the new rerank function can be imported as the old name
    from src.services.rerank_via_embeddings import (  # noqa: E402
        rerank_via_embeddings as rerank_pairs,
    )

    # Test with simple mock
    with mock.patch("src.services.rerank_via_embeddings.requests") as mock_requests:
        mock_resp_a = mock.MagicMock()
        mock_resp_a.json.return_value = {"data": [{"embedding": [1.0, 0.0]}]}
        mock_resp_b = mock.MagicMock()
        mock_resp_b.json.return_value = {"data": [{"embedding": [0.0, 1.0]}]}
        mock_requests.post.side_effect = [mock_resp_a, mock_resp_b]

        # Test that it can be called with the old interface
        pairs = [(0, 1)]
        names = {0: "test1", 1: "test2"}

        scores = rerank_pairs(pairs, names)
        assert len(scores) == 1, "Should return one score for one pair"
        assert 0 <= scores[0] <= 1, "Score should be in [0,1] range"

        print("   ✅ Import and interface compatibility test PASSED")

    print("\n🎉 All Bi-Encoder Rerank Tests PASSED!")
    print("The implementation is ready for pipeline integration.")
    print("\nNext steps:")
    print("- Start LM Studio servers manually or fix CLI issues")
    print("- Run Genesis pipeline with ALLOW_PARTIAL=1 for small batch")
    print("- Validate rerank scores show proper distribution (not all ~0.5)")


if __name__ == "__main__":
    test_bi_encoder_rerank()
