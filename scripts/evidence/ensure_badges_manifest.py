#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import time

ROOT = pathlib.Path(".")
EVID = ROOT / "evidence"
BADGES = [EVID / "badges" / "xrefs_coverage.svg", EVID / "badges" / "xrefs_rate.svg"]
METRICS = EVID / "xrefs_metrics.json"
OUT = EVID / "badges_manifest.json"


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    EVID.mkdir(parents=True, exist_ok=True)
    items = []
    if METRICS.exists():
        items.append({"path": str(METRICS), "sha256": sha256(METRICS)})
    for p in BADGES:
        if p.exists():
            items.append({"path": str(p), "sha256": sha256(p)})
    OUT.write_text(
        json.dumps(
            {
                "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "items": items,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    print(f"wrote {OUT} with {len(items)} item(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
