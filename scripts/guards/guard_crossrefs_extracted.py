# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3

import sys, json, os


def main():
    if not os.path.exists("exports/ai_nouns.json"):
        print("ERROR: exports/ai_nouns.json not found", file=sys.stderr)
        sys.exit(2)

    with open("exports/ai_nouns.json") as f:
        data = json.load(f)

    if "nodes" not in data:
        print("ERROR: no nodes in ai_nouns.json", file=sys.stderr)
        sys.exit(2)

    total_nodes = len(data["nodes"])
    nodes_with_crossrefs = 0

    for node in data["nodes"]:
        enrichment = node.get("enrichment", {})
        crossrefs = enrichment.get("crossrefs", [])
        if crossrefs and len(crossrefs) > 0:
            nodes_with_crossrefs += 1

    if nodes_with_crossrefs == 0:
        print("ERROR: no nodes with crossrefs found", file=sys.stderr)
        sys.exit(2)

    print(f"OK: crossrefs extracted for {nodes_with_crossrefs}/{total_nodes} verse-mentioning nouns.")


if __name__ == "__main__":
    main()
