import json, sys, pathlib

p = pathlib.Path(sys.argv[1])

d = json.load(p.open())

# Check for unified envelope structure
required_keys = ["temporal_patterns", "edges"]
if not all(k in d for k in required_keys):
    print("ERROR: not a unified envelope (missing temporal_patterns or edges).")
    sys.exit(2)

# Check edges have correlation_weight
edges = d.get("edges", [])
if edges and "correlation_weight" not in edges[0]:
    print("ERROR: not a unified envelope (edges missing correlation_weight).")
    sys.exit(2)

print("OK: unified envelope detected.")
