#!/usr/bin/env python3
"""
Export semantic concept network as viz-ready JSON.

Creates graph_latest.json with nodes, edges, clusters, and centrality
for UI consumption and visualization tools.
"""

import json
import os

from src.infra.db import get_gematria_rw
from src.infra.env_loader import ensure_env_loaded
from src.infra.structured_logger import get_logger, log_json
from src.rerank.blender import blend_strength

# Load environment variables from .env file
ensure_env_loaded()

LOG = get_logger("export_graph")


def export_correlation_graph():
    """Export correlation network as viz-ready JSON for correlation analysis."""
    try:
        # Read correlation data
        correlations_path = os.path.join("exports", "graph_correlations.json")
        if not os.path.exists(correlations_path):
            LOG.warning("Correlation data not found, skipping correlation graph export")
            return None

        with open(correlations_path) as f:
            correlation_data = json.load(f)

        correlations = correlation_data.get("correlations", [])
        metadata = correlation_data.get("metadata", {})

        # Filter correlations |r| >= 0.4
        filtered_correlations = [corr for corr in correlations if abs(corr.get("correlation", 0)) >= 0.4]

        if not filtered_correlations:
            LOG.info("No strong correlations found (>= 0.4), correlation graph will be empty")
            filtered_correlations = []

        # Build NetworkX graph for analysis
        try:
            import networkx as nx  # noqa: E402

            G = nx.Graph()

            # Add nodes (unique concepts from correlations)
            nodes_set = set()
            for corr in filtered_correlations:
                nodes_set.add(corr["source"])
                nodes_set.add(corr["target"])

            for node_id in nodes_set:
                G.add_node(node_id)

            # Add weighted edges
            for corr in filtered_correlations:
                G.add_edge(
                    corr["source"],
                    corr["target"],
                    weight=abs(corr["correlation"]),  # Use absolute correlation as weight
                    correlation=corr["correlation"],  # Keep signed correlation
                    p_value=corr.get("p_value", 1.0),
                    metric=corr.get("metric", "unknown"),
                )

            # Compute network metrics
            network_metrics = {
                "node_count": G.number_of_nodes(),
                "edge_count": G.number_of_edges(),
                "connected_components": nx.number_connected_components(G),
                "is_connected": (nx.is_connected(G) if G.number_of_nodes() > 0 else False),
            }

            # Weighted degree statistics
            if G.number_of_edges() > 0:
                degrees = dict(G.degree(weight="weight"))
                network_metrics.update(
                    {
                        "avg_weighted_degree": (sum(degrees.values()) / len(degrees) if degrees else 0),
                        "max_weighted_degree": max(degrees.values()) if degrees else 0,
                        "avg_clustering_coeff": nx.average_clustering(G, weight="weight"),
                    }
                )

                # Find most central nodes
                if degrees:
                    top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:5]
                    network_metrics["top_weighted_degree_nodes"] = [
                        {"node": node, "weighted_degree": degree} for node, degree in top_nodes
                    ]
            else:
                network_metrics.update(
                    {
                        "avg_weighted_degree": 0,
                        "max_weighted_degree": 0,
                        "avg_clustering_coeff": 0,
                        "top_weighted_degree_nodes": [],
                    }
                )

        except ImportError:
            LOG.warning("NetworkX not available, computing basic correlation graph")
            # Fallback without NetworkX
            nodes_set = set()
            for corr in filtered_correlations:
                nodes_set.add(corr["source"])
                nodes_set.add(corr["target"])

            G = None  # Not used in fallback
            network_metrics = {
                "node_count": len(nodes_set),
                "edge_count": len(filtered_correlations),
                "connected_components": "unknown (networkx not available)",
                "is_connected": "unknown (networkx not available)",
                "avg_weighted_degree": "unknown (networkx not available)",
                "max_weighted_degree": "unknown (networkx not available)",
                "avg_clustering_coeff": "unknown (networkx not available)",
                "top_weighted_degree_nodes": [],
            }

        # Build correlation graph structure
        correlation_graph = {
            "nodes": [
                {
                    "id": node_id,
                    "label": node_id,  # Could be enhanced with concept names
                    "type": "correlation_node",
                }
                for node_id in nodes_set
            ],
            "edges": [
                {
                    "source": corr["source"],
                    "target": corr["target"],
                    "correlation": corr["correlation"],
                    "weight": abs(corr["correlation"]),
                    "p_value": corr.get("p_value", 1.0),
                    "metric": corr.get("metric", "unknown"),
                    "cluster_source": corr.get("cluster_source"),
                    "cluster_target": corr.get("cluster_target"),
                    "significance": ("significant" if corr.get("p_value", 1.0) < 0.05 else "not_significant"),
                }
                for corr in filtered_correlations
            ],
            "metadata": {
                **network_metrics,
                "correlation_threshold": 0.4,
                "total_input_correlations": len(correlations),
                "filtered_correlations": len(filtered_correlations),
                "correlation_methods": metadata.get("correlation_methods", []),
                "export_timestamp": metadata.get(
                    "generated_at",
                    str(next(iter(get_gematria_rw().execute("SELECT now()")))[0]),
                ),
            },
        }

        # Write to file
        out_dir = os.getenv("EXPORT_DIR", "exports")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "graph_correlation_network.json")

        with open(out_path, "w") as f:
            json.dump(correlation_graph, f, indent=2)

        result = {
            "export_path": out_path,
            "correlation_threshold": 0.4,
            "nodes": len(correlation_graph["nodes"]),
            "edges": len(correlation_graph["edges"]),
            "network_metrics": network_metrics,
            "export_complete": True,
        }

        log_json(LOG, 20, "correlation_graph_export_complete", **result)
        return result

    except Exception as e:
        log_json(LOG, 40, "correlation_graph_export_failed", error=str(e))
        LOG.error(f"Correlation graph export failed: {e}")
        return None


