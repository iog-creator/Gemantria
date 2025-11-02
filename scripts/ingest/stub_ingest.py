from __future__ import annotations

import json, os, sys, pathlib


def is_ci() -> bool:
    return any(os.getenv(k) for k in ("CI", "GITHUB_ACTIONS", "GITLAB_CI", "BUILDKITE"))


def main() -> int:
    if is_ci():
        print("HINT[p9.ingest]: CI detected; no DB/network. noop by design.")

        return 0

    snap = os.getenv("SNAPSHOT_FILE", "docs/phase9/example_snapshot.json")

    p = pathlib.Path(snap)

    if not p.exists():
        print(f"ERR[p9.ingest]: snapshot not found: {p}", file=sys.stderr)

        return 2

    data = json.loads(p.read_text(encoding="utf-8"))

    # minimal stats only; no external calls; deterministic

    nodes = len(data.get("nodes", []))

    edges = len(data.get("edges", []))

    print(json.dumps({"snapshot": str(p), "nodes": nodes, "edges": edges}, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
