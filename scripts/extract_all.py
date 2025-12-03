# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
Unified envelope extraction script for UI consumption.
Creates unified_envelope_SIZE.json with configurable node limits.
Reads from exports/graph_latest.json (or graph_latest.scored.json) with Rule 045 fields.
"""

import json
import argparse
import pathlib
import sys
from datetime import datetime, UTC

# Add project root to path for imports
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def load_graph_export() -> dict:
    """
    Load graph export from SSOT paths.

    Tries in order:
    1. exports/graph_latest.scored.json (if exists)
    2. exports/graph_latest.json

    Returns:
        Graph data with nodes and edges (empty dict if not found)
    """
    candidates = [
        pathlib.Path("exports/graph_latest.scored.json"),
        pathlib.Path("exports/graph_latest.json"),
    ]

    for candidate in candidates:
        if candidate.exists():
            try:
                with open(candidate, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    print(f">> Loaded graph from {candidate}", file=sys.stderr)
                    return data
            except Exception as e:
                print(f">> Warning: Failed to load {candidate}: {e}", file=sys.stderr)
                continue

    print(">> Warning: No graph export found, returning empty graph", file=sys.stderr)
    return {"nodes": [], "edges": [], "metadata": {}}


def load_correlation_weights() -> dict:
    """
    Load Phase 10 correlation weights from graph export.

    Returns:
        Dict mapping (source, target) to correlation value (empty if not found)
    """
    # Correlation weights should already be in graph_latest.json edges
    # This function is for validation/checking only
    correlations_file = pathlib.Path("exports/graph_correlations.json")
    if correlations_file.exists():
        try:
            with open(correlations_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            correlations = data.get("correlations", [])
            print(f">> Found {len(correlations)} correlations in graph_correlations.json", file=sys.stderr)
            return {len(correlations): "available"}  # Just for logging
        except Exception as e:
            print(f">> Warning: Failed to load correlations file: {e}", file=sys.stderr)
    return {}


def load_temporal_patterns() -> list:
    """
    Load Phase 8 temporal patterns and transform to COMPASS format.

    COMPASS expects: [{"series": str, "timestamps": [str], "values": [float]}]

    Returns:
        List of temporal patterns in COMPASS format (empty list if not found)
    """
    temporal_file = pathlib.Path("exports/temporal_patterns.json")
    if not temporal_file.exists():
        print(">> Warning: temporal_patterns.json not found", file=sys.stderr)
        return []

    try:
        with open(temporal_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        patterns = data.get("temporal_patterns", [])
        compass_patterns = []

        for pattern in patterns:
            # Transform to COMPASS format
            series_id = pattern.get("series_id", "unknown")
            values = pattern.get("values", [])

            # Generate timestamps from position indices (if available)
            # Use start_index/end_index or generate sequential timestamps
            start_idx = pattern.get("start_index", 0)
            timestamps = [f"position_{start_idx + i}" for i in range(len(values))]

            compass_patterns.append(
                {
                    "series": series_id,
                    "timestamps": timestamps,
                    "values": values,
                }
            )

        print(f">> Loaded {len(compass_patterns)} temporal patterns", file=sys.stderr)
        return compass_patterns
    except Exception as e:
        print(f">> Warning: Failed to load temporal_patterns.json: {e}", file=sys.stderr)
        return []


def main():
    parser = argparse.ArgumentParser(description="Extract unified envelope for UI")
    parser.add_argument("--real", action="store_true", help="Use real SSOT paths (always true now)")
    parser.add_argument("--size", type=int, default=50000, help="Max nodes to extract")
    parser.add_argument("--outdir", default="ui/out", help="Output directory")
    args = parser.parse_args()

    # Load real graph export (no longer mock)
    graph_data = load_graph_export()

    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])
    metadata = graph_data.get("metadata", {})

    # Limit nodes to requested size
    if len(nodes) > args.size:
        node_ids = {n.get("id") for n in nodes[: args.size]}
        # Filter edges to only include connections between selected nodes
        edges = [e for e in edges if e.get("source") in node_ids and e.get("target") in node_ids]
        nodes = nodes[: args.size]
        print(f">> Limited to {args.size} nodes (from {len(graph_data.get('nodes', []))})", file=sys.stderr)

    # Load Phase 8 temporal patterns (for COMPASS validation)
    temporal_patterns = load_temporal_patterns()

    # Check for correlation weights in edges (Phase 10)
    edges_with_corr = sum(1 for e in edges if "correlation_weight" in e)
    correlation_available = edges_with_corr > 0

    # Build unified envelope with Rule 045 fields + Phase 10 correlation weights
    envelope = {
        "schema": "unified-v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "nodes": nodes,
        "edges": [
            {
                "source": e.get("source"),
                "target": e.get("target"),
                # Rule 045 fields (required for COMPASS validation)
                "cosine": e.get("cosine"),
                "rerank_score": e.get("rerank_score"),
                "edge_strength": e.get("edge_strength"),
                # Phase 10 correlation weights (for COMPASS validation)
                "correlation_weight": e.get("correlation_weight"),  # May be None if not available
                # Legacy compatibility (if needed)
                "strength": e.get("edge_strength") or e.get("strength"),
            }
            for e in edges
        ],
        "temporal_patterns": temporal_patterns,  # Phase 8 data (for COMPASS)
        "meta": {
            "extraction_time": datetime.now(UTC).isoformat(),
            "temporal_source": "real" if temporal_patterns else "missing",  # COMPASS expects this
            "correlation_weights": "real" if correlation_available else "missing",  # Phase 10 (COMPASS expects this)
            "source_file": str(metadata.get("export_timestamp", "unknown")),
            "node_count": len(nodes),
            "edge_count": len(edges),
            "edges_with_correlation_weight": edges_with_corr,  # For validation
            "original_node_count": len(graph_data.get("nodes", [])),
            "original_edge_count": len(graph_data.get("edges", [])),
        },
    }

    # Create output directory
    out_path = pathlib.Path(args.outdir)
    out_path.mkdir(parents=True, exist_ok=True)

    # Write envelope
    output_file = out_path / f"unified_envelope_{args.size}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(envelope, f, indent=2, ensure_ascii=False)

    print(f"Extracted {len(envelope['nodes'])} nodes, {len(envelope['edges'])} edges to {output_file}")
    print(f"temporal_source: {envelope['meta']['temporal_source']}")
    print(f"temporal_patterns: {len(temporal_patterns)} patterns")
    print(f"correlation_weights: {envelope['meta']['correlation_weights']} ({edges_with_corr} edges)")
    print(f"Rule 045 fields: cosine, rerank_score, edge_strength")
    print(f"Phase 10 field: correlation_weight")


if __name__ == "__main__":
    main()
