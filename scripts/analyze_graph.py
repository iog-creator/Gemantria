#!/usr/bin/env python3
"""
Analyze semantic concept network for communities and centrality.

Computes Louvain communities and centrality measures, then persists results
to concept_clusters and concept_centrality tables for reporting and viz.
"""

import json

from src.graph.patterns import build_graph, compute_patterns
from src.infra.db import get_gematria_rw
from src.infra.structured_logger import get_logger, log_json

LOG = get_logger("analyze_graph")


def main():
    """Main analysis function."""
    log_json(LOG, 20, "analysis_start")

    try:
        # Build graph from database
        db = get_gematria_rw()
        G = build_graph(db)

        if G.number_of_nodes() == 0:
            log_json(LOG, 30, "analysis_skipped", reason="no_nodes")
            print(json.dumps({"error": "No nodes found in concept_network"}))
            return

        # Compute patterns
        cluster_map, degree, betw, eigen = compute_patterns(G)

        # Store clusters
        cluster_insert_count = 0
        for node, cluster_id in cluster_map.items():
            try:
                db.execute(
                    """
                    INSERT INTO concept_clusters (concept_id, cluster_id)
                    VALUES (%s, %s)
                    ON CONFLICT (concept_id) DO NOTHING
                """,
                    (node, cluster_id),
                )
                cluster_insert_count += 1
            except Exception as e:
                log_json(
                    LOG,
                    40,
                    "cluster_insert_failed",
                    node=node[:8],
                    cluster_id=cluster_id,
                    error=str(e),
                )

        # Store centrality
        centrality_insert_count = 0
        for node in G.nodes():
            try:
                db.execute(
                    """
                    INSERT INTO concept_centrality (concept_id, degree, betweenness, eigenvector)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (concept_id) DO NOTHING
                """,
                    (node, degree.get(node, 0), betw.get(node, 0), eigen.get(node, 0)),
                )
                centrality_insert_count += 1
            except Exception as e:
                log_json(
                    LOG, 40, "centrality_insert_failed", node=node[:8], error=str(e)
                )

        # Report results
        result = {
            "clusters_found": len(set(cluster_map.values())),
            "nodes_analyzed": G.number_of_nodes(),
            "edges_analyzed": G.number_of_edges(),
            "largest_cluster": max(
                [
                    list(cluster_map.values()).count(cid)
                    for cid in set(cluster_map.values())
                ],
                default=0,
            ),
            "avg_degree": sum(degree.values()) / len(degree) if degree else 0,
            "cluster_inserts": cluster_insert_count,
            "centrality_inserts": centrality_insert_count,
            "analysis_complete": True,
        }

        # Ensure all changes are committed
        if hasattr(db, "commit"):
            db.commit()

        log_json(LOG, 20, "analysis_complete", **result)
        print(json.dumps(result))

    except Exception as e:
        log_json(LOG, 40, "analysis_failed", error=str(e))
        print(json.dumps({"error": str(e)}))
        raise


if __name__ == "__main__":
    main()
