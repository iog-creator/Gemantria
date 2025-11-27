# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
Sanity check script for quality metrics validation.
Runs focused test on Genesis 1 and reports key quality metrics.
"""

import os
import statistics
import sys

# Add src to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
src_path = os.path.join(project_root, "src")
sys.path.insert(0, src_path)

from src.infra.env_loader import ensure_env_loaded  # noqa: E402
from agentpm.modules.gematria.utils.collect_nouns_db import collect_nouns_for_book  # noqa: E402
from src.nodes.enrichment import enrichment_node  # noqa: E402
from src.nodes.network_aggregator import (  # noqa: E402
    _build_document_string,
    _knn_pairs,
    _l2_normalize,
)
from src.services.lmstudio_client import get_lmstudio_client  # noqa: E402

# Load environment
ensure_env_loaded()


def test_genesis_chapter_1():
    """Run sanity check on Genesis chapter 1 nouns."""

    print("🔍 GEMATRIA QUALITY SANITY CHECK")
    print("=" * 50)

    # 1. Collect nouns from Genesis (limited to chapter 1 context)
    print("\n1. 📚 Collecting nouns from Genesis...")
    try:
        # Get all Genesis nouns but we'll limit processing
        all_nouns = collect_nouns_for_book("Genesis")
        # Take first 10 for focused testing
        test_nouns = all_nouns[:10]

        print(f"   Found {len(all_nouns)} total nouns, testing with {len(test_nouns)}")

        for i, noun in enumerate(test_nouns[:3]):  # Show first 3
            print(f"   {i + 1}. {noun['hebrew']} ({noun['freq']} occurrences)")

    except Exception as e:
        print(f"   ❌ Collection failed: {e}")
        return

    # 2. Enrich nouns
    print("\n2. 🤖 Enriching nouns with AI...")
    enriched_nouns = []
    total_words = 0
    total_confidence = 0

    for i, noun in enumerate(test_nouns):
        print(f"   Enriching {i + 1}/{len(test_nouns)}: {noun['hebrew']}")
        try:
            # Create run context

            # Enrich using the node function
            state = {"validated_nouns": [noun], "run_id": "sanity_check"}
            result = enrichment_node(state)
            enriched_nouns_result = result.get("enriched_nouns", [])
            if enriched_nouns_result:
                enriched = enriched_nouns_result[0].copy()
            else:
                print("     ❌ No enriched nouns returned")
                continue

            # Extract confidence and word count
            confidence = enriched.get("confidence", 0)
            insight = enriched.get("insights", "")
            word_count = len(insight.split())

            total_confidence += confidence
            total_words += word_count

            enriched_nouns.append(enriched)

            print(f"     ✓ Confidence: {confidence:.3f}, Words: {word_count}")

        except Exception as e:
            print(f"     ❌ Failed: {e}")
            continue

    avg_confidence = total_confidence / len(enriched_nouns) if enriched_nouns else 0
    avg_words = total_words / len(enriched_nouns) if enriched_nouns else 0

    print(".2f")
    print(".1f")
    # 3. Generate embeddings and test similarities
    print("\n3. 🧮 Testing embedding similarities...")

    try:
        client = get_lmstudio_client()

        # Build document strings
        doc_strings = []
        for noun in enriched_nouns:
            doc = _build_document_string(noun)
            doc_strings.append(doc)

        print(f"   Generated {len(doc_strings)} document strings")

        # Get embeddings
        embeddings = client.get_embeddings(doc_strings)
        embeddings = [_l2_normalize(vec) for vec in embeddings]

        print(f"   Generated {len(embeddings)} embeddings (dim: {len(embeddings[0]) if embeddings else 0})")

        # Test self-similarities (should be ~1.0)
        self_similarities = []
        for _i, emb in enumerate(embeddings):
            # Cosine similarity with itself should be 1.0
            self_sim = sum(a * b for a, b in zip(emb, emb, strict=False))
            self_similarities.append(self_sim)

        mean_self_sim = statistics.mean(self_similarities)

        # Test top-5 similarities across all pairs
        import numpy as np  # noqa: E402

        X = np.vstack(embeddings)
        sim_matrix = X @ X.T  # Cosine similarities

        # Get average of top-5 similarities for each node (excluding self)
        top5_similarities = []
        for i in range(len(embeddings)):
            similarities = sim_matrix[i]
            # Exclude self-similarity
            other_sims = [sim for j, sim in enumerate(similarities) if j != i]
            if other_sims:
                top5 = sorted(other_sims, reverse=True)[:5]
                top5_similarities.extend(top5)

        avg_top5_sim = statistics.mean(top5_similarities) if top5_similarities else 0

        print(".4f")
        print(".4f")
        # 4. Test edge counts at different thresholds
        print("\n4. 🔗 Testing edge quality thresholds...")

        # Create mock IDs for testing
        ids = [f"id_{i}" for i in range(len(embeddings))]

        # Test exploration threshold (0.4)
        pairs_0_4 = _knn_pairs(embeddings, ids, k=5)  # k=5 for meaningful connections
        exploration_edges = len(pairs_0_4)

        # Count KPI edges (≥0.75 and ≥0.90)
        weak_edges = sum(1 for _, _, sim in pairs_0_4 if sim >= 0.75)
        strong_edges = sum(1 for _, _, sim in pairs_0_4 if sim >= 0.90)

        print(f"   Exploration edges (≥0.4): {exploration_edges}")
        print(f"   KPI weak edges (≥0.75): {weak_edges}")
        print(f"   KPI strong edges (≥0.90): {strong_edges}")

        # 5. Test reranker YES rates at different thresholds
        print("\n5. 🎯 Testing reranker decision thresholds...")

        # Mock reranker scores (normally from actual reranker)
        # For testing, we'll use similarity scores as proxy
        mock_rerank_scores = [sim for _, _, sim in pairs_0_4]

        if mock_rerank_scores:
            yes_at_02 = sum(1 for s in mock_rerank_scores if s >= 0.2) / len(mock_rerank_scores)
            yes_at_04 = sum(1 for s in mock_rerank_scores if s >= 0.4) / len(mock_rerank_scores)
            yes_at_06 = sum(1 for s in mock_rerank_scores if s >= 0.6) / len(mock_rerank_scores)

            print(".2f")
            print(".2f")
            print(".2f")
        # Summary report
        print("\n" + "=" * 50)
        print("📊 SANITY CHECK RESULTS")
        print("=" * 50)

        print(f"\n1. Mean self-similarity: {mean_self_sim:.4f}")
        print(f"2. Avg top-5 cosine similarity: {avg_top5_sim:.4f}")
        print("3. Edge counts:")
        print(f"   - ≥0.90 (strong KPI): {strong_edges}")
        print(f"   - ≥0.75 (weak KPI): {weak_edges}")
        print("4. Reranker YES rates:")
        print(f"   - At 0.2 cut: {yes_at_02 if mock_rerank_scores else 0:.1%}")
        print(f"   - At 0.4 cut: {yes_at_04 if mock_rerank_scores else 0:.1%}")
        print(f"   - At 0.6 cut: {yes_at_06 if mock_rerank_scores else 0:.1%}")
        print("5. Enrichment quality:")
        print(f"   - Avg words per insight: {avg_words:.1f}")
        print(f"   - Avg external confidence: {avg_confidence:.3f}")

        # Quality assessment
        issues = []
        if abs(mean_self_sim - 1.0) > 0.01:
            issues.append("Self-similarity not ~1.0")
        if avg_top5_sim < 0.5:
            issues.append("Top-5 similarities too low")
        if avg_confidence < 0.9:
            issues.append("AI confidence below 0.9 threshold")
        if avg_words < 150:
            issues.append("Insights too short (<150 words)")
        if strong_edges == 0:
            issues.append("No strong edges found")
        if weak_edges < strong_edges * 2:
            issues.append("Weak edges count suspicious")

        if issues:
            print("\n⚠️  QUALITY ISSUES DETECTED:")
            for issue in issues:
                print(f"   • {issue}")
        else:
            print("\n✅ ALL QUALITY METRICS LOOK GOOD")

    except Exception as e:
        print(f"   ❌ Embedding test failed: {e}")
        import traceback  # noqa: E402

        traceback.print_exc()


if __name__ == "__main__":
    test_genesis_chapter_1()
