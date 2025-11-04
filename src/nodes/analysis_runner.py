import json
import os
from typing import Any

from src.infra.structured_logger import get_logger, log_json

LOG = get_logger("gematria.analysis_runner")


class AnalysisError(Exception):
    """Raised when analysis operations fail."""


def analysis_runner_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    Run analysis operations on pipeline outputs.

    This node performs graph analysis, community detection, centrality calculations,
    and exports visualization-ready data.
    """
    try:
        analysis_results = {}

        # Run graph analysis if we have network data
        if "network_summary" in state and state["network_summary"].get("total_nodes", 0) > 0:
            try:
                # Import and run graph analysis
                from src.graph.patterns import build_graph, compute_patterns
                from src.infra.db import get_gematria_rw

                db = get_gematria_rw()
                G = build_graph(db)

                if G.number_of_nodes() > 0:
                    cluster_map, degree, betw, eigen = compute_patterns(G)

                    # Store clusters and centrality
                    cluster_count = 0
                    centrality_count = 0

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
                            cluster_count += 1
                        except Exception as e:
                            log_json(LOG, 30, "cluster_insert_failed", node=str(node), error=str(e))

                    # Store centrality measures
                    for node in G.nodes():
                        try:
                            db.execute(
                                """
                                INSERT INTO concept_centrality (
                                    concept_id, degree, betweenness, eigenvector
                                ) VALUES (%s, %s, %s, %s)
                                ON CONFLICT (concept_id) DO UPDATE SET
                                    degree = EXCLUDED.degree,
                                    betweenness = EXCLUDED.betweenness,
                                    eigenvector = EXCLUDED.eigenvector,
                                    metrics_at = now()
                            """,
                                (
                                    node,
                                    degree.get(node, 0),
                                    betw.get(node, 0),
                                    eigen.get(node, 0),
                                ),
                            )
                            centrality_count += 1
                        except Exception as e:
                            log_json(LOG, 30, "centrality_insert_failed", node=str(node), error=str(e))

                    analysis_results["graph_analysis"] = {
                        "clusters_stored": cluster_count,
                        "centrality_measures_stored": centrality_count,
                        "communities_found": len(set(cluster_map.values())),
                    }

                    log_json(
                        LOG,
                        20,
                        "graph_analysis_complete",
                        clusters=cluster_count,
                        centrality=centrality_count,
                        communities=len(set(cluster_map.values())),
                    )

            except Exception as e:
                log_json(LOG, 30, "graph_analysis_failed", error=str(e))
                analysis_results["graph_analysis_error"] = str(e)

        # Run export operations
        try:
            # Export graph data for visualization
            _export_graph_data()
            analysis_results["graph_export"] = "completed"

            # Export stats
            _export_stats()
            analysis_results["stats_export"] = "completed"

        except Exception as e:
            log_json(LOG, 30, "export_operations_failed", error=str(e))
            analysis_results["export_error"] = str(e)

        # Update state with analysis results
        state["analysis_results"] = analysis_results
        log_json(LOG, 20, "analysis_runner_complete", results=analysis_results)

        return state

    except Exception as e:
        log_json(LOG, 40, "analysis_runner_unexpected_error", error=str(e))
        state["analysis_error"] = str(e)
        return state


def _export_graph_data():
    """Export graph data for visualization."""
    try:
        from src.infra.db import get_gematria_rw
        from src.rerank.blender import blend_strength

        db = get_gematria_rw()

        # Get concepts with their metadata
        concepts = db.execute("""
            SELECT
                c.concept_id,
                c.name,
                c.hebrew_text,
                c.gematria_value,
                c.primary_verse,
                c.book,
                c.chapter,
                c.freq,
                cc.cluster_id,
                cen.degree,
                cen.betweenness,
                cen.eigenvector
            FROM concepts c
            LEFT JOIN concept_clusters cc ON c.concept_id = cc.concept_id
            LEFT JOIN concept_centrality cen ON c.concept_id = cen.concept_id
        """).fetchall()

        # Get relationships
        relationships = db.execute("""
            SELECT
                cn1.concept_id as source_id,
                cn2.concept_id as target_id,
                r.weight as cosine,
                r.evidence->>'rerank_score' as rerank_score,
                r.evidence->>'edge_strength' as edge_strength
            FROM concept_relations r
            JOIN concept_network cn1 ON r.src_concept_id = cn1.concept_id
            JOIN concept_network cn2 ON r.dst_concept_id = cn2.concept_id
            WHERE r.relation_type = 'semantic_similarity'
        """).fetchall()

        # Build nodes
        nodes = []
        for row in concepts:
            (
                concept_id,
                name,
                hebrew,
                gematria,
                verse,
                book,
                chapter,
                freq,
                cluster,
                degree,
                betweenness,
                eigenvector,
            ) = row
            nodes.append(
                {
                    "id": str(concept_id),
                    "label": name or hebrew or str(concept_id),
                    "hebrew": hebrew,
                    "gematria_value": gematria,
                    "primary_verse": verse,
                    "book": book,
                    "chapter": chapter,
                    "frequency": freq,
                    "cluster": cluster,
                    "degree": float(degree or 0),
                    "betweenness": float(betweenness or 0),
                    "eigenvector": float(eigenvector or 0),
                }
            )

        # Build edges
        edges = []
        for row in relationships:
            source_id, target_id, cosine, rerank_score, edge_strength = row
            # Use blended strength if available, otherwise compute it
            if edge_strength:
                strength = float(edge_strength)
            else:
                strength = blend_strength(float(cosine or 0), float(rerank_score or 0))

            edges.append(
                {
                    "source": str(source_id),
                    "target": str(target_id),
                    "cosine": float(cosine or 0),
                    "rerank_score": float(rerank_score or 0),
                    "edge_strength": strength,
                }
            )

        # Write to exports
        os.makedirs("exports", exist_ok=True)
        with open("exports/graph_latest.json", "w", encoding="utf-8") as f:
            json.dump(
                {
                    "nodes": nodes,
                    "edges": edges,
                    "metadata": {
                        "node_count": len(nodes),
                        "edge_count": len(edges),
                        "export_timestamp": None,  # Will be set by calling code
                    },
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        log_json(LOG, 20, "graph_data_exported", nodes=len(nodes), edges=len(edges))

    except Exception as e:
        log_json(LOG, 30, "graph_export_failed", error=str(e))
        raise


def _export_stats():
    """Export graph statistics."""
    try:
        from src.infra.db import get_gematria_rw

        db = get_gematria_rw()

        # Get basic counts
        concept_count = db.execute("SELECT count(*) FROM concepts").fetchone()[0]
        relation_count = db.execute("SELECT count(*) FROM concept_relations").fetchone()[0]
        cluster_count = db.execute("SELECT count(distinct cluster_id) FROM concept_clusters").fetchone()[0]

        # Get centrality averages
        centrality_stats = db.execute("""
            SELECT
                avg(degree) as avg_degree,
                max(degree) as max_degree,
                avg(betweenness) as avg_betweenness,
                avg(eigenvector) as avg_eigenvector
            FROM concept_centrality
        """).fetchone()

        # Write stats
        os.makedirs("exports", exist_ok=True)
        with open("exports/graph_stats.json", "w", encoding="utf-8") as f:
            json.dump(
                {
                    "nodes": concept_count,
                    "edges": relation_count,
                    "clusters": cluster_count,
                    "centrality": {
                        "avg_degree": float(centrality_stats[0] or 0),
                        "max_degree": float(centrality_stats[1] or 0),
                        "avg_betweenness": float(centrality_stats[2] or 0),
                        "avg_eigenvector": float(centrality_stats[3] or 0),
                    },
                },
                f,
                indent=2,
            )

        log_json(LOG, 20, "stats_exported", nodes=concept_count, edges=relation_count, clusters=cluster_count)

    except Exception as e:
        log_json(LOG, 30, "stats_export_failed", error=str(e))
        raise
