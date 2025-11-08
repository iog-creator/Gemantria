# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

from __future__ import annotations

import json, os, sys, hashlib, pathlib


def is_ci() -> bool:
    return any(os.getenv(k) for k in ("CI", "GITHUB_ACTIONS", "GITLAB_CI", "BUILDKITE"))


def main() -> int:
    if is_ci():
        print("HINT[ingest.meta]: CI detected; noop (hermetic).")
        return 0

    out = os.getenv("OUT_FILE", "/tmp/p9-ingest-envelope.json")
    p = pathlib.Path(out)
    if not p.exists():
        print(f"ERR[ingest.meta]: envelope not found: {p}", file=sys.stderr)
        return 2

    b = p.read_bytes()
    meta = json.loads(b).get("meta", {})
    print("META:", json.dumps(meta, indent=2))
    print("SHA256:", hashlib.sha256(b).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
