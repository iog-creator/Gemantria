#!/usr/bin/env python3

import json, os, sys, re

from datetime import datetime


PATH = sys.argv[1] if len(sys.argv) > 1 else "exports/graph_latest.json"
STRICT = os.getenv("STRICT_RFC3339", "0") == "1"


def is_rfc3339(ts: str) -> bool:
    # Accept 'Z' and offsets like +00:00
    try:
        t = ts.replace("Z", "+00:00")
        datetime.fromisoformat(t)
        # Basic RFC3339 shape check (YYYY-MM-DDThh:mm:ss(.frac)?(Z|±hh:mm))
        return bool(re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+\-]\d{2}:\d{2})$", ts))
    except Exception:
        return False


def main():
    try:
        with open(PATH, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"HINT: {PATH} not found (fast-lane not run?); skipping.", flush=True)
        sys.exit(0)

    ts = data.get("generated_at")
    ok = isinstance(ts, str) and is_rfc3339(ts)

    if not ok:
        print(f"HINT: graph_latest.generated_at is missing or not RFC3339 (got={ts!r}).", flush=True)
        if STRICT:
            sys.exit(2)
    else:
        print(f"OK: graph_latest.generated_at RFC3339 = {ts}", flush=True)

    # Optional metadata friendliness
    metadata = data.get("metadata", {})
    src = metadata.get("source") if isinstance(metadata, dict) else None
    if src == "fallback_fast_lane":
        print("OK: metadata.source=fallback_fast_lane present.", flush=True)
    else:
        print(
            "HINT: metadata.source not 'fallback_fast_lane' (value="
            f"{src!r}); ensure set when using orchestrator fast-lane.",
            flush=True,
        )


if __name__ == "__main__":
    main()
