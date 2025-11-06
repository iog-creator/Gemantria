#!/usr/bin/env python3
"""
Build graph from AI-discovered and enriched nouns.
"""

import json
import os
import sys

from src.graph.graph import build_graph
from src.nodes.network_aggregator import _ensure_nouns_in_concepts


def main():
    """
    Loads enriched nouns and builds the graph, saving it to exports.
    """
    input_file = os.getenv("INPUT", "exports/ai_nouns.enriched.json")
    output_file = os.getenv("OUTPUT", "exports/graph_latest.json")

    if not os.path.exists(input_file):
        print(f"Error: Input file not found at {input_file}", file=sys.stderr)
        sys.exit(1)

    with open(input_file, encoding="utf-8") as f:
        data = json.load(f)

    nouns = data.get("nodes", [])
    graph = build_graph(nouns)

    # Ensure nouns are stored in database
    try:
        import psycopg

        dsn = os.getenv("GEMATRIA_DSN")
        if dsn:
            with psycopg.connect(dsn) as conn:
                _ensure_nouns_in_concepts(conn, nouns)
            print(f"Inserted/updated {len(nouns)} nouns in concepts table")
        else:
            print("Warning: GEMATRIA_DSN not set, skipping database storage")
    except Exception as e:
        print(f"Warning: Failed to store nouns in database: {e}")

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2, ensure_ascii=False)

    print(
        f"Graph with {len(graph.get('nodes', []))} nodes and {len(graph.get('edges', []))} edges saved to {output_file}"
    )


if __name__ == "__main__":
    main()
