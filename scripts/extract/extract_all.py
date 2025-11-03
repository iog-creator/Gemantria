#!/usr/bin/env python3
"""
extract_all.py - Phase 11 Unified Envelope Extractor

Merges graph_latest.json, temporal_patterns.json, pattern_forecast.json,
and correlation_weights.json into a single unified_envelope.json.

Usage:
    python scripts/extract/extract_all.py --size 10000 --outdir ui/out

Arguments:
    --size: Number of nodes to extract (default: 1000)
    --outdir: Output directory (default: ui/out)
    --graph: Path to graph_latest.json (default: share/exports/graph_latest.json)
    --temporal: Path to temporal_patterns.json (default: share/exports/temporal_patterns.json)
    --forecast: Path to pattern_forecast.json (default: share/exports/pattern_forecast.json)
    --correlations: Path to correlation_weights.json (default: share/exports/correlation_weights.json)
"""

import argparse
import json
import time
from pathlib import Path
from typing import Dict, Any


def load_json_file(path: str) -> Dict[str, Any] | None:
    """Load JSON file, return None if not found."""
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def generate_mock_graph(size: int) -> Dict[str, Any]:
    """Generate mock graph data for testing."""
    nodes = []
    edges = []

    for i in range(size):
        nodes.append(
            {
                "id": f"node-{i}",
                "gematria_value": 10 + (i % 90),  # Values between 10-99
                "hebrew_text": f"מילה{i}",  # Mock Hebrew text
                "book": "Genesis",
                "chapter": 1,
                "verse": i % 31 + 1,
            }
        )

    # Generate edges with mock similarity data (limited for performance)
    if size <= 1000:
        max_edges = min(size * 4, 10000)
        nodes_to_process = min(size, 1000)
        max_connections = 4
    elif size <= 10000:
        max_edges = 4000  # Fixed for 10k datasets
        nodes_to_process = min(size, 1000)
        max_connections = 2
    else:  # size > 10000 (like 100k)
        max_edges = 2000  # Very limited edges for performance
        nodes_to_process = 500  # Process only first 500 nodes
        max_connections = 1  # Only 1 connection per node

    edge_count = 0
    for i in range(nodes_to_process):
        if edge_count >= max_edges:
            break
        for j in range(i + 1, min(i + max_connections + 1, size)):
            if edge_count >= max_edges:
                break
            cosine_sim = 0.3 + (i + j) % 70 / 100  # Mock cosine similarity
            rerank_score = cosine_sim + ((i - j) % 20 - 10) / 100  # Mock rerank
            edge_strength = 0.5 * cosine_sim + 0.5 * rerank_score

            edges.append(
                {
                    "source": f"node-{i}",
                    "target": f"node-{j}",
                    "cosine": cosine_sim,
                    "rerank_score": rerank_score,
                    "edge_strength": edge_strength,
                    "correlation_weight": 0.6 + (i + j) % 40 / 100,  # >0.5 for COMPASS
                }
            )
            edge_count += 1

    return {
        "version": "graph-v1",
        "nodes": nodes,
        "edges": edges,
        "meta": {"node_count": len(nodes), "edge_count": len(edges), "algorithm": "mock-graph"},
    }


