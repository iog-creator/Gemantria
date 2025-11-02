from __future__ import annotations

import json, os, sys, pathlib

REQ_META = {"version": str, "source": str, "snapshot_path": str, "seed": int}
REQ_METRICS = {"nodes": int, "edges": int, "density": (int, float)}


def is_ci() -> bool:
    return any(os.getenv(k) for k in ("CI", "GITHUB_ACTIONS", "GITLAB_CI", "BUILDKITE"))


def type_ok(v, t):
    if isinstance(t, tuple):
        return isinstance(v, t)
    return isinstance(v, t)


def validate_envelope(env: dict) -> list[str]:
    errs = []
    if not isinstance(env, dict):
        return ["Envelope must be an object"]
    meta = env.get("meta")
    metrics = env.get("metrics")
    if not isinstance(meta, dict):
        errs.append("meta must be an object")
    else:
        for k, t in REQ_META.items():
            if k not in meta:
                errs.append(f"meta.{k} missing")
            elif not type_ok(meta[k], t):
                errs.append(f"meta.{k} wrong type")
    if not isinstance(metrics, dict):
        errs.append("metrics must be an object")
    else:
        for k, t in REQ_METRICS.items():
            if k not in metrics:
                errs.append(f"metrics.{k} missing")
            elif not type_ok(metrics[k], t):
                errs.append(f"metrics.{k} wrong type")
        # numeric constraints
        if isinstance(metrics.get("nodes"), int) and metrics["nodes"] < 0:
            errs.append("metrics.nodes < 0")
        if isinstance(metrics.get("edges"), int) and metrics["edges"] < 0:
            errs.append("metrics.edges < 0")
        if isinstance(metrics.get("density"), (int, float)) and metrics["density"] < 0:
            errs.append("metrics.density < 0")
    return errs


def main(argv=None) -> int:
    if is_ci():
        print("HINT[p9.schema]: CI detected; noop (hermetic).")
        return 0
    if len(sys.argv) < 2:
        print(
            "usage: python3 scripts/ingest/validate_envelope_schema.py <envelope.json>",
            file=sys.stderr,
        )
        return 2
    path = pathlib.Path(sys.argv[1])
    if not path.exists():
        print(f"ERR[p9.schema]: not found: {path}", file=sys.stderr)
        return 2
    env = json.loads(path.read_text(encoding="utf-8"))
    errs = validate_envelope(env)
    if errs:
        print("SCHEMA_ERRORS:")
        for e in errs:
            print(f"- {e}")
        return 3
    print("SCHEMA_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
