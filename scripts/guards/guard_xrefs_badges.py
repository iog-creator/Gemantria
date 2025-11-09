#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import pathlib
import time

XREF_INDEX = pathlib.Path("ui/public/xrefs/xrefs_index.v1.json")
BADGE_DIR = pathlib.Path("share/eval/badges")
BADGES = [BADGE_DIR / "xrefs_coverage.svg", BADGE_DIR / "xrefs_rate.svg"]


def emit(ok: bool, note: str, missing: list[str]):
    out = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "guard": "guard_xrefs_badges",
        "ok": ok,
        "note": note,
        "inputs": {
            "xref_index_exists": XREF_INDEX.exists(),
            "xref_index_path": str(XREF_INDEX),
        },
        "badges": {
            "dir": str(BADGE_DIR),
            "required": [str(p) for p in BADGES],
            "missing": missing,
        },
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    strict = os.environ.get("STRICT_XREF_BADGES", "0") == "1"
    if strict and not ok:
        return 1
    return 0


def main() -> int:
    # Fast no-op: let CI tell us to skip this check entirely on PRs
    if os.environ.get("CI_XREF_BADGES_SKIP", "0") == "1":
        return emit(True, "skipped by CI (paths do not affect xref badges)", [])
    # If no xref index, HINT-ok (nothing to check).
    if not XREF_INDEX.exists():
        return emit(True, "xref index not present; skipping badge check (HINT).", [])

    missing = [str(p) for p in BADGES if not p.exists()]
    ok = len(missing) == 0
    note = "xref badges present" if ok else "some xref badges are missing"

    return emit(ok, note, missing)


if __name__ == "__main__":
    raise SystemExit(main())
