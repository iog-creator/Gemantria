#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

OUT = Path("docs/atlas/data/mcp_catalog.json")
STUB = {
    "version": 1,
    "endpoints": [
        {"name": "hybrid_search", "spec": {"inputs": ["q_text", "k"], "max_k": 25, "version": 1}},
        {
            "name": "graph_neighbors",
            "spec": {"inputs": ["node_id", "depth", "k"], "max_k": 25, "version": 1},
        },
        {
            "name": "lookup_ref",
            "spec": {"inputs": ["book", "chapter", "verse", "k"], "max_k": 25, "version": 1},
        },
    ],
}


def get_dsn() -> str:
    try:
        from scripts.config import env as _env

        ro = getattr(_env, "dsn_ro", lambda: None)()
        rw = getattr(_env, "dsn_rw", lambda: None)()
        return ro or rw or ""
    except Exception:
        return os.getenv("GEMATRIA_RO_DSN") or os.getenv("ATLAS_DSN_RO") or os.getenv("GEMATRIA_RW_DSN") or ""


def main() -> int:
    dsn = get_dsn()
    if not shutil.which("psql") or not dsn:
        OUT.write_text(json.dumps(STUB, indent=2))
        print("[export] SKIP: using stub (no psql or DSN)")
        return 0
    # Query: return endpoints as an array of {name, spec}
    q = r"\pset format unaligned \pset tuples_only on SELECT jsonb_build_object('version',1,'endpoints', jsonb_agg(jsonb_build_object('name',name,'spec',spec))) FROM mcp.catalog;"
    try:
        res = subprocess.run(["psql", dsn, "-c", q], capture_output=True, text=True, check=True)
        txt = res.stdout.strip().splitlines()[-1] if res.stdout else ""
        data = json.loads(txt) if txt else STUB
        OUT.write_text(json.dumps(data, indent=2))
        print("[export] OK: wrote docs/atlas/data/mcp_catalog.json")
        return 0
    except Exception as e:
        OUT.write_text(json.dumps(STUB, indent=2))
        print(f"[export] FALLBACK stub due to error: {e}", file=sys.stderr)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
