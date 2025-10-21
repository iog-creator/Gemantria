#!/usr/bin/env python3
"""
Export quick graph statistics for dashboard consumption.

Provides aggregated metrics about the semantic concept network for UI cards
and monitoring dashboards, focusing on key insights and health indicators.
"""

import json
import os
import sys
from src.infra.db import get_gematria_rw
from src.infra.structured_logger import get_logger, log_json

LOG = get_logger("export_stats")


def calculate_graph_stats(db):
    """Calculate comprehensive graph statistics."""

    stats = {}

    # Basic counts
    node_result = list(db.execute("SELECT COUNT(*) FROM concept_network"))
    stats["nodes"] = node_result[0][0] if node_result else 0

    edge_result = list(db.execute("SELECT COUNT(*) FROM concept_relations"))
    stats["edges"] = edge_result[0][0] if edge_result else 0

    # Cluster statistics
    cluster_result = list(db.execute("SELECT COUNT(DISTINCT cluster_id) FROM concept_clusters"))
    stats["clusters"] = cluster_result[0][0] if cluster_result else 0

    # Centrality averages
    centrality_stats = list(db.execute("""
        SELECT
            COALESCE(AVG(degree), 0) as avg_degree,
            COALESCE(MAX(degree), 0) as max_degree,
            COALESCE(AVG(betweenness), 0) as avg_betweenness,
            COALESCE(MAX(betweenness), 0) as max_betweenness,
            COALESCE(AVG(eigenvector), 0) as avg_eigenvector,
            COALESCE(MAX(eigenvector), 0) as max_eigenvector
        FROM concept_centrality
    """))

    if centrality_stats:
        stats["centrality"] = {
            "avg_degree": float(centrality_stats[0][0]),
            "max_degree": float(centrality_stats[0][1]),
            "avg_betweenness": float(centrality_stats[0][2]),
            "max_betweenness": float(centrality_stats[0][3]),
            "avg_eigenvector": float(centrality_stats[0][4]),
            "max_eigenvector": float(centrality_stats[0][5])
        }

    # Edge strength distribution
    edge_distribution = list(db.execute("""
        SELECT
            COUNT(*) as total_edges,
            SUM(CASE WHEN cosine >= 0.90 THEN 1 ELSE 0 END) as strong_edges,
            SUM(CASE WHEN cosine >= 0.75 AND cosine < 0.90 THEN 1 ELSE 0 END) as weak_edges,
            SUM(CASE WHEN cosine < 0.75 THEN 1 ELSE 0 END) as very_weak_edges,
            COALESCE(AVG(cosine), 0) as avg_cosine,
            COALESCE(MIN(cosine), 0) as min_cosine,
            COALESCE(MAX(cosine), 0) as max_cosine
        FROM concept_relations
    """))

    if edge_distribution and stats["edges"] > 0:
        stats["edge_distribution"] = {
            "strong_edges": edge_distribution[0][1],
            "weak_edges": edge_distribution[0][2],
            "very_weak_edges": edge_distribution[0][3],
            "avg_cosine": float(edge_distribution[0][4]),
            "min_cosine": float(edge_distribution[0][5]),
            "max_cosine": float(edge_distribution[0][6])
        }

    # Cluster size distribution
    cluster_sizes = list(db.execute("""
        SELECT cluster_id, COUNT(*) as size
        FROM concept_clusters
        GROUP BY cluster_id
        ORDER BY size DESC
    """))

    if cluster_sizes:
        stats["cluster_sizes"] = [
            {"cluster_id": row[0], "size": row[1]}
            for row in cluster_sizes
        ]

        # Largest cluster info
        largest_cluster = cluster_sizes[0]
        stats["largest_cluster"] = {
            "id": largest_cluster[0],
            "size": largest_cluster[1]
        }

    # Network density (actual edges / possible edges)
    if stats["nodes"] > 1:
        possible_edges = stats["nodes"] * (stats["nodes"] - 1) / 2
        stats["density"] = stats["edges"] / possible_edges if possible_edges > 0 else 0

    # Cluster metrics (if available)
    metrics_overview = list(db.execute("SELECT * FROM v_metrics_overview"))
    if metrics_overview:
        stats["cluster_metrics"] = {
            "avg_cluster_density": float(metrics_overview[0][3]) if metrics_overview[0][3] else None,
            "avg_cluster_diversity": float(metrics_overview[0][4]) if metrics_overview[0][4] else None
        }

    # Health indicators
    stats["health"] = {
        "has_nodes": stats["nodes"] > 0,
        "has_edges": stats["edges"] > 0,
        "has_clusters": stats["clusters"] > 0,
        "density_reasonable": 0.001 <= stats.get("density", 0) <= 0.1 if "density" in stats else False
    }

    return stats


def main():
    """Main export function."""

    log_json(LOG, 20, "export_stats_start")

    try:
        db = get_gematria_rw()
        stats = calculate_graph_stats(db)

        # Add timestamp
        import datetime
        stats["export_timestamp"] = datetime.datetime.now().isoformat()

        # === Rule 021/022: schema validation (fail-closed) ===
        from jsonschema import validate, ValidationError
        import json, sys
        from pathlib import Path

        SCHEMA_PATH = Path("docs/SSOT/graph-stats.schema.json")
        schema = json.loads(SCHEMA_PATH.read_text())
        try:
            validate(instance=stats, schema=schema)
        except ValidationError as e:
            print(f"[export_stats] schema validation failed: {e.message}", file=sys.stderr)
            sys.exit(2)

        # Output JSON to stdout
        print(json.dumps(stats, indent=2))

        # Also write static file for UI consumption
        out_dir = os.getenv("EXPORT_DIR", "exports")
        os.makedirs(out_dir, exist_ok=True)
        stats_path = os.path.join(out_dir, "graph_stats.json")
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

        log_json(LOG, 20, "export_stats_complete", **{k: v for k, v in stats.items() if isinstance(v, (int, float, bool))})

    except Exception as e:
        log_json(LOG, 40, "export_stats_failed", error=str(e))
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
