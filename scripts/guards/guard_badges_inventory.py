#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import time

REQUIRED = ["xrefs_coverage.svg", "xrefs_rate.svg", "rerank_quality.svg"]
BADGE_DIR = pathlib.Path("share/eval/badges")


def main() -> int:
    present = []
    if BADGE_DIR.exists():
        present = sorted(p.name for p in BADGE_DIR.iterdir() if p.suffix == ".svg")
    missing = [b for b in REQUIRED if b not in present]
    out = {
        "schema": "guard.badges-inventory.v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "ok": len(missing) == 0,
        "required": REQUIRED,
        "present": present,
        "missing": missing,
        "note": "HINT-only; non-fatal on PR/main",
    }
    pathlib.Path("evidence").mkdir(exist_ok=True)
    pathlib.Path("evidence/guard_badges_inventory.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(out))
    return 0  # HINT-only


if __name__ == "__main__":
    raise SystemExit(main())
