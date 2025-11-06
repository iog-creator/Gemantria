#!/usr/bin/env python3
"""
Guard script to verify pipeline node sequence matches documentation.

Enforces that src/graph/graph.py calls nodes in the canonical order:
1) collect_nouns → 2) validate_batch → 3) enrichment → 4) confidence_validator →
5) network_aggregator → 6) schema_validator → 7) analysis_runner → 8) wrap_hints

Related Rules: Rule-060 (Pipeline Node Sequence)
"""

import re
import sys
from pathlib import Path

# Canonical node sequence (must match AGENTS.md and graph.py)
ORDER = [
    "collect_nouns_node",
    "validate_batch_node",
    "enrichment_node",
    "confidence_validator_node",
    "network_aggregator_node",
    "schema_validator_node",
    "analysis_runner_node",
    "wrap_hints_node",
]

GRAPH_FILE = Path("src/graph/graph.py")


def main():
    """Check that pipeline nodes are called in the correct order."""
    if not GRAPH_FILE.exists():
        print(f"ERROR: {GRAPH_FILE} not found", file=sys.stderr)
        sys.exit(2)

    content = GRAPH_FILE.read_text(encoding="utf-8")

    # Find all node function calls in the main() function
    # Look for patterns like: state = collect_nouns_node(state)
    # or: state = node_module.node_function(state)
    idxs = []
    missing_nodes = []

    for name in ORDER:
        # Match both direct calls (node_function(state)) and module calls (module.node_function(state))
        pattern = rf"\b{re.escape(name)}\s*\("
        matches = list(re.finditer(pattern, content))

        if not matches:
            missing_nodes.append(name)
            continue

        # Find the first occurrence in the main() function
        # (after "def main(" but before any other function definitions)
        main_start = content.find("def main(")
        if main_start == -1:
            print(f"ERROR: main() function not found in {GRAPH_FILE}", file=sys.stderr)
            sys.exit(2)

        # Find the end of main() function (next def or end of file)
        main_end = content.find("\ndef ", main_start + 1)
        if main_end == -1:
            main_end = len(content)

        main_content = content[main_start:main_end]

        # Find the position of this node call within main()
        node_match = re.search(pattern, main_content)
        if node_match:
            idxs.append((name, main_start + node_match.start()))
        else:
            missing_nodes.append(name)

    if missing_nodes:
        print(f"ERROR: missing node calls: {', '.join(missing_nodes)}", file=sys.stderr)
        sys.exit(2)

    # Verify order (indices should be in ascending order)
    if len(idxs) != len(ORDER):
        print(f"ERROR: expected {len(ORDER)} nodes, found {len(idxs)}", file=sys.stderr)
        sys.exit(2)

    # Check if indices are in order
    sorted_idxs = sorted(idxs, key=lambda x: x[1])
    node_names = [name for name, _ in sorted_idxs]

    if node_names != ORDER:
        print("ERROR: pipeline nodes out of order", file=sys.stderr)
        print(f"Expected: {ORDER}", file=sys.stderr)
        print(f"Found:    {node_names}", file=sys.stderr)
        sys.exit(2)

    print("OK: pipeline sequence present and ordered.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
