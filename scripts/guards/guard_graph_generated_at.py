# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3

import json, os, sys, re

from datetime import datetime


TARGETS = ["exports/graph_latest.json", "exports/graph_stats.json"]
STRICT = os.getenv("STRICT_RFC3339", "0") == "1"


def is_rfc3339(ts: str) -> bool:
    # Accept 'Z' and offsets like +00:00
    try:
        t = ts.replace("Z", "+00:00")
        datetime.fromisoformat(t)
        # Basic RFC3339 shape check (YYYY-MM-DDThh:mm:ss(.frac)?(Z|±hh:mm))
        return bool(
            re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+\-]\d{2}:\d{2})$", ts)
        )
    except Exception:
        return False


def check_source(data, path):
    """Check metadata.source for fast-lane contract."""
    metadata = data.get("metadata", {})
    src = metadata.get("source") if isinstance(metadata, dict) else None
    if src == "fallback_fast_lane":
        print(f"OK: {path}: metadata.source=fallback_fast_lane present.", flush=True)
    else:
        print(
            f"HINT: {path}: metadata.source not 'fallback_fast_lane' (value="
            f"{src!r}); set when using orchestrator fast-lane.",
            flush=True,
        )


def validate_file(path):
    """Validate RFC3339 timestamp and metadata.source for a single file."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"HINT: {path} not found (fast-lane not run?); skipping.", flush=True)
        return True

    ts = data.get("generated_at")
    ok = isinstance(ts, str) and is_rfc3339(ts)

    if not ok:
        print(f"HINT: {path}: generated_at is missing or not RFC3339 (got={ts!r}).", flush=True)
        if STRICT:
            return False
    else:
        print(f"OK: {path}: generated_at RFC3339 = {ts}", flush=True)

    # Optional metadata friendliness
    check_source(data, path)
    return True


def main():
    paths = sys.argv[1:] if len(sys.argv) > 1 else TARGETS
    failed = False

    for path in paths:
        if not validate_file(path):
            failed = True

    if failed and STRICT:
        sys.exit(2)


if __name__ == "__main__":
    main()