def generate_mock_temporal(size: int) -> Dict[str, Any]:
    """Generate mock temporal patterns data."""
    patterns = []

    # Generate some time series patterns
    for i in range(min(size // 10, 50)):  # One pattern per 10 nodes
        pattern = {
            "pattern_id": f"pattern-{i}",
            "timestamps": [f"2024-01-{day:02d}" for day in range(1, 32)],
            "frequencies": [(i * 10 + day) % 100 for day in range(1, 32)],
            "confidence": 0.8 + (i % 20) / 100,
            "trend": "increasing" if i % 2 == 0 else "decreasing",
        }
        patterns.append(pattern)

    return {
        "version": "temporal-v1",
        "patterns": patterns,
        "meta": {"pattern_count": len(patterns), "time_range": "2024-01-01 to 2024-01-31"},
    }


def generate_mock_forecast(size: int) -> Dict[str, Any]:
    """Generate mock forecast data."""
    forecasts = []

    for i in range(min(size // 20, 25)):  # One forecast per 20 nodes
        forecast = {
            "forecast_id": f"forecast-{i}",
            "pattern_id": f"pattern-{i}",
            "predictions": [100 + i * 5 + j for j in range(7)],  # 7-day forecast
            "lower_bounds": [90 + i * 5 + j for j in range(7)],
            "upper_bounds": [110 + i * 5 + j for j in range(7)],
            "confidence_intervals": [0.85 + (j % 10) / 100 for j in range(7)],
        }
        forecasts.append(forecast)

    return {
        "version": "forecast-v1",
        "forecasts": forecasts,
        "meta": {"forecast_count": len(forecasts), "horizon_days": 7},
    }


def generate_mock_correlations(size: int) -> Dict[str, Any]:
    """Generate mock correlation weights data."""
    correlations = []

    for i in range(min(size // 5, 200)):  # One correlation per 5 nodes
        correlation = {
            "source_pattern": f"pattern-{i % 10}",
            "target_pattern": f"pattern-{(i + 1) % 10}",
            "correlation_coefficient": 0.5 + (i % 50) / 100,  # >0.5 for COMPASS
            "significance": 0.95 + (i % 5) / 100,
            "edge_type": "strong" if i % 3 == 0 else "weak",
        }
        correlations.append(correlation)

    return {
        "version": "correlations-v1",
        "correlations": correlations,
        "meta": {"correlation_count": len(correlations), "threshold": 0.5},
    }


def merge_data_sources(
    graph_data: Dict, temporal_data: Dict, forecast_data: Dict, correlation_data: Dict, size: int
) -> Dict[str, Any]:
    """Merge all data sources into unified envelope format."""

    # Use graph data as base
    if not graph_data:
        graph_data = generate_mock_graph(size)

    # Ensure we have the right number of nodes
    nodes = graph_data["nodes"][:size]
    edges = [
        edge
        for edge in graph_data.get("edges", [])
        if edge["source"] in [n["id"] for n in nodes] and edge["target"] in [n["id"] for n in nodes]
    ]

    # Add temporal data if available
    temporal_patterns = []
    if temporal_data and "patterns" in temporal_data:
        temporal_patterns = temporal_data["patterns"]

    # Add forecast data if available
    forecasts = []
    if forecast_data and "forecasts" in forecast_data:
        forecasts = forecast_data["forecasts"]

    # Add correlation data if available
    correlations = []
    if correlation_data and "correlations" in correlation_data:
        correlations = correlation_data["correlations"]

    # Create unified envelope
    envelope = {
        "version": "unified-v1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "meta": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "temporal_patterns_count": len(temporal_patterns),
            "forecasts_count": len(forecasts),
            "correlations_count": len(correlations),
            "extraction_size": size,
            "source": "extract_all.py",
        },
        "nodes": nodes,
        "edges": edges,
        "temporal_patterns": temporal_patterns,
        "forecasts": forecasts,
        "correlations": correlations,
    }

    return envelope


def save_envelope(envelope: Dict[str, Any], outdir: str, size: int) -> str:
    """Save envelope to JSON file."""
    Path(outdir).mkdir(parents=True, exist_ok=True)
    filename = f"unified_envelope_{size}.json"
    filepath = Path(outdir) / filename

    with open(filepath, "w") as f:
        json.dump(envelope, f, indent=2, ensure_ascii=False)

    return str(filepath)


def main():
    parser = argparse.ArgumentParser(description="Phase 11 Unified Envelope Extractor")
    parser.add_argument("--size", type=int, default=1000, help="Number of nodes to extract")
    parser.add_argument("--outdir", default="ui/out", help="Output directory")
    parser.add_argument(
        "--graph", default="share/exports/graph_latest.json", help="Path to graph_latest.json"
    )
    parser.add_argument(
        "--temporal",
        default="share/exports/temporal_patterns.json",
        help="Path to temporal_patterns.json",
    )
    parser.add_argument(
        "--forecast",
        default="share/exports/pattern_forecast.json",
        help="Path to pattern_forecast.json",
    )
    parser.add_argument(
        "--correlations",
        default="share/exports/correlation_weights.json",
        help="Path to correlation_weights.json",
    )

    args = parser.parse_args()

    print(f">> Extracting unified envelope with {args.size} nodes...")

    start_time = time.time()

    # Load data sources (use mock data if not found)
    graph_data = load_json_file(args.graph)
    if graph_data:
        print(f"✓ Loaded graph data from {args.graph}")
    else:
        print(f"⚠️  Graph data not found at {args.graph}, using mock data")
        graph_data = generate_mock_graph(args.size)

    temporal_data = load_json_file(args.temporal)
    if temporal_data:
        print(f"✓ Loaded temporal data from {args.temporal}")
    else:
        print(f"⚠️  Temporal data not found at {args.temporal}, using mock data")
        temporal_data = generate_mock_temporal(args.size)

    forecast_data = load_json_file(args.forecast)
    if forecast_data:
        print(f"✓ Loaded forecast data from {args.forecast}")
    else:
        print(f"⚠️  Forecast data not found at {args.forecast}, using mock data")
        forecast_data = generate_mock_forecast(args.size)

    correlation_data = load_json_file(args.correlations)
    if correlation_data:
        print(f"✓ Loaded correlation data from {args.correlations}")
    else:
        print(f"⚠️  Correlation data not found at {args.correlations}, using mock data")
        correlation_data = generate_mock_correlations(args.size)

    # Merge into unified envelope
    envelope = merge_data_sources(
        graph_data, temporal_data, forecast_data, correlation_data, args.size
    )

    # Save envelope
    filepath = save_envelope(envelope, args.outdir, args.size)

    elapsed = time.time() - start_time

    print(">> Extraction complete:")
    print(f"  - Nodes: {envelope['meta']['node_count']}")
    print(f"  - Edges: {envelope['meta']['edge_count']}")
    print(f"  - Temporal patterns: {envelope['meta']['temporal_patterns_count']}")
    print(f"  - Forecasts: {envelope['meta']['forecasts_count']}")
    print(f"  - Correlations: {envelope['meta']['correlations_count']}")
    print(f"  - Time: {elapsed:.2f}s")
    print(f"  - Output: {filepath}")

    return envelope


if __name__ == "__main__":
    main()
