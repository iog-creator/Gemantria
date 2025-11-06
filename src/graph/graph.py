"""
LangGraph pipeline orchestration and execution engine.
Coordinates AI-driven noun discovery, enrichment, and network building.

Related Rules: Rule-039 (Execution Contract), Rule-050 (OPS Contract), Rule-058 (Auto-Housekeeping)
Related ADRs: ADR-032 (Organic AI Discovery), ADR-019 (Data Contracts)
"""

from __future__ import annotations

from typing import Any, TypedDict, Dict, List

from langgraph.graph import StateGraph

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
    save_checkpoint,
    get_model_versions,
    get_schema_version,
)
from src.persist.runs_ledger import mark_run_started, mark_run_finished

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


def main(state: PipelineState) -> PipelineState:
    run_id = state.get("run_id", "")

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

    # Save checkpoint after ai.nouns
    save_checkpoint(run_id, "ai.nouns", {"nouns": state["nouns"], "metrics": state["metrics"]})

    # 2. Validate and weigh nouns (placeholder - function not implemented)
    state["weighted_nouns"] = state["nouns"]  # Pass through for now
    state["validated_nouns"] = state["weighted_nouns"]  # Set validated nouns for enrichment

    # 3. Enrich nouns with theological insights
    state, _ = enrichment_node(state)

    # Normalize enriched nouns using SSOT adapter at enrichment boundary
    state["enriched_nouns"] = [adapt_ai_noun(n) for n in state.get("enriched_nouns", [])]

    # Save checkpoint after ai.enrich
    save_checkpoint(run_id, "ai.enrich", {"enriched_nouns": state["enriched_nouns"]})

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

    # 5. Network aggregation (graph.build)
    # Use the network_aggregator_node to build the network
    state = network_aggregator.network_aggregator_node(state)
    state["graph"] = state.get("network_summary", {})

    # Save checkpoint after graph.build
    save_checkpoint(run_id, "graph.build", {"graph": state["graph"]})

    # 6. Graph scoring (graph.score)
    # Apply SSOT blend thresholds and classify edges
    state = graph_scorer_node(state)
    state["scored_graph"] = state.get("graph", {})

    # Save checkpoint after graph.score
    save_checkpoint(run_id, "graph.score", {"scored_graph": state["scored_graph"]})

    # Return final state
    return state


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

    # Optional: record run start (tolerant if DSN missing)
    try:
        mark_run_started(run_id, book, notes="langgraph pipeline")
    except Exception as e:
        print(f"[runs_ledger.start] WARN: {e}")

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

    try:
        # Run the pipeline
        final_state = main(initial_state)

        # Update run status to completed
        from datetime import datetime

        update_run_status(run_id, "completed", finished_at=datetime.utcnow())

        # Finish marker (always tolerant)
        try:
            mark_run_finished(run_id, notes="ok")
        except Exception as e:
            print(f"[runs_ledger.finish] WARN: {e}")

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
        # Optional: mark run finished with error (tolerant)
        try:
            mark_run_finished(run_id, notes=f"error: {str(e)[:100]}")
        except Exception as finish_e:
            print(f"[runs_ledger.finish] WARN: {finish_e}")
        return {
            "run_id": initial_state.get("run_id"),
            "book": book,
            "mode": mode,
            "success": False,
            "error": str(e),
        }


def get_graph() -> StateGraph:
    workflow = StateGraph(PipelineState)

    # The single node `main` encapsulates the entire pipeline logic
    workflow.add_node("main", main)

    # The pipeline starts and ends with the `main` node
    workflow.set_entry_point("main")
    workflow.set_finish_point("main")

    return workflow.compile()
