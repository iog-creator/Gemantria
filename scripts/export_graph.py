# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
Export semantic concept network as viz-ready JSON.

Creates graph_latest.json with nodes, edges, clusters, and centrality
for UI consumption and visualization tools.
"""

import json
import os
import pathlib
import sys
from datetime import datetime, UTC

from src.infra.db import get_gematria_rw
from src.infra.env_loader import ensure_env_loaded
from src.infra.structured_logger import get_logger, log_json
from src.rerank.blender import blend_strength

# Load environment variables from .env file
ensure_env_loaded()

LOG = get_logger("export_graph")


def _load_correlation_weights(db) -> dict:
    """
    Load correlation weights from Phase 10 export and map to concept_network.id.

    Correlations use concept_network.concept_id, but edges use concept_network.id.
    This function creates a mapping from (network_id_source, network_id_target) to correlation.

    Returns:
        Dict mapping (source_network_id, target_network_id) tuple to correlation value.
        Handles bidirectional matching (both (a,b) and (b,a) keys).
    """
    correlations_path = os.path.join("exports", "graph_correlations.json")
    if not os.path.exists(correlations_path):
        LOG.warning(f"Correlation file not found: {correlations_path}")
        return {}

    try:
        with open(correlations_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        correlations_list = data.get("correlations", [])
        if not correlations_list:
            LOG.warning("Correlation file exists but contains no correlations")
            return {}

        # Build mapping from concept_id to network_id
        # Correlations use concept_id, but edges use network_id
        concept_to_network = {}
        try:
            for row in db.execute("SELECT id, concept_id FROM concept_network"):
                network_id = str(row[0])
                concept_id = str(row[1])
                concept_to_network[concept_id] = network_id
            LOG.info(f"Mapped {len(concept_to_network)} concept_ids to network_ids")
        except Exception as e:
            LOG.warning(f"Failed to build concept_id->network_id mapping: {e}")
            return {}

        # Build lookup dict using network_ids (what edges use)
        lookup = {}
        mapped_count = 0
        for corr in correlations_list:
            source_concept_id = str(corr.get("source", ""))
            target_concept_id = str(corr.get("target", ""))
            correlation = float(corr.get("correlation", 0.0))

            if not source_concept_id or not target_concept_id:
                continue

            # Map concept_ids to network_ids
            source_network_id = concept_to_network.get(source_concept_id)
            target_network_id = concept_to_network.get(target_concept_id)

            if not source_network_id or not target_network_id:
                continue

            # Store with both orderings for flexible lookup
            key_forward = (source_network_id, target_network_id)
            key_reverse = (target_network_id, source_network_id)
            lookup[key_forward] = correlation
            lookup[key_reverse] = correlation
            mapped_count += 1

        LOG.info(
            f"Loaded {len(correlations_list)} correlations, mapped {mapped_count} to network_ids, {len(lookup)} lookup entries"
        )
        return lookup

    except Exception as e:
        LOG.warning(f"Failed to load correlations: {e}")
        import traceback

        LOG.warning(traceback.format_exc())
        return {}


def _node_payload(noun: dict) -> dict:
    out = {
        "id": noun["noun_id"],
        "surface": noun.get("surface"),
        "class": noun.get("class"),
        "analysis": noun.get("analysis", {}),
        "gematria": noun.get("gematria"),
        "book": noun.get("book"),
        "chapter": noun.get("chapter"),
        "verse": noun.get("verse"),
        "position": noun.get("position"),
    }
    # Expose enrichment cross-references to UI as external_refs (optional)
    enr = noun.get("enrichment") or {}
    xrefs = enr.get("crossrefs") or []
    if xrefs:
        out["external_refs"] = [{"label": xr.get("label"), "osis": xr.get("osis")} for xr in xrefs if xr.get("osis")]
    return out


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

    fast_lane = pathlib.Path("exports/graph_latest.json")
    if fast_lane.exists():
        try:
            payload = json.loads(fast_lane.read_text())
            nodes = len(payload.get("nodes", []))
            edges = len(payload.get("edges", []))
            stats_path = pathlib.Path("exports/graph_stats.json")
            if not stats_path.exists():
                density = (2.0 * edges) / (nodes * (nodes - 1)) if nodes > 1 else 0.0
                stats_path.write_text(
                    json.dumps(
                        {
                            "book": payload.get("book"),
                            "nodes": nodes,
                            "edges": edges,
                            "density": round(density, 6),
                            "generated_at": datetime.now(UTC).isoformat(),
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
                    + "\n"
                )
            print(
                ">> analytics.export: fast-lane file detected (exports/graph_latest.json), skipping DB.",
                flush=True,
            )
            log_json(
                LOG,
                20,
                "export_fast_lane_used",
                nodes=nodes,
                edges=edges,
                stats_exists=stats_path.exists(),
            )
            return
        except Exception as exc:
            print(
                f">> analytics.export: fast-lane present but unreadable: {exc}; falling back to DB.",
                file=sys.stderr,
                flush=True,
            )
            log_json(LOG, 30, "export_fast_lane_failed", error=str(exc))

    try:
        out_dir = os.getenv("EXPORT_DIR", "exports")
        os.makedirs(out_dir, exist_ok=True)

        # Try to read ai_nouns.json for enriched node data (prioritize over database)
        ai_nouns_path = os.path.join("exports", "ai_nouns.json")
        nodes_data = []
        use_ai_nouns = False
        if os.path.exists(ai_nouns_path):
            with open(ai_nouns_path, encoding="utf-8") as f:
                ai_nouns_data = json.load(f)
                nodes_data = ai_nouns_data.get("nodes", [])
            LOG.info(f"Loaded {len(nodes_data)} nodes from ai_nouns.json")
            use_ai_nouns = len(nodes_data) > 0
        else:
            LOG.warning("ai_nouns.json not found, falling back to database nodes")

        if not use_ai_nouns:
            # Fallback to database nodes if ai_nouns.json doesn't exist or is empty
            db = get_gematria_rw()
            # PM Decision: Use v_concepts_with_verses as canonical bridge
            # See docs/SSOT/PHASE8_BRIDGE_DECISION.md
            db_nodes = list(
                db.execute(
                    """
                SELECT n.concept_id, cm.label, c.cluster_id,
                       ce.degree, ce.betweenness, ce.eigenvector,
                       v.gematria_value, v.book_source, v.verses
                FROM concept_network n
                LEFT JOIN concept_metadata cm ON cm.concept_id = n.concept_id
                LEFT JOIN concept_clusters c ON c.concept_id = n.concept_id
                LEFT JOIN concept_centrality ce ON ce.concept_id = n.concept_id
                LEFT JOIN v_concepts_with_verses v ON cm.source = 'bible_db:concept_id:' || v.id::text
            """
                )
            )
            nodes_data = []
            for r in db_nodes:
                node = {
                    "noun_id": str(r[0]),
                    "surface": r[1] or str(r[0]),
                    "cluster": r[2],
                    "degree": float(r[3] or 0),
                    "betweenness": float(r[4] or 0),
                    "eigenvector": float(r[5] or 0),
                }

                # Enrichment Logic (Phase 8)
                # Extract metadata from v_concepts_with_verses columns
                gematria_val = r[6]
                book_src = r[7]
                verses_data = r[8]  # JSONB array of objects

                # 1. Gematria
                if gematria_val is not None:
                    node["gematria"] = float(gematria_val)

                # 2. Book
                if book_src:
                    node["book"] = book_src

                # 3. Chapter/Verse/Position from verses JSON
                # Expected JSON structure: [{"ref": "Gen 1:1", "verse_id": ..., "position": 1001, ...}, ...]
                if verses_data and isinstance(verses_data, list) and len(verses_data) > 0:
                    # Take the first occurrence as primary reference
                    first_occ = verses_data[0]
                    if isinstance(first_occ, dict):
                        # Try explicit fields first if view provides them
                        # The view definition shows: 'ref', 'verse_id', 'position'
                        # It constructs ref as "Book Chapter:Verse"

                        # Extract position directly if available
                        if "position" in first_occ and first_occ["position"] is not None:
                            node["position"] = int(first_occ["position"])

                        # Parse ref or use other fields for chapter/verse
                        # View def: ref = book + ' ' + chapter + ':' + verse
                        ref = first_occ.get("ref", "")
                        if ":" in ref:
                            try:
                                # "Genesis 1:1" -> split last part
                                parts = ref.rsplit(" ", 1)
                                if len(parts) == 2:
                                    cv = parts[1].split(":")
                                    if len(cv) == 2:
                                        node["chapter"] = int(cv[0])
                                        node["verse"] = int(cv[1])
                                        # Fallback position calculation if not in JSON
                                        if "position" not in node:
                                            node["position"] = (node["chapter"] * 1000) + node["verse"]
                            except (ValueError, IndexError):
                                pass

                nodes_data.append(node)

        # Build nodes using _node_payload function
        nodes = [_node_payload(noun) for noun in nodes_data]

        # Always need db connection for edges
        db = get_gematria_rw()

        # Load correlation weights (Phase 10) - needs DB for concept_id->network_id mapping
        correlation_lookup = _load_correlation_weights(db)

        # Fetch edges
        try:
            edges_result = db.execute(
                """
            SELECT source_id, target_id, cosine, rerank_score, decided_yes
            FROM concept_relations
            """
            )
            edges = list(edges_result)
            LOG.info(f"Fetched {len(edges)} edges, first edge: {edges[0] if edges else 'No edges'}")
        except Exception as e:
            LOG.warning(f"Could not fetch edges: {e}, using empty edges list")
            edges = []

        # Build graph structure with correlation weights
        edges_with_corr = []
        edges_with_correlation_count = 0
        for r in edges:
            source_id = str(r[0])
            target_id = str(r[1])
            edge = {
                "source": source_id,
                "target": target_id,
                "cosine": float(r[2] or 0),
                "rerank_score": float(r[3] or 0) if r[3] else None,
                "edge_strength": blend_strength(float(r[2] or 0), float(r[3] or 0)) if r[3] else float(r[2] or 0),
            }

            # Add correlation_weight if available (Phase 10)
            # Normalize from [-1, 1] to [0, 1] for COMPASS validation
            # Only include if normalized value > 0.5 (i.e., original correlation > 0)
            corr_key = (source_id, target_id)
            if corr_key in correlation_lookup:
                raw_correlation = correlation_lookup[corr_key]
                # Normalize from [-1, 1] to [0, 1]
                normalized_correlation = (raw_correlation + 1.0) / 2.0
                # Only include if significant (normalized > 0.5 means original > 0)
                if normalized_correlation > 0.5:
                    edge["correlation_weight"] = normalized_correlation
                    edges_with_correlation_count += 1

            edges_with_corr.append(edge)

        if edges_with_correlation_count > 0:
            LOG.info(f"Added correlation_weight to {edges_with_correlation_count} edges (Phase 10)")

        graph = {
            "nodes": nodes,
            # SSOT field names (Rule-045); validators depend on exact keys.
            "edges": edges_with_corr,
            "metadata": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "cluster_count": len(set(n.get("cluster") for n in nodes_data if n.get("cluster") is not None)),
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
