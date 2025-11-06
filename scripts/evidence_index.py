#!/usr/bin/env python3
"""
Evidence Index Generator

Creates a rolling catalog of runs for debugging and monitoring.
"""

import json
import glob
import os
import time
import re


def items(pat):
    out = []
    for p in sorted(glob.glob(pat)):
        try:
            j = json.load(open(p))
        except Exception:
            continue
        out.append(
            {
                "path": p,
                "ts": int(os.path.getmtime(p)),
                "kind": re.sub(r".*evidence/(.+?)_", r"\1", p),
                "summary": {
                    "models_used": j.get("models_used"),
                    "run": j.get("run"),
                    "budget": j.get("budget"),
                    "timing": {k: j.get(k) for k in ("timing_p50_ms", "timing_p95_ms", "timing_p99_ms", "tps")},
                },
            }
        )
    return out


def main():
    idx = {
        "generated_at": int(time.time()),
        "summaries": items("share/evidence/*summary_*.json")[-200:],  # last 200
        "results": items("share/evidence/*result_*.json")[-200:],
        "starts": items("share/evidence/*start_*.json")[-200:],
    }
    print(json.dumps(idx, indent=2))


if __name__ == "__main__":
    main()
