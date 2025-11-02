from __future__ import annotations

import json, os, sys, pathlib, math



def is_ci() -> bool:

    return any(os.getenv(k) for k in ("CI","GITHUB_ACTIONS","GITLAB_CI","BUILDKITE"))



def load_snapshot(path: str) -> dict:

    p = pathlib.Path(path)

    if not p.exists():

        print(f"ERR[p9.validate]: snapshot not found: {p}", file=sys.stderr)

        sys.exit(2)

    return json.loads(p.read_text(encoding="utf-8"))



def compute_metrics(d: dict) -> dict:

    nodes = len(d.get("nodes", []))

    edges = len(d.get("edges", []))

    # simple undirected density: 2E / (N(N-1)) ; define 0 if N<2

    density = 0.0

    if nodes >= 2:

        density = (2.0 * edges) / (nodes * (nodes - 1))

    return {"nodes": nodes, "edges": edges, "density": round(density, 6)}



def main() -> int:

    if is_ci():

        print("HINT[p9.validate]: CI detected; noop (hermetic).")

        return 0

    snap = os.getenv("SNAPSHOT_FILE", "docs/phase9/example_snapshot.json")

    seed = int(os.getenv("P9_SEED", "42"))

    data = load_snapshot(snap)

    metrics = compute_metrics(data)

    envelope = {

        "meta": {

            "version": "0.1.0",

            "source": "p9-validate-local",

            "snapshot_path": snap,

            "seed": seed

        },

        "metrics": metrics

    }

    print(json.dumps(envelope, indent=2))

    return 0



if __name__ == "__main__":

    raise SystemExit(main())
