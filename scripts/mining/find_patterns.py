"""
Phase 12: Advanced Pattern Mining
Discovers deep semantic patterns across the biblical text using graph structure.
"""

import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any
import uuid

import networkx as nx
from networkx.algorithms.community import louvain_communities

# Add project root to path for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.config.env import get_rw_dsn  # noqa: E402

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def build_graph_from_json(graph_data: Dict[str, Any]) -> nx.Graph:
    """
    Build NetworkX graph from graph_latest.json structure.

    Args:
        graph_data: Graph data with 'nodes' and 'edges' keys

    Returns:
        NetworkX graph with nodes and weighted edges
    """
    G = nx.Graph()

    # Add nodes
    nodes = graph_data.get("nodes", [])
    for node in nodes:
        node_id = node.get("id", str(uuid.uuid4()))
        G.add_node(node_id, **node)

    # Add edges
    edges = graph_data.get("edges", [])
    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        weight = edge.get("edge_strength", edge.get("similarity", 0.5))
        if source and target:
            G.add_edge(source, target, weight=weight, **edge)

    logger.info(f"Built graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    return G


def find_patterns(graph_latest: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Core logic for Phase 12 Advanced Pattern Mining.
    Builds NetworkX graph and computes patterns (Louvain clustering, centrality) before persisting.

    Args:
        graph_latest: Graph data structure from graph_latest.json

    Returns:
        List of discovered patterns with metadata
    """
    logger.info("STATUS: Initializing Pattern Mining Engine...")

    # 1. Build NetworkX graph from input
    G = build_graph_from_json(graph_latest)

    if G.number_of_nodes() == 0:
        logger.warning("Empty graph - no patterns to discover")
        return []

    # 2. Run Louvain community detection
    logger.info("Running Louvain community detection...")
    communities = louvain_communities(G, weight="weight", seed=42)
    cluster_map = {}
    for idx, community in enumerate(communities):
        for node in community:
            cluster_map[node] = idx

    logger.info(f"Found {len(communities)} communities")

    # 3. Calculate centrality measures
    logger.info("Calculating centrality measures...")
    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G, weight="weight")

    # 4. Build pattern results
    patterns = []

    # Create a pattern for each community
    for idx, community in enumerate(communities):
        community_nodes = list(community)
        if len(community_nodes) < 2:
            continue  # Skip single-node communities

        pattern = {
            "id": str(uuid.uuid4()),
            "name": f"community_{idx}",
            "type": "louvain_community",
            "definition": {
                "node_count": len(community_nodes),
                "node_ids": community_nodes[:10],  # Sample for storage
                "algorithm": "louvain",
                "seed": 42,
            },
            "metadata": {
                "avg_degree_centrality": sum(degree_centrality[n] for n in community_nodes) / len(community_nodes),
                "avg_betweenness_centrality": sum(betweenness_centrality[n] for n in community_nodes)
                / len(community_nodes),
            },
            "occurrences": community_nodes,
        }
        patterns.append(pattern)

    logger.info(f"Generated {len(patterns)} patterns from communities")

    # 5. Find maximal cliques (dense subgraphs)
    logger.info("Finding maximal cliques...")
    cliques = list(nx.find_cliques(G))
    clique_count = 0
    for idx, clique in enumerate(cliques):
        if len(clique) >= 3:  # Only store cliques with 3+ nodes
            pattern = {
                "id": str(uuid.uuid4()),
                "name": f"clique_{idx}",
                "type": "maximal_clique",
                "definition": {"node_count": len(clique), "node_ids": list(clique), "algorithm": "find_cliques"},
                "metadata": {
                    "is_complete": True,  # Cliques are complete subgraphs
                },
                "occurrences": list(clique),
            }
            patterns.append(pattern)
            clique_count += 1

    logger.info(f"Found {clique_count} maximal cliques (size >= 3)")

    # 6. Find triangle motifs (3-cycles)
    logger.info("Finding triangle motifs...")
    triangles = []
    for node in G.nodes():
        neighbors = set(G.neighbors(node))
        for neighbor1 in neighbors:
            for neighbor2 in neighbors:
                if neighbor1 < neighbor2 and G.has_edge(neighbor1, neighbor2):
                    triangle = sorted([node, neighbor1, neighbor2])
                    if triangle not in triangles:
                        triangles.append(triangle)

    for idx, triangle in enumerate(triangles):
        pattern = {
            "id": str(uuid.uuid4()),
            "name": f"triangle_{idx}",
            "type": "triangle_motif",
            "definition": {"node_count": 3, "node_ids": triangle, "algorithm": "cycle_detection"},
            "metadata": {
                "motif_type": "triangle",
            },
            "occurrences": triangle,
        }
        patterns.append(pattern)

    logger.info(f"Found {len(triangles)} triangle motifs")

    # 7. Persist to database
    persisted_count = persist_patterns_to_db(patterns)
    logger.info(f"STATUS: Pattern mining complete. {persisted_count} patterns persisted to database.")

    return patterns


def persist_patterns_to_db(patterns: List[Dict[str, Any]]) -> int:
    """
    Persist discovered patterns to Phase 12 database tables.

    Args:
        patterns: List of pattern dictionaries

    Returns:
        Number of patterns successfully persisted
    """
    try:
        import psycopg2
        import psycopg2.extras
    except ImportError:
        logger.warning("psycopg2 not available - skipping database persistence")
        return 0

    dsn = get_rw_dsn()
    if not dsn:
        logger.warning("No RW DSN available - skipping database persistence")
        return 0

    try:
        conn = psycopg2.connect(dsn)
        cur = conn.cursor()

        persisted_count = 0

        for pattern in patterns:
            # Insert into patterns table
            cur.execute(
                """
                INSERT INTO public.patterns (id, name, type, definition, metadata)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (name) DO NOTHING
                RETURNING id
                """,
                (
                    pattern["id"],
                    pattern["name"],
                    pattern["type"],
                    psycopg2.extras.Json(pattern["definition"]),
                    psycopg2.extras.Json(pattern["metadata"]),
                ),
            )

            result = cur.fetchone()
            if not result:
                continue  # Pattern already exists

            pattern_id = result[0]

            # Insert pattern occurrences
            nodes = pattern.get("occurrences", [])
            if nodes:
                cur.execute(
                    """
                    INSERT INTO public.pattern_occurrences (pattern_id, nodes, score)
                    VALUES (%s, %s, %s)
                    """,
                    (
                        pattern_id,
                        psycopg2.extras.Json(nodes),
                        len(nodes),  # Use node count as score
                    ),
                )

            persisted_count += 1

        conn.commit()
        cur.close()
        conn.close()

        return persisted_count

    except Exception as e:
        logger.error(f"Database persistence error: {e}")
        return 0


if __name__ == "__main__":
    # Load sample graph data
    graph_files = [Path("exports/graph_latest.json"), Path("share/exports/graph_latest.json")]

    graph_data = None
    for graph_file in graph_files:
        if graph_file.exists():
            logger.info(f"Loading graph from {graph_file}")
            with open(graph_file) as f:
                graph_data = json.load(f)
            break

    if not graph_data:
        logger.warning("No graph data found - creating minimal test graph")
        graph_data = {
            "nodes": [
                {"id": "node1", "label": "Test1"},
                {"id": "node2", "label": "Test2"},
                {"id": "node3", "label": "Test3"},
            ],
            "edges": [
                {"source": "node1", "target": "node2", "edge_strength": 0.8},
                {"source": "node2", "target": "node3", "edge_strength": 0.7},
            ],
        }

    # Execute pattern mining
    patterns = find_patterns(graph_data)
    logger.info(f"Mining complete. Found {len(patterns)} patterns.")

    sys.exit(0)
