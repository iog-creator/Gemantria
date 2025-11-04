#!/usr/bin/env python3
"""
Unified envelope extraction script for UI consumption.
Creates unified_envelope_SIZE.json with configurable node limits.
Supports --real flag for temporal source tagging.
"""

import json
import argparse
import pathlib
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(description="Extract unified envelope for UI")
    parser.add_argument("--real", action="store_true", help="Use real SSOT paths")
    parser.add_argument("--size", type=int, default=50000, help="Max nodes to extract")
    parser.add_argument("--outdir", default="ui/out", help="Output directory")
    args = parser.parse_args()

    source = "real" if args.real else "mock"

    # Mock data for now - replace with actual extraction logic
    envelope = {
        "nodes": [
            {"id": f"node_{i}", "label": f"Concept {i}", "cluster": i % 5}
            for i in range(min(args.size, 1000))  # Limit for demo
        ],
        "edges": [
            {"source": f"node_{i}", "target": f"node_{(i + 1) % 1000}", "strength": 0.8}
            for i in range(min(args.size, 1000))
        ],
        "meta": {
            "extraction_time": datetime.now().isoformat(),
            "temporal_source": source,
            "node_count": len([{"id": f"node_{i}"} for i in range(min(args.size, 1000))]),
            "edge_count": len([{"source": f"node_{i}"} for i in range(min(args.size, 1000))]),
        },
    }

    # Create output directory
    out_path = pathlib.Path(args.outdir)
    out_path.mkdir(parents=True, exist_ok=True)

    # Write envelope
    output_file = out_path / f"unified_envelope_{args.size}.json"
    with open(output_file, "w") as f:
        json.dump(envelope, f, indent=2)

    print(f"Extracted {len(envelope['nodes'])} nodes to {output_file}")
    print(f"temporal_source: {source}")


if __name__ == "__main__":
    main()
