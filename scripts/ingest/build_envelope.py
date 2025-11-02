from __future__ import annotations

import json, os, sys, pathlib

from typing import Any, Dict, List

from scripts.ingest.mappers import map_node, map_edge
from datetime import datetime


def is_ci() -> bool:
    return any(os.getenv(k) for k in ("CI", "GITHUB_ACTIONS", "GITLAB_CI", "BUILDKITE"))


def load_snapshot(path: str) -> Dict[str, Any]:
    p = pathlib.Path(path)
    if not p.exists():
        print(f"ERR[p9.envelope]: snapshot not found: {p}", file=sys.stderr)
        sys.exit(2)
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
    if is_ci():
        print("HINT[p9.envelope]: CI detected; noop (hermetic).")
        return 0

    snap = os.getenv("SNAPSHOT_FILE", "docs/phase9/example_snapshot.json")
    seed = int(os.getenv("P9_SEED", "42"))
    # Deterministic override for created_at to keep local runs reproducible when desired
    created_at = os.getenv("P9_CREATED_AT") or datetime.now().isoformat(timespec="seconds")
    out_path = os.getenv("OUT_FILE", "/tmp/p9-ingest-envelope.json")

    data = load_snapshot(snap)
    raw_nodes: List[Dict[str, Any]] = data.get("nodes", [])
    raw_edges: List[Dict[str, Any]] = data.get("edges", [])

    nodes = [map_node(n) for n in raw_nodes]
    edges = [map_edge(e) for e in raw_edges]

    envelope = {
        "meta": {
            "version": "0.1.0",
            "source": "p9-envelope-local",
            "snapshot_path": snap,
            "seed": seed,
            "created_at": created_at,
        },
        "nodes": nodes,
        "edges": edges,
    }
    s = json.dumps(envelope, indent=2)
    pathlib.Path(out_path).write_text(s, encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
