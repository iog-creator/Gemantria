"""
Pattern discovery module for concept networks.

Provides graph construction from database relations and community detection
with centrality analysis using NetworkX algorithms.
"""

import logging

import networkx as nx

logger = logging.getLogger(__name__)


def build_graph(db):
    """
    Build NetworkX graph from concept_network nodes and concept_relations edges.

    Args:
        db: Database connection object

    Returns:
        nx.Graph: NetworkX graph with nodes and weighted edges
    """
    # nodes - use UUID as label since concept names aren't stored in concept_network
    nodes = list(db.execute("SELECT concept_id, LEFT(CAST(concept_id AS TEXT), 8) FROM concept_network"))

    # edges
    edges = list(db.execute("SELECT source_id, target_id, cosine FROM concept_relations"))

    G = nx.Graph()
    for cid, label in nodes:
        G.add_node(str(cid), label=label)
    for sid, tid, cos in edges:
        G.add_edge(str(sid), str(tid), weight=float(cos))

    logger.info(f"Built graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    return G


def compute_patterns(G):
    """
    Compute community clusters and centrality measures.

    Args:
        G: NetworkX graph

    Returns:
        tuple: (cluster_map, degree_centrality, betweenness_centrality, eigenvector_centrality)
    """
    # clusters using Louvain method
    from networkx.algorithms.community import louvain_communities

    comms = louvain_communities(G, weight="weight", seed=42)
    cluster_map = {}
    for idx, c in enumerate(comms):
        for n in c:
            cluster_map[n] = idx

    logger.info(f"Found {len(comms)} communities")

    # centrality measures
    degree = nx.degree_centrality(G)
    betw = nx.betweenness_centrality(G, weight="weight", normalized=True)

    # eigenvector centrality (may fail on disconnected graphs)
    try:
        eigen = nx.eigenvector_centrality_numpy(G, weight="weight")
    except nx.PowerIterationFailedConvergence:
        logger.warning("Eigenvector centrality failed to converge, using zeros")
        eigen = {n: 0.0 for n in G.nodes()}
    except Exception as e:
        logger.warning(f"Eigenvector centrality error: {e}, using zeros")
        eigen = {n: 0.0 for n in G.nodes()}

    return cluster_map, degree, betw, eigen
