#!/usr/bin/env python3
"""
Build graph from AI-enriched nouns.

Reads exports/ai_nouns.enriched.json and creates exports/graph_latest.json
following the gematria/graph.v1 schema.
"""

import json
import os
from pathlib import Path

# Add src to path
script_dir = Path(__file__).parent
project_root = script_dir.parent
src_dir = project_root / "src"
import sys

sys.path.insert(0, str(src_dir))

from src.infra.env_loader import ensure_env_loaded
from src.infra.structured_logger import get_logger, log_json

# Load environment
ensure_env_loaded()
LOG = get_logger("build_graph_from_ai_nouns")


def build_graph_from_enriched_nouns():
    """Build graph from enriched nouns file."""
    enriched_path = "exports/ai_nouns.enriched.json"
    output_path = "exports/graph_latest.json"

    if not os.path.exists(enriched_path):
        LOG.error(f"Enriched nouns file not found: {enriched_path}")
        return False

    # Read enriched nouns
    with open(enriched_path, encoding="utf-8") as f:
        enriched_data = json.load(f)

    enriched_nouns = enriched_data.get("nodes", [])
    log_json(LOG, 20, "loaded_enriched_nouns", count=len(enriched_nouns))

    # Build graph nodes
    nodes = []
    for noun in enriched_nouns:
        node = {
            "id": noun["noun_id"],
            "surface": noun["surface"],
            "hebrew": noun["surface"],  # For compatibility
            "gematria": noun["gematria"],
            "class": noun["class"],
            "book": noun.get("book", "Unknown"),
            "analysis": noun.get("analysis", ""),
        }
        # Add enrichment data if available
        if "enrichment" in noun:
            node["enrichment"] = noun["enrichment"]
        nodes.append(node)

    # For now, create empty edges (relationships will be added by network_aggregator)
    edges = []

    # Create graph structure
    graph = {
        "schema": "gematria/graph.v1",
        "book": enriched_data.get("book", "Unknown"),
        "generated_at": enriched_data.get("generated_at", ""),
        "nodes": nodes,
        "edges": edges,
        "metadata": {"node_count": len(nodes), "edge_count": len(edges), "source": "ai_enriched_nouns"},
    }

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Write graph
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)

    log_json(LOG, 20, "graph_built", nodes=len(nodes), edges=len(edges))
    print(f"GRAPH_BUILT {len(nodes)} nodes, {len(edges)} edges to {output_path}")
    return True


if __name__ == "__main__":
    success = build_graph_from_enriched_nouns()
    sys.exit(0 if success else 1)
