"""
LangGraph pipeline orchestration and execution engine.
Coordinates AI-driven noun discovery, enrichment, and network building.

Related Rules: Rule-039 (Execution Contract), Rule-050 (OPS Contract), Rule-058 (Auto-Housekeeping)
Related ADRs: ADR-032 (Organic AI Discovery), ADR-019 (Data Contracts)
"""

from __future__ import annotations

from typing import Any, TypedDict, Dict, List


from src.infra.env_loader import ensure_env_loaded
from src.graph.state import PipelineState
from src.nodes import network_aggregator
from src.nodes.enrichment import enrichment_node
from src.nodes.ai_noun_discovery import discover_nouns_for_book
from src.nodes.graph_scorer import graph_scorer_node
from src.services.expert_agent import analyze_theological
from src.ssot.noun_adapter import adapt_ai_noun
from src.infra.runs_ledger import (
    create_run,
    update_run_status,
    get_model_versions,
    get_schema_version,
)
from src.persist.checkpointer import get_checkpointer
import os

# Load environment variables from .env file
ensure_env_loaded()


class Graph(TypedDict):
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]


def build_graph(nouns: List[Dict]) -> Dict:
    """
    Nodes must expose Hebrew + gematria for downstream UI/analytics.
    Node.id = noun_id; keep book if present on inputs.
    """
    nodes = []
    for raw in nouns:
        n = adapt_ai_noun(raw)
        nodes.append(
            {
                "id": n["noun_id"],
                "surface": n["surface"],
                "hebrew": n["hebrew_text"],
                "gematria": n["gematria_value"],
                "class": n["class"],
            }
        )
    edges = []  # existing edge derivation unchanged
    return {"schema": "gemantria/graph.v1", "nodes": nodes, "edges": edges}


def run_pipeline(
    book: str = "Genesis", mode: str = "START", nouns: List[Dict[str, Any]] | None = None
) -> Dict[str, Any]:
    """
    Run the complete pipeline for a given book.

    Args:
        book: The book name to process
        mode: Processing mode (START, RESUME, etc.)
        nouns: Optional list of nouns to use instead of AI discovery

    Returns:
        Dictionary with pipeline results and metadata
    """
    # Create run in ledger
    versions = {
        "schema_version": get_schema_version(),
        "models": get_model_versions(),
    }
    run_id = create_run(book, versions)

    # Create initial state
    initial_state: PipelineState = {
        "run_id": run_id,
        "book_name": book,
        "book": book,  # DEPRECATED: for backwards compatibility
        "mode": mode,
        "nouns": nouns or [],
        "enriched_nouns": [],
        "analyzed_nouns": [],
        "weighted_nouns": [],
        "conflicts": [],
        "graph": {},
        "metrics": {},
        "metadata": {},
        "use_agents": True,  # Enable agentic processing by default
    }

    state = initial_state
    saver = get_checkpointer()
    run_id_for_saver = saver.start_run(book=book)

    try:
        # 1. Collect nouns (AI-driven discovery, or use provided nouns)
        if state.get("nouns"):
            # Nouns already provided (e.g., from file input)
            timing_samples = []
        else:
            # Discover nouns via AI
            state["nouns"], timing_samples = discover_nouns_for_book(state["book"])

        # Normalize nouns using SSOT adapter at discovery boundary
        state["nouns"] = [adapt_ai_noun(n) for n in state["nouns"]]

        # Log metrics
        state["metrics"]["ai_call_latencies_ms"] = timing_samples

        saver.save(run_id_for_saver, "collect_nouns", state)

        # 2. Validate and weigh nouns (placeholder - function not implemented)
        state["weighted_nouns"] = state["nouns"]  # Pass through for now
        state["validated_nouns"] = state["weighted_nouns"]  # Set validated nouns for enrichment

        saver.save(run_id_for_saver, "validate_batch", state)

        # 3. Enrich nouns with theological insights
        state, _ = enrichment_node(state)

        # Normalize enriched nouns using SSOT adapter at enrichment boundary
        state["enriched_nouns"] = [adapt_ai_noun(n) for n in state.get("enriched_nouns", [])]

        saver.save(run_id_for_saver, "enrichment", state)

        # 4. Expert agent analysis
        if state.get("use_agents"):
            enriched_nouns = state.get("enriched_nouns", [])
            analyzed_nouns_results = []
            for noun in enriched_nouns:
                analyzed_noun = analyze_theological(noun)
                analyzed_nouns_results.append(analyzed_noun)
            state["analyzed_nouns"] = analyzed_nouns_results
        else:
            # If agents are not used, pass enriched nouns directly
            state["analyzed_nouns"] = state.get("enriched_nouns", [])

        saver.save(run_id_for_saver, "confidence_validator", state)

        # 5. Network aggregation (graph.build)
        # Use the network_aggregator_node to build the network
        state = network_aggregator.network_aggregator_node(state)
        state["graph"] = state.get("network_summary", {})

        saver.save(run_id_for_saver, "network_aggregator", state)

        # 6. Graph scoring (graph.score)
        # Apply SSOT blend thresholds and classify edges
        state = graph_scorer_node(state)
        state["scored_graph"] = state.get("graph", {})

        saver.save(run_id_for_saver, "graph_scorer", state)

        # Persist centrality if present (tolerant to missing keys)
        try:
            import psycopg  # type: ignore

            if os.getenv("CHECKPOINTER", "memory").lower() == "postgres" and os.getenv("GEMATRIA_DSN"):
                central = state.get("centrality") or (state.get("stats") or {}).get("centrality")
                if central and isinstance(central, dict):
                    dsn = os.getenv("GEMATRIA_DSN")
                    with psycopg.connect(dsn) as c, c.cursor() as cur:
                        for cid, vals in central.items():
                            cur.execute(
                                "INSERT INTO gematria.concept_centrality(concept_id, degree, betweenness, eigenvector, run_id) "
                                "VALUES (%s,%s,%s,%s,%s)",
                                (
                                    cid,
                                    vals.get("degree"),
                                    vals.get("betweenness"),
                                    vals.get("eigenvector"),
                                    run_id_for_saver,
                                ),
                            )
        except Exception:
            # non-fatal; analysis still usable even if persistence is skipped
            pass

        saver.save(run_id_for_saver, "analysis_runner", state)

        # Wrap hints
        # TODO: implement wrap_hints_node
        saver.save(run_id_for_saver, "wrap_hints", state)

        saver.finish(run_id_for_saver, status="ok")

        # Run the pipeline
        final_state = state

        # Update run status to completed
        from datetime import datetime

        update_run_status(run_id, "completed", finished_at=datetime.utcnow())

        # Return results
        return {
            "run_id": final_state.get("run_id"),
            "book": book,
            "mode": mode,
            "success": True,
            "nouns_count": len(final_state.get("nouns", [])),
            "graph_nodes": len(final_state.get("graph", {}).get("nodes", [])),
            "graph_edges": len(final_state.get("graph", {}).get("edges", [])),
            "metrics": final_state.get("metrics", {}),
        }

    except Exception as e:
        # Update run status to failed
        update_run_status(run_id, "failed")
        return {
            "run_id": initial_state.get("run_id"),
            "book": book,
            "mode": mode,
            "success": False,
            "error": str(e),
        }


# LangGraph interface removed - pipeline is now direct execution
def get_graph():
    """Legacy function - pipeline now runs directly via run_pipeline()"""
    return None
