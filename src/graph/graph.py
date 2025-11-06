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
from src.nodes import collect_nouns
from src.nodes import validate_batch
from src.nodes import confidence_validator
from src.nodes import schema_validator
from src.nodes import analysis_runner
from src.nodes import wrap_hints
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


def _normalize_state(x):
    # Some nodes may return (state, meta). Normalize to dict state.
    return x[0] if isinstance(x, tuple) else x


def run_pipeline(book: str, nouns: list | None = None) -> dict:
    """
    Orchestrates the canonical pipeline.
    """
    state = {"book": book}
    if nouns:
        state["nouns"] = nouns

    state = _normalize_state(collect_nouns.collect_nouns_node(state))
    state = _normalize_state(validate_batch.validate_batch_node(state))
    state = _normalize_state(enrichment_node(state))
    state = _normalize_state(confidence_validator.confidence_validator_node(state))
    state = _normalize_state(network_aggregator.network_aggregator_node(state))
    state = _normalize_state(schema_validator.schema_validator_node(state))
    state = _normalize_state(analysis_runner.analysis_runner_node(state))
    state = _normalize_state(wrap_hints.wrap_hints_node(state))
    return state


def main():
    book = os.getenv("BOOK", "Genesis")
    run_pipeline(book=book, nouns=None)


if __name__ == "__main__":
    main()


# LangGraph interface removed - pipeline is now direct execution
def get_graph():
    """Legacy function - pipeline now runs directly via run_pipeline()"""
    return None
