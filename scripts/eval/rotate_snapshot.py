# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVAL = ROOT / "share" / "eval"
CUR = EVAL / "graph_latest.json"
PREV = EVAL / "graph_prev.json"


def main() -> int:
    if not CUR.exists():
        print("[snapshot.rotate] missing", CUR.relative_to(ROOT))
        return 2
    try:
        # sanity: valid json
        json.loads(CUR.read_text(encoding="utf-8"))
    except Exception as e:
        print("[snapshot.rotate] invalid current graph:", e)
        return 3
    shutil.copy2(CUR, PREV)
    print(f"[snapshot.rotate] {CUR.relative_to(ROOT)} → {PREV.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
