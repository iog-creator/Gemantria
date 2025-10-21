#!/usr/bin/env python3
"""
Export semantic concept network as viz-ready JSON.

Creates graph_latest.json with nodes, edges, clusters, and centrality
for UI consumption and visualization tools.
"""

import os
import json
from src.infra.db import get_gematria_rw
from src.infra.structured_logger import get_logger, log_json

LOG = get_logger("export_graph")


def main():
    """Main export function."""
    log_json(LOG, 20, "export_start")

    try:
        out_dir = os.getenv("EXPORT_DIR", "exports")
        os.makedirs(out_dir, exist_ok=True)

        db = get_gematria_rw()

        # Fetch nodes with cluster and centrality data
        nodes = list(db.execute("""
            SELECT n.concept_id, co.name, c.cluster_id,
                   ce.degree, ce.betweenness, ce.eigenvector
            FROM concept_network n
            LEFT JOIN concepts co ON co.id::text = n.concept_id::text
            LEFT JOIN concept_clusters c ON c.concept_id = n.concept_id
            LEFT JOIN concept_centrality ce ON ce.concept_id = n.concept_id
        """))

        # Fetch edges
        edges = list(db.execute("""
            SELECT source_id, target_id, cosine, rerank_score, decided_yes
            FROM concept_relations
        """))

        # Build graph structure
        graph = {
            "nodes": [
                {
                    "id": str(r[0]),
                    "label": r[1] or str(r[0]),
                    "cluster": r[2],
                    "degree": float(r[3] or 0),
                    "betweenness": float(r[4] or 0),
                    "eigenvector": float(r[5] or 0)
                }
                for r in nodes
            ],
            "edges": [
                {
                    "source": str(r[0]),
                    "target": str(r[1]),
                    "strength": float(r[2] or 0),
                    "rerank": float(r[3] or 0) if r[3] else None,
                    "yes": bool(r[4]) if r[4] is not None else None
                }
                for r in edges
            ],
            "metadata": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "cluster_count": len(set(r[2] for r in nodes if r[2] is not None)),
                "export_timestamp": str(list(db.execute("SELECT now()"))[0][0])
            }
        }

        # Write to file
        out_path = os.path.join(out_dir, "graph_latest.json")
        with open(out_path, "w") as f:
            json.dump(graph, f, indent=2)

        result = {
            "export_path": out_path,
            "node_count": len(graph["nodes"]),
            "edge_count": len(graph["edges"]),
            "export_complete": True
        }

        log_json(LOG, 20, "export_complete", **result)
        print(json.dumps(result))

    except Exception as e:
        log_json(LOG, 40, "export_failed", error=str(e))
        print(json.dumps({"error": str(e)}))
        raise


if __name__ == "__main__":
    main()

