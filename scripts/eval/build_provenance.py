# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
import hashlib
import json
import os
import pathlib
import subprocess
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVAL = ROOT / "share" / "eval"
OUT = EVAL / "provenance.json"


def sha256_path(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def git(cmd):
    try:
        return subprocess.check_output(["git", *cmd], cwd=ROOT).decode().strip()
    except Exception:
        return None


def safe_json(p: pathlib.Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def main() -> int:
    cur = safe_json(EVAL / "graph_latest.json") or {}
    man = safe_json(EVAL / "release_manifest.json") or {}

    nodes = len(cur.get("nodes", []))
    edges = len(cur.get("edges", []))
    artifacts = man.get("artifact_count")
    commit = git(["rev-parse", "--short", "HEAD"])
    branch = git(["rev-parse", "--abbrev-ref", "HEAD"])
    tag = git(["describe", "--tags", "--dirty", "--always"])
    py = os.environ.get("PYTHON_VERSION")
    prov = {
        "generated_at": int(time.time()),
        "git": {"commit": commit, "branch": branch, "describe": tag},
        "env": {"python": py, "rerank_provider": os.environ.get("RERANK_PROVIDER", "none")},
        "counts": {"nodes": nodes, "edges": edges, "artifacts": artifacts},
        "hashes": {
            "graph_latest.json": sha256_path(EVAL / "graph_latest.json")
            if (EVAL / "graph_latest.json").exists()
            else None,
            "graph_prev.json": sha256_path(EVAL / "graph_prev.json") if (EVAL / "graph_prev.json").exists() else None,
            "release_manifest.json": sha256_path(EVAL / "release_manifest.json")
            if (EVAL / "release_manifest.json").exists()
            else None,
        },
        "delta_present": (EVAL / "delta.json").exists(),
        "centrality_present": (EVAL / "centrality.json").exists(),
    }
    OUT.write_text(json.dumps(prov, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[provenance] wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
