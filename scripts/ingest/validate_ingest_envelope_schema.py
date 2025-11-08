# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

from __future__ import annotations

import json, os, sys, pathlib

from typing import Any, Dict, List


def is_ci() -> bool:
    return any(os.getenv(k) for k in ("CI", "GITHUB_ACTIONS", "GITLAB_CI", "BUILDKITE"))


def error(msg: str) -> None:
    print(msg, file=sys.stderr)


def ensure_str(d: Dict[str, Any], k: str, errs: List[str]) -> None:
    if k not in d:
        errs.append(f"meta.{k} missing")
        return
    if not isinstance(d[k], str) and k != "seed":
        errs.append(f"meta.{k} wrong type")


def main() -> int:
    if is_ci():
        print("HINT[p9.ingest.schema]: CI detected; noop (hermetic).")
        return 0
    if len(sys.argv) < 2:
        error("usage: python3 scripts/ingest/validate_ingest_envelope_schema.py <envelope.json>")
        return 2
    p = pathlib.Path(sys.argv[1])
    if not p.exists():
        error(f"ERR[p9.ingest.schema]: not found: {p}")
        return 2
    env = json.loads(p.read_text(encoding="utf-8"))

    errs: List[str] = []
    if not isinstance(env, dict):
        errs.append("envelope must be an object")
    meta = env.get("meta")
    nodes = env.get("nodes")
    edges = env.get("edges")

    if not isinstance(meta, dict):
        errs.append("meta must be an object")
    else:
        for k in ("version", "source", "snapshot_path"):
            ensure_str(meta, k, errs)
        if "seed" not in meta:
            errs.append("meta.seed missing")
        elif not isinstance(meta["seed"], int):
            errs.append("meta.seed wrong type")

    if not isinstance(nodes, list):
        errs.append("nodes must be an array")
    if not isinstance(edges, list):
        errs.append("edges must be an array")

    # Spot-check a few node/edge fields for shape (not exhaustive)
    if isinstance(nodes, list) and nodes:
        n0 = nodes[0]
        if not isinstance(n0, dict):
            errs.append("nodes[0] must be object")
        else:
            if "id" not in n0 or "label" not in n0:
                errs.append("nodes[0] missing id/label")
    if isinstance(edges, list) and edges:
        e0 = edges[0]
        if not isinstance(e0, dict):
            errs.append("edges[0] must be object")
        else:
            for req in ("src", "dst", "rel_type"):
                if req not in e0:
                    errs.append(f"edges[0] missing {req}")

    if errs:
        print("SCHEMA_ERRORS:")
        for e in errs:
            print(f"- {e}")
        return 3
    print("SCHEMA_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