def main():
    """Main export function."""
    log_json(LOG, 20, "export_start")

    try:
        out_dir = os.getenv("EXPORT_DIR", "exports")
        os.makedirs(out_dir, exist_ok=True)

        db = get_gematria_rw()

        # Fetch nodes with cluster and centrality data
        nodes = list(
            db.execute(
                """
            SELECT n.concept_id, co.name, c.cluster_id,
                   ce.degree, ce.betweenness, ce.eigenvector
            FROM concept_network n
            LEFT JOIN concepts co ON co.id::text = n.concept_id::text
            LEFT JOIN concept_clusters c ON c.concept_id = n.concept_id
            LEFT JOIN concept_centrality ce ON ce.concept_id = n.concept_id
        """
            )
        )

        # Fetch edges
        edges = list(
            db.execute(
                """
            SELECT source_id, target_id, cosine, rerank_score, decided_yes
            FROM concept_relations
        """
            )
        )

        # Build graph structure
        graph = {
            "nodes": [
                {
                    "id": str(r[0]),
                    "label": r[1] or str(r[0]),
                    "cluster": r[2],
                    "degree": float(r[3] or 0),
                    "betweenness": float(r[4] or 0),
                    "eigenvector": float(r[5] or 0),
                }
                for r in nodes
            ],
            # SSOT field names (Rule-045); validators depend on exact keys.
            "edges": [
                {
                    "source": str(r[0]),
                    "target": str(r[1]),
                    "cosine": float(r[2] or 0),
                    "rerank_score": float(r[3] or 0) if r[3] else None,
                    "edge_strength": blend_strength(float(r[2] or 0), float(r[3] or 0)) if r[3] else float(r[2] or 0),
                }
                for r in edges
            ],
            "metadata": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "cluster_count": len(set(r[2] for r in nodes if r[2] is not None)),
                "export_timestamp": str(next(iter(db.execute("SELECT now()")))[0]),
            },
        }

        # Write to file
        out_path = os.path.join(out_dir, "graph_latest.json")
        with open(out_path, "w") as f:
            json.dump(graph, f, indent=2)

        result = {
            "export_path": out_path,
            "node_count": len(graph["nodes"]),
            "edge_count": len(graph["edges"]),
            "export_complete": True,
        }

        log_json(LOG, 20, "export_complete", **result)
        print(json.dumps(result))

        # Phase 5-C: Export correlation graph
        correlation_result = export_correlation_graph()
        if correlation_result:
            print(f"Correlation graph exported to: {correlation_result['export_path']}")
            log_json(LOG, 20, "correlation_export_included", **correlation_result)

    except Exception as e:
        log_json(LOG, 40, "export_failed", error=str(e))
        print(json.dumps({"error": str(e)}))
        raise


if __name__ == "__main__":
    main()
