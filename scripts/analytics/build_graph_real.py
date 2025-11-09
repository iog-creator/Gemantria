#!/usr/bin/env python3
from __future__ import annotations
import json, os, pathlib, subprocess, sys

OUT = pathlib.Path("exports/graph_latest.scored.json")

def main() -> int:
    cmd = os.getenv("REAL_EXTRACT_CMD")
    if not cmd:
        print("[build_graph_real] REAL_EXTRACT_CMD not set", file=sys.stderr)
        return 2
    print(f"[build_graph_real] running: {cmd}")
    rc = subprocess.call(cmd, shell=True)
    if rc != 0:
        return rc
    if not OUT.exists() or OUT.stat().st_size == 0:
        print(f"[build_graph_real] expected {OUT} not found/empty", file=sys.stderr)
        return 3
    print(f"[build_graph_real] OK: {OUT} present")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
