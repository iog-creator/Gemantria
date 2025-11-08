# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

"""
Graph Scoring Node

Applies SSOT blend thresholds and classifies edges with cosine/rerank scoring.
"""

from src.graph.state import PipelineState
from src.rerank.blender import blend_strength, classify_strength


def graph_scorer_node(state: PipelineState) -> PipelineState:
    """
    Score and classify graph edges using SSOT blend formula.

    Applies edge_strength = a*cosine + (1-a)*rerank_score
    and classifies edges as strong/weak/other.
    """
    ts = state.get("ts")
    graph = dict(state.get("graph", {}) or {})
    edges = list(graph.get("edges", []) or [])

    if not edges:
        # Ensure we keep a stable graph structure while preserving ts metadata.
        state["graph"] = {**graph, "edges": []}
        if ts is not None:
            state["ts"] = ts
        return state

    scored_edges = []
    for edge in edges:
        # Extract scores (handle missing values gracefully)
        cosine = edge.get("cosine", edge.get("weight", 0.0))
        rerank_score = edge.get("rerank_score", 0.0)

        # Compute blended strength
        edge_strength = blend_strength(float(cosine), float(rerank_score))

        # Classify edge
        edge_class = classify_strength(edge_strength)

        # Create scored edge
        scored_edge = {
            **edge,
            "cosine": float(cosine),
            "rerank_score": float(rerank_score),
            "edge_strength": edge_strength,
            "class": edge_class,
        }
        scored_edges.append(scored_edge)

    # Update graph with scored edges
    state["graph"] = {
        **graph,
        "edges": scored_edges,
    }
    if ts is not None:
        state["ts"] = ts

    return state
