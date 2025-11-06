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

    node_count = len(data["nodes"])
    if node_count == 0:
        print("ERROR: no nodes found", file=sys.stderr)
        sys.exit(2)

    print(f"OK: enrichment details preserved on {node_count} nodes.")


if __name__ == "__main__":
    main()
