"""Envelope ingest for MCP catalog (E03)."""

from __future__ import annotations

import json
import pathlib
import sys
import time
import uuid


def ingest(envelope_path: str) -> str:
    """Ingest an envelope file into share/mcp/envelopes/."""
    src = pathlib.Path(envelope_path)
    if not src.exists():
        raise FileNotFoundError(envelope_path)

    data = json.loads(src.read_text())
    outdir = pathlib.Path("share/mcp/envelopes")
    outdir.mkdir(parents=True, exist_ok=True)

    eid = data.get("id") or f"env-{uuid.uuid4().hex[:8]}"
    stamp = {
        "id": eid,
        "ingested_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "size": len(json.dumps(data)),
    }
    (outdir / f"{eid}.json").write_text(json.dumps({"envelope": data, "stamp": stamp}, indent=2))
    return str(outdir / f"{eid}.json")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ingest.py <envelope_path>", file=sys.stderr)
        sys.exit(1)
    print(ingest(sys.argv[1]))
