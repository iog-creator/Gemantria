#!/usr/bin/env python3
# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="file_first")
"""Graph Statistics Calculator (Phase 10 - Rule 022)

Calculates required metrics from exports/graph_latest.scored.json:
- nodes, edges, clusters, density
- centrality.avg_degree, centrality.avg_betweenness

Uses NetworkX for graph analysis and Louvain communities for clustering.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
from datetime import UTC, datetime

try:
    import networkx as nx  # type: ignore[import]
    from networkx.algorithms.community import louvain_communities  # type: ignore[import]
except ImportError:
    print("ERROR: networkx not installed. Install with: pip install networkx")
    sys.exit(1)


def build_graph_from_json(nodes: list[dict], edges: list[dict]) -> nx.Graph:
    """Build NetworkX graph from JSON nodes and edges."""
    G = nx.Graph()

    # Extract node IDs
    node_ids = set()
    for node in nodes:
        node_id = node.get("id") or node.get("noun_id")
        if node_id:
            node_ids.add(str(node_id))
            G.add_node(str(node_id))

    # Add edges with weights
    for edge in edges:
        # Support both "source/target" and "src/dst" formats
        source = edge.get("source") or edge.get("src")
        target = edge.get("target") or edge.get("dst")

        if source and target and str(source) in node_ids and str(target) in node_ids:
            # Use edge_strength if available, otherwise cosine, otherwise 0.0
            weight = edge.get("edge_strength") or edge.get("cosine") or 0.0
            try:
                weight = float(weight)
                weight = max(0.0, min(1.0, weight))  # Clamp to [0, 1]
            except (ValueError, TypeError):
                weight = 0.0

            G.add_edge(str(source), str(target), weight=weight)

    return G


def calculate_clusters(G: nx.Graph) -> int:
    """Calculate number of clusters using Louvain communities."""
    if G.number_of_nodes() == 0:
        return 0

    try:
        communities = louvain_communities(G, weight="weight", seed=42)
        return len(communities)
    except Exception:
        # Fallback: count connected components
        return nx.number_connected_components(G)


def calculate_centrality(G: nx.Graph) -> dict[str, float]:
    """Calculate average degree and betweenness centrality."""
    if G.number_of_nodes() == 0:
        return {"avg_degree": 0.0, "avg_betweenness": 0.0}

    # Degree centrality (normalized to 0-1)
    degree_centrality = nx.degree_centrality(G)
    avg_degree = sum(degree_centrality.values()) / len(degree_centrality) if degree_centrality else 0.0

    # Betweenness centrality (weighted, normalized)
    try:
        if G.number_of_edges() > 0:
            betweenness = nx.betweenness_centrality(G, weight="weight", normalized=True)
        else:
            betweenness = {n: 0.0 for n in G.nodes()}
    except Exception:
        # Fallback: unweighted betweenness
        betweenness = nx.betweenness_centrality(G, normalized=True)

    avg_betweenness = sum(betweenness.values()) / len(betweenness) if betweenness else 0.0

    return {
        "avg_degree": round(float(avg_degree), 6),
        "avg_betweenness": round(float(avg_betweenness), 6),
    }


def main() -> int:
    """Main entry point for graph statistics calculation."""
    # Input file: prefer scored graph, fallback to unscored
    src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("exports/graph_latest.scored.json")

    if not src.exists():
        # Fall back to unscored graph
        src = pathlib.Path("exports/graph_latest.json")
        if not src.exists():
            print(f"ERROR: Graph file not found: {src}")
            return 1

    # Load graph data
    try:
        data = json.loads(src.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: Failed to load graph JSON: {e}")
        return 1

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    # Basic counts
    n, m = len(nodes), len(edges)

    # Build NetworkX graph
    G = build_graph_from_json(nodes, edges)

    # Calculate density (actual edges / possible edges)
    if n > 1:
        possible_edges = n * (n - 1) / 2
        density = min(1.0, m / possible_edges) if possible_edges > 0 else 0.0
    else:
        density = 0.0

    # Calculate clusters
    clusters = calculate_clusters(G)

    # Calculate centrality metrics
    centrality = calculate_centrality(G)

    # Build output (Rule 022 required fields)
    out = {
        "schema": "graph-stats.v1",
        "generated_at": datetime.now(UTC).isoformat(),  # RFC3339
        "pipeline_version": os.getenv("PIPELINE_VERSION", "dev"),
        "nodes": n,
        "edges": m,
        "clusters": clusters,
        "density": round(density, 6),
        "centrality": centrality,
        "metadata": {
            "source": "file_first",
            "input": str(src),
            "graph_nodes": G.number_of_nodes(),
            "graph_edges": G.number_of_edges(),
        },
    }

    # Write output
    output_path = pathlib.Path("exports/graph_stats.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"OK: wrote {output_path} from {src}")
    print(f"    nodes={n}, edges={m}, clusters={clusters}, density={density:.6f}")
    print(f"    avg_degree={centrality['avg_degree']:.6f}, avg_betweenness={centrality['avg_betweenness']:.6f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
