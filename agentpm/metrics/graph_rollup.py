from __future__ import annotations

import json, os, sys, time

from pathlib import Path

from typing import Dict, Any


SCHEMA_ID = "atlas.graph.rollup.v1"

SCHEMA_VERSION = 1


def generate(output_path: Path, mode: str = "HINT") -> Dict[str, Any]:
    """
    Generate a minimal, deterministic rollup receipt with versioning.

    - mode: "HINT" (no DB required) or "STRICT" (future: pull from DSN)
    """
    # Minimal placeholder metrics; filled with real values in future slices.
    metrics = {
        "nodes": 0,
        "edges": 0,
        "batches": 0,
    }
    payload = {
        "schema": {"id": SCHEMA_ID, "version": SCHEMA_VERSION},
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mode": mode,
        "metrics": metrics,
        "ok": True,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=False)
        f.write("\n")
    return payload


def main(argv: list[str]) -> int:
    out = Path(os.environ.get("GRAPH_ROLLUP_OUT", "share/atlas/graph/rollup.json"))
    mode = os.environ.get("STRICT_MODE", "HINT").upper()
    generate(out, mode=mode)
    print(f"wrote: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
