#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import re
import time

RFC3339_Z = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
TARGETS = [
    ("exports/graph_stats.json", ("graph-stats.",)),
    ("exports/graph_latest.json", ("graph.", "graph-v", "graph_latest")),
    ("exports/graph_latest.scored.json", ("graph.", "graph-v", "graph_latest")),
    ("share/eval/rerank_blend_report.json", ("rerank-blend.",)),
    ("share/eval/patterns.json", ("patterns.",)),
]


def check_file(path: pathlib.Path, prefixes: tuple[str, ...]) -> dict:
    if not path.exists():
        return {"file": str(path), "present": False, "ok": True, "note": "missing (HINT)"}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return {"file": str(path), "present": True, "ok": False, "error": f"json:{e}"}
    sch = str(data.get("schema", ""))
    ts = str(data.get("generated_at", ""))
    schema_ok = any(sch.startswith(p) for p in prefixes)
    ts_ok = bool(RFC3339_Z.match(ts))
    return {
        "file": str(path),
        "present": True,
        "schema": sch,
        "generated_at": ts,
        "ok": schema_ok and ts_ok,
        "schema_ok": schema_ok,
        "ts_ok": ts_ok,
    }


def main() -> int:
    results = [check_file(pathlib.Path(p), pf) for p, pf in TARGETS]
    ok = all(r.get("ok", True) for r in results if r.get("present"))
    out = {
        "schema": "guard.schema-smoke.v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "ok": ok,
        "results": results,
    }
    pathlib.Path("evidence").mkdir(exist_ok=True)
    pathlib.Path("evidence/guard_schema_smoke.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(out))
    # HINT-only: never fail CI; return 0 regardless
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
