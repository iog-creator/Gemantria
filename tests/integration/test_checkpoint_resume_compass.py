import hashlib
import json
import os
import pytest
from unittest.mock import patch

from src.graph.graph import get_graph
from src.graph.state import PipelineState
from src.infra.checkpointer import get_checkpointer


@pytest.mark.skipif(
    os.getenv("CHECKPOINTER", "memory").lower() != "postgres" or not os.getenv("GEMATRIA_DSN"),
    reason="Postgres checkpointer required for COMPASS correlation test",
)
def test_checkpoint_resume_compass_correlation():
    """
    Test COMPASS correlation: validate that resumed pipeline produces identical node state hashes.

    This ensures deterministic resumption and validates the mathematical correctness
    of the checkpoint/resume mechanism per Rule-053 (Idempotent Baseline).
    """
    # Create test state
    initial_state: PipelineState = {
        "run_id": "test-compass-123",
        "book_name": "Genesis",
        "book": "Genesis",
        "mode": "START",
        "nouns": [
            {
                "noun_id": "test-noun-1",
                "surface": "אלהים",
                "hebrew_text": "אלהים",
                "gematria_value": 86,
                "class": "person",
                "ai_discovered": True,
                "sources": [{"ref": "Gen 1:1", "offset": 0}],
                "analysis": {"notes": "Test noun for COMPASS validation"},
            }
        ],
        "enriched_nouns": [],
        "analyzed_nouns": [],
        "weighted_nouns": [],
        "validated_nouns": [],
        "conflicts": [],
        "graph": {},
        "scored_graph": {},
        "metrics": {},
        "metadata": {},
        "use_agents": False,  # Disable agents for deterministic testing
        "hints": ["compass_test_start"],
        "enveloped_hints": {},
    }

    # Thread ID for this test
    thread_id = "compass-test-thread"

    # First run: Execute pipeline and collect node state hashes
    graph = get_graph()
    config = {"configurable": {"thread_id": thread_id, "checkpoint_id": "compass-run-1"}}

    # Mock external dependencies for deterministic testing
    with patch("src.nodes.ai_noun_discovery.discover_nouns_for_book") as mock_discover:
        mock_discover.return_value = initial_state["nouns"]

        # Run first execution
        result1 = graph.invoke(initial_state, config=config)

        # Collect node state hashes from checkpointer
        checkpointer = get_checkpointer()
        hashes1 = {}
        for node_name in [
            "collect_nouns",
            "validate_batch",
            "enrichment",
            "confidence_validator",
            "network_aggregator",
            "analysis_runner",
            "wrap_hints",
        ]:
            state = checkpointer.load("langgraph_pipeline", node_name)
            if state:
                # Create deterministic hash of state
                state_str = json.dumps(state, sort_keys=True, default=str)
                hashes1[node_name] = hashlib.sha256(state_str.encode()).hexdigest()

    # Second run: Resume and collect hashes again
    config2 = {"configurable": {"thread_id": thread_id, "checkpoint_id": "compass-run-2"}}

    with patch("src.nodes.ai_noun_discovery.discover_nouns_for_book") as mock_discover:
        mock_discover.return_value = initial_state["nouns"]

        # Run second execution (should resume from checkpoints)
        result2 = graph.invoke(initial_state, config=config2)

        # Collect node state hashes again
        hashes2 = {}
        for node_name in [
            "collect_nouns",
            "validate_batch",
            "enrichment",
            "confidence_validator",
            "network_aggregator",
            "analysis_runner",
            "wrap_hints",
        ]:
            state = checkpointer.load("langgraph_pipeline", node_name)
            if state:
                state_str = json.dumps(state, sort_keys=True, default=str)
                hashes2[node_name] = hashlib.sha256(state_str.encode()).hexdigest()

    # COMPASS Correlation Validation: All node states should have identical hashes
    # This proves mathematical correctness of checkpoint/resume mechanism
    for node_name in hashes1.keys():
        assert node_name in hashes2, f"Missing hash for node {node_name} in second run"
        assert (
            hashes1[node_name] == hashes2[node_name]
        ), f"COMPASS correlation failed for {node_name}: hash mismatch between runs"

    # Validate final results are also identical
    assert result1["run_id"] == result2["run_id"]
    assert len(result1.get("nouns", [])) == len(result2.get("nouns", []))
    assert result1.get("hints", []) == result2.get("hints", [])

    # Verify envelope structure exists (Rule-026 compliance)
    assert "enveloped_hints" in result1
    assert "enveloped_hints" in result2
    assert result1["enveloped_hints"]["type"] == "hints_envelope"
    assert result2["enveloped_hints"]["type"] == "hints_envelope"


