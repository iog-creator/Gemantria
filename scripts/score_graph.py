#!/usr/bin/env python3
# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

"""
Graph Scoring Script (Phase 10 - Correlation Visualization)

Loads exports/graph_latest.json, applies SSOT blend formula (Rule 045),
and writes exports/graph_latest.scored.json with edge_strength and class fields.

This script implements the make graph.score target for Phase 10.
"""

from __future__ import annotations

import json
import pathlib
import sys
from datetime import UTC, datetime

# Add project root to path for imports
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from src.rerank.blender import blend_strength, classify_strength


def load_graph(input_path: pathlib.Path) -> dict:
    """Load graph JSON from file."""
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(input_path.read_text(encoding="utf-8"))
        return data
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {input_path}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to load {input_path}: {e}", file=sys.stderr)
        sys.exit(1)


def score_edges(edges: list[dict]) -> list[dict]:
    """
    Score edges using SSOT blend formula (Rule 045).

    Applies: edge_strength = alpha*cosine + (1-alpha)*rerank_score
    Classifies: strong (>=0.90), weak (>=0.75), other (<0.75)
    """
    scored_edges = []

    for edge in edges:
        # Extract scores (handle missing values gracefully)
        # Support both 'cosine' and legacy 'weight' field names
        cosine = edge.get("cosine", edge.get("weight", edge.get("similarity", 0.0)))
        rerank_score = edge.get("rerank_score", edge.get("rerank", 0.0))

        # Ensure numeric types
        cosine = float(cosine) if cosine is not None else 0.0
        rerank_score = float(rerank_score) if rerank_score is not None else 0.0

        # Compute blended strength using SSOT formula (Rule 045)
        edge_strength = blend_strength(cosine, rerank_score)

        # Classify edge strength
        edge_class = classify_strength(edge_strength)

        # Create scored edge (preserve all original fields, add scoring fields)
        scored_edge = {
            **edge,  # Preserve all original fields
            "cosine": cosine,
            "rerank_score": rerank_score,
            "edge_strength": edge_strength,
            "class": edge_class,
        }
        scored_edges.append(scored_edge)

    return scored_edges


def main() -> int:
    """Main scoring pipeline."""
    # Input/output paths
    input_path = pathlib.Path("exports/graph_latest.json")
    output_path = pathlib.Path("exports/graph_latest.scored.json")

    # Check if input exists
    if not input_path.exists():
        print(f"HINT: Input file not found: {input_path}", file=sys.stderr)
        print("HINT: Run 'make graph.build' first to generate graph_latest.json", file=sys.stderr)
        return 1

    # Load graph
    print(f"Loading graph from {input_path}...")
    graph_data = load_graph(input_path)

    # Extract edges
    edges = graph_data.get("edges", [])
    print(f"Found {len(edges)} edges to score")

    if not edges:
        print("HINT: No edges to score (empty graph)")
        # Still write output with empty edges to maintain contract
        scored_edges = []
    else:
        # Score edges
        print("Scoring edges with SSOT blend formula (Rule 045)...")
        scored_edges = score_edges(edges)

        # Report scoring statistics
        strong_count = sum(1 for e in scored_edges if e.get("class") == "strong")
        weak_count = sum(1 for e in scored_edges if e.get("class") == "weak")
        other_count = sum(1 for e in scored_edges if e.get("class") == "other")
        print(f"Edge classification: {strong_count} strong, {weak_count} weak, {other_count} other")

    # Build output graph (preserve all metadata)
    output_graph = {
        **graph_data,  # Preserve schema, book, nodes, metadata, etc.
        "edges": scored_edges,
    }

    # Update metadata to indicate scoring
    if "metadata" not in output_graph:
        output_graph["metadata"] = {}
    output_graph["metadata"]["scored"] = True
    output_graph["metadata"]["scoring_timestamp"] = datetime.now(UTC).isoformat()
    output_graph["metadata"]["source"] = output_graph["metadata"].get("source", "file_first")

    # Update generated_at timestamp (RFC3339)
    output_graph["generated_at"] = datetime.now(UTC).isoformat()

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write scored graph
    print(f"Writing scored graph to {output_path}...")
    output_path.write_text(
        json.dumps(output_graph, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"OK: Scored graph written to {output_path}")
    print(f"    Nodes: {len(graph_data.get('nodes', []))}")
    print(f"    Edges: {len(scored_edges)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
