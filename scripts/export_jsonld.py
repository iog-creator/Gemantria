# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
Export semantic concept network as JSON-LD and RDF/Turtle for semantic web compliance.

Creates graph_latest.jsonld and graph_latest.ttl files with proper linked data structure,
URI namespaces, and semantic web standards compliance for knowledge graph integration.
"""

import json
import os
from typing import Any

from rdflib import RDF, RDFS, Graph, Literal, Namespace
from rdflib.namespace import SDO as SCHEMA

from src.infra.db import get_gematria_rw
from src.infra.env_loader import ensure_env_loaded
from src.infra.structured_logger import get_logger, log_json

# Load environment variables from .env file
ensure_env_loaded()

LOG = get_logger("export_jsonld")

# Define namespaces
GEMATRIA = Namespace("https://gemantria.ai/concept/")
SCHEMA_ORG = Namespace("http://schema.org/")


def fetch_graph_data(
    db,
) -> tuple[list[tuple], list[tuple], list[tuple] | None, dict[int, dict[str, Any]] | None]:
    """Fetch nodes, edges, optional metadata, and cluster metrics from database."""

    # Fetch nodes with cluster, centrality, and concept metrics data
    nodes = db.execute(
        """
        SELECT DISTINCT n.concept_id, n.label, c.cluster_id,
               ce.degree, ce.betweenness, ce.eigenvector,
               cm.semantic_cohesion, cm.bridge_score, cm.diversity_local
        FROM concept_network n
        LEFT JOIN concept_clusters c ON c.concept_id = n.concept_id
        LEFT JOIN concept_centrality ce ON ce.concept_id = n.concept_id
        LEFT JOIN concept_metrics cm ON cm.concept_id = n.concept_id
    """
    ).fetchall()

    # Fetch edges
    edges = db.execute(
        """
        SELECT source_id, target_id, cosine, rerank_score, decided_yes
        FROM concept_relations
    """
    ).fetchall()

    # Fetch cluster metrics
    cmetrics = db.execute(
        """
        SELECT cluster_id, density, semantic_diversity, top_examples FROM cluster_metrics
    """
    ).fetchall()
    cmeta = {
        r[0]: {"clusterDensity": r[1], "clusterDiversity": r[2], "topExamples": r[3]}
        for r in cmetrics
    }

    # Try to fetch metadata (optional table)
    metadata = None
    try:
        metadata = db.execute(
            """
            SELECT concept_id, label, description, source, language
            FROM concept_metadata
        """
        ).fetchall()
    except Exception:
        log_json(
            LOG,
            15,
            "metadata_table_missing",
            message="concept_metadata table not found, using basic labels",
        )

    return nodes, edges, metadata, cmeta


def create_jsonld_context() -> dict[str, Any]:
    """Create JSON-LD context with proper namespace mappings."""
    return {
        "@context": {
            "@vocab": str(GEMATRIA),
            "label": str(RDFS.label),
            "relatedTo": str(SCHEMA.relatedTo),
            "cosine": str(SCHEMA.value),
            "rerankScore": str(GEMATRIA.rerankScore),
            "cluster": str(SCHEMA.category),
            "degree": str(GEMATRIA.degree),
            "betweenness": str(GEMATRIA.betweenness),
            "eigenvector": str(GEMATRIA.eigenvector),
            "semanticCohesion": str(GEMATRIA.semanticCohesion),
            "bridgeScore": str(GEMATRIA.bridgeScore),
            "diversityLocal": str(GEMATRIA.diversityLocal),
            "clusterDensity": str(GEMATRIA.clusterDensity),
            "clusterDiversity": str(GEMATRIA.clusterDiversity),
            "topExamples": str(GEMATRIA.topExamples),
            "description": str(SCHEMA.description),
            "source": str(SCHEMA.source),
            "language": str(SCHEMA.inLanguage),
        }
    }


def build_jsonld_graph(
    nodes: list[tuple],
    edges: list[tuple],
    metadata: list[tuple] | None = None,
    cmeta: dict[int, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Build JSON-LD @graph array with nodes and edges."""

    # Create metadata lookup
    metadata_lookup = {}
    if metadata:
        for m in metadata:
            metadata_lookup[m[0]] = {
                "label": m[1],
                "description": m[2],
                "source": m[3],
                "language": m[4],
            }

    graph = []

    # Add concept nodes
    for node in nodes:
        (
            concept_id,
            label,
            cluster_id,
            degree,
            betweenness,
            eigenvector,
            semantic_cohesion,
            bridge_score,
            diversity_local,
        ) = node
        concept_uri = GEMATRIA[str(concept_id)]

        # Use metadata if available, otherwise basic label
        meta = metadata_lookup.get(concept_id, {})
        final_label = meta.get("label", label or str(concept_id))

        node_data = {
            "@id": str(concept_uri),
            "@type": str(GEMATRIA.Concept),
            "label": final_label,
        }

        # Add optional metadata
        if meta.get("description"):
            node_data["description"] = meta["description"]
        if meta.get("source"):
            node_data["source"] = meta["source"]
        if meta.get("language"):
            node_data["language"] = meta["language"]

        # Add cluster and centrality data
        if cluster_id is not None:
            node_data["cluster"] = cluster_id
        if degree is not None:
            node_data["degree"] = float(degree)
        if betweenness is not None:
            node_data["betweenness"] = float(betweenness)
        if eigenvector is not None:
            node_data["eigenvector"] = float(eigenvector)

        # Add concept metrics
        if semantic_cohesion is not None:
            node_data["semanticCohesion"] = float(semantic_cohesion)
        if bridge_score is not None:
            node_data["bridgeScore"] = float(bridge_score)
        if diversity_local is not None:
            node_data["diversityLocal"] = float(diversity_local)

        # Attach cluster rollups
        cinfo = cmeta.get(cluster_id) if cmeta and cluster_id is not None else None
        if cinfo:
            node_data.update({k: v for k, v in cinfo.items() if v is not None})

        graph.append(node_data)

    # Add relation edges
    for edge in edges:
        source_id, target_id, cosine, rerank_score, decided_yes = edge
        edge_uri = GEMATRIA[f"edge/{source_id}-{target_id}"]

        edge_data = {
            "@id": str(edge_uri),
            "@type": str(GEMATRIA.Relation),
            "relatedTo": [str(GEMATRIA[str(source_id)]), str(GEMATRIA[str(target_id)])],
            "cosine": float(cosine) if cosine else 0.0,
        }

        if rerank_score is not None:
            edge_data["rerankScore"] = float(rerank_score)
        if decided_yes is not None:
            edge_data[str(GEMATRIA.decidedYes)] = bool(decided_yes)

        graph.append(edge_data)

    return graph