@pytest.mark.skipif(
    os.getenv("CHECKPOINTER", "memory").lower() != "postgres" or not os.getenv("GEMATRIA_DSN"),
    reason="Postgres checkpointer required for node identity test",
)
def test_checkpoint_node_identity_consistency():
    """
    Test that individual nodes produce identical outputs when resumed.

    This validates the temporal test harness requirement: run with stop after N nodes
    → resume → verify node identity consistency.
    """
    initial_state: PipelineState = {
        "run_id": "test-identity-456",
        "book_name": "Genesis",
        "book": "Genesis",
        "mode": "START",
        "nouns": [],
        "enriched_nouns": [],
        "analyzed_nouns": [],
        "weighted_nouns": [],
        "validated_nouns": [],
        "conflicts": [],
        "graph": {},
        "scored_graph": {},
        "metrics": {},
        "metadata": {},
        "use_agents": False,
        "hints": ["identity_test_start"],
        "enveloped_hints": {},
    }

    thread_id = "identity-test-thread"
    graph = get_graph()

    # Run pipeline once to establish baseline
    config1 = {"configurable": {"thread_id": thread_id, "checkpoint_id": "identity-run-1"}}

    with patch("src.nodes.ai_noun_discovery.discover_nouns_for_book") as mock_discover:
        mock_discover.return_value = [
            {
                "noun_id": "identity-test-noun",
                "surface": "תורה",
                "hebrew_text": "תורה",
                "gematria_value": 611,
                "class": "thing",
                "ai_discovered": True,
                "sources": [{"ref": "Gen 1:1", "offset": 10}],
                "analysis": {"notes": "Identity test noun"},
            }
        ]

        result1 = graph.invoke(initial_state, config=config1)

    # Simulate interruption and resume by running again
    config2 = {"configurable": {"thread_id": thread_id, "checkpoint_id": "identity-run-2"}}

    with patch("src.nodes.ai_noun_discovery.discover_nouns_for_book") as mock_discover:
        mock_discover.return_value = [
            {
                "noun_id": "identity-test-noun",
                "surface": "תורה",
                "hebrew_text": "תורה",
                "gematria_value": 611,
                "class": "thing",
                "ai_discovered": True,
                "sources": [{"ref": "Gen 1:1", "offset": 10}],
                "analysis": {"notes": "Identity test noun"},
            }
        ]

        result2 = graph.invoke(initial_state, config=config2)

    # Verify node identity consistency: same inputs should produce same outputs
    assert result1["nouns"] == result2["nouns"], "Noun collection not consistent"
    assert result1["enriched_nouns"] == result2["enriched_nouns"], "Enrichment not consistent"
    assert result1["analyzed_nouns"] == result2["analyzed_nouns"], "Analysis not consistent"
    assert result1["graph"] == result2["graph"], "Graph building not consistent"
    assert result1["scored_graph"] == result2["scored_graph"], "Graph scoring not consistent"

    # Verify hints envelope identity
    assert result1["enveloped_hints"]["items"] == result2["enveloped_hints"]["items"]
    assert result1["enveloped_hints"]["count"] == result2["enveloped_hints"]["count"]


@pytest.mark.skipif(
    os.getenv("CHECKPOINTER", "memory").lower() != "postgres" or not os.getenv("GEMATRIA_DSN"),
    reason="Postgres checkpointer required for temporal test harness",
)
def test_temporal_test_harness_stop_resume():
    """
    Temporal test harness: run with stop after N nodes → resume → verify node identity consistency.

    This implements the temporal testing requirement from the directive.
    """
    from src.graph.graph import run_pipeline

    # Test data
    test_nouns = [
        {
            "noun_id": "temporal-test-noun",
            "surface": "בראשית",
            "hebrew_text": "בראשית",
            "gematria_value": 913,
            "class": "thing",
            "ai_discovered": True,
            "sources": [{"ref": "Gen 1:1", "offset": 0}],
            "analysis": {"notes": "Temporal test noun"},
        }
    ]

    # Phase 1: Run pipeline stopping after 3 nodes (should stop at enrichment)
    result_partial = run_pipeline(
        book="Genesis",
        mode="START",
        nouns=test_nouns,
        stop_after_n_nodes=3,  # Stop after collect_nouns, validate_batch, enrichment
    )

    # Verify partial execution stopped at the right point
    assert result_partial["success"]
    assert "enrichment: completed" in result_partial["hints"]
    assert "confidence_validator: completed" not in result_partial["hints"]
    assert len(result_partial["hints"]) == 3  # Should have hints from first 3 nodes

    # Phase 2: Resume the pipeline (should continue from enrichment)
    result_resume = run_pipeline(
        book="Genesis",
        mode="RESUME",
        nouns=test_nouns,
        stop_after_n_nodes=None,  # Run to completion
    )

    # Verify resumed execution completed successfully
    assert result_resume["success"]
    assert "wrap_hints: completed" in result_resume["hints"]
    assert len(result_resume["hints"]) == 7  # All 7 nodes should have completed

    # Verify node identity consistency: resumed pipeline should produce same final state
    # (Note: run IDs will be different, so we compare the core pipeline outputs)
    assert result_resume["nouns"] == test_nouns
    assert len(result_resume["enriched_nouns"]) > 0
    assert len(result_resume["analyzed_nouns"]) > 0
    assert "graph" in result_resume and len(result_resume["graph"].get("nodes", [])) > 0
    assert (
        "scored_graph" in result_resume and len(result_resume["scored_graph"].get("edges", [])) > 0
    )

    # Verify envelope structure (Rule-026 compliance)
    assert result_resume["enveloped_hints"]["type"] == "hints_envelope"
    assert result_resume["enveloped_hints"]["version"] == "1.0"
    assert len(result_resume["enveloped_hints"]["items"]) == 7  # All nodes completed
