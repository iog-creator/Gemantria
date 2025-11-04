#!/usr/bin/env python3
"""
Test Hebrew label validation for graph exports.

Ensures that exported graph nodes have proper Hebrew labels
instead of UUID strings.
"""

import json
import re
import pytest
from pathlib import Path


def test_graph_labels_are_hebrew():
    """Test that graph_latest.json contains Hebrew labels, not UUIDs."""

    # Load the exported graph
    graph_path = Path("exports/graph_latest.json")
    assert graph_path.exists(), "graph_latest.json not found"

    with open(graph_path) as f:
        data = json.load(f)

    assert "nodes" in data, "Graph data missing nodes"
    assert len(data["nodes"]) > 0, "No nodes in graph"

    # Hebrew Unicode range: \u0590-\u05FF
    hebrew_pattern = re.compile(r"[\u0590-\u05FF]+")

    uuid_pattern = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

    hebrew_count = 0
    uuid_count = 0

    for node in data["nodes"]:
        label = node.get("label", "")
        node_id = node.get("id", "")

        # Labels should not be UUIDs
        assert not uuid_pattern.match(label), f"Node label is UUID: {label}"

        # Labels should contain Hebrew characters
        if hebrew_pattern.search(label):
            hebrew_count += 1
        elif label.startswith("Concept "):
            # Allow fallback labels for unmapped nodes
            pass
        else:
            # Unexpected label format
            pytest.fail(f"Unexpected label format: {label}")

        # Node IDs should be UUIDs (internal identifiers)
        assert uuid_pattern.match(str(node_id)), f"Node ID not UUID: {node_id}"

    # At least some labels should be Hebrew
    assert hebrew_count > 0, "No Hebrew labels found in graph"

    print(f"✅ Found {hebrew_count} Hebrew labels out of {len(data['nodes'])} nodes")


if __name__ == "__main__":
    test_graph_labels_are_hebrew()
    print("✅ Hebrew label validation passed")
