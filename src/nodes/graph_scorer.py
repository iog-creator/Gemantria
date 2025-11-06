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
    graph = state.get("graph", {})
    edges = graph.get("edges", [])

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

    return state