def create_rdf_graph(
    nodes: list[tuple], edges: list[tuple], metadata: list[tuple] | None = None
) -> Graph:
    """Create RDF graph using rdflib."""

    g = Graph()

    # Bind namespaces
    g.bind("gem", GEMATRIA)
    g.bind("schema", SCHEMA)
    g.bind("rdfs", RDFS)

    # Create metadata lookup
    metadata_lookup = {}
    if metadata:
        for m in metadata:
            metadata_lookup[m[0]] = {
                "label": m[1],
                "description": m[2],
                "source": m[3],
                "language": m[4],
            }

    # Add concept nodes
    for node in nodes:
        concept_id, label, cluster_id, degree, betweenness, eigenvector = node
        concept_uri = GEMATRIA[str(concept_id)]

        # Use metadata if available, otherwise basic label
        meta = metadata_lookup.get(concept_id, {})
        final_label = meta.get("label", label or str(concept_id))

        # Add type and label
        g.add((concept_uri, RDF.type, GEMATRIA.Concept))
        g.add((concept_uri, RDFS.label, Literal(final_label)))

        # Add optional metadata
        if meta.get("description"):
            g.add((concept_uri, SCHEMA.description, Literal(meta["description"])))
        if meta.get("source"):
            g.add((concept_uri, SCHEMA.source, Literal(meta["source"])))
        if meta.get("language"):
            g.add((concept_uri, SCHEMA.inLanguage, Literal(meta["language"])))

        # Add cluster and centrality data
        if cluster_id is not None:
            g.add((concept_uri, SCHEMA.category, Literal(cluster_id)))
        if degree is not None:
            g.add((concept_uri, GEMATRIA.degree, Literal(float(degree))))
        if betweenness is not None:
            g.add((concept_uri, GEMATRIA.betweenness, Literal(float(betweenness))))
        if eigenvector is not None:
            g.add((concept_uri, GEMATRIA.eigenvector, Literal(float(eigenvector))))

    # Add relation edges
    for edge in edges:
        source_id, target_id, cosine, rerank_score, decided_yes = edge
        edge_uri = GEMATRIA[f"edge/{source_id}-{target_id}"]
        source_uri = GEMATRIA[str(source_id)]
        target_uri = GEMATRIA[str(target_id)]

        # Add edge type and relationships
        g.add((edge_uri, RDF.type, GEMATRIA.Relation))
        g.add((edge_uri, SCHEMA.relatedTo, source_uri))
        g.add((edge_uri, SCHEMA.relatedTo, target_uri))
        g.add((edge_uri, SCHEMA.value, Literal(float(cosine) if cosine else 0.0)))

        if rerank_score is not None:
            g.add((edge_uri, GEMATRIA.rerankScore, Literal(float(rerank_score))))
        if decided_yes is not None:
            g.add((edge_uri, GEMATRIA.decidedYes, Literal(bool(decided_yes))))

    return g


def export_jsonld():
    """Main export function for JSON-LD and RDF formats."""

    log_json(LOG, 20, "export_jsonld_start")

    try:
        out_dir = os.getenv("EXPORT_DIR", "exports")
        os.makedirs(out_dir, exist_ok=True)

        db = get_gematria_rw()
        nodes, edges, metadata, cmeta = fetch_graph_data(db)

        # Create JSON-LD export
        context = create_jsonld_context()
        graph_data = build_jsonld_graph(nodes, edges, metadata, cmeta)

        jsonld_data = {**context, "@graph": graph_data}

        jsonld_path = os.path.join(out_dir, "graph_latest.jsonld")
        with open(jsonld_path, "w", encoding="utf-8") as f:
            json.dump(jsonld_data, f, indent=2, ensure_ascii=False)

        # Create RDF/Turtle export
        rdf_graph = create_rdf_graph(nodes, edges, metadata)
        ttl_path = os.path.join(out_dir, "graph_latest.ttl")
        rdf_graph.serialize(ttl_path, format="turtle")

        # Calculate stats
        node_count = len(nodes)
        edge_count = len(edges)
        cluster_count = len(set(n[2] for n in nodes if n[2] is not None))

        result = {
            "jsonld_path": jsonld_path,
            "ttl_path": ttl_path,
            "node_count": node_count,
            "edge_count": edge_count,
            "cluster_count": cluster_count,
            "export_complete": True,
            "metadata_available": metadata is not None,
        }

        log_json(LOG, 20, "export_jsonld_complete", **result)
        print(json.dumps(result))

    except Exception as e:
        log_json(LOG, 40, "export_jsonld_failed", error=str(e))
        print(json.dumps({"error": str(e)}))
        raise


if __name__ == "__main__":
    export_jsonld()
