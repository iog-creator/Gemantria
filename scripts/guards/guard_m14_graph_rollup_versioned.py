from __future__ import annotations

import json, re

from pathlib import Path

from typing import Any, Dict


ROLLUP_PATH = Path("share/atlas/graph/rollup.json")

VERDICT_PATH = Path("evidence/guard_m14_graph_rollup_versioned.verdict.json")


def verdict(ok: bool, **extra: Any) -> int:
    VERDICT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload: Dict[str, Any] = {"ok": ok, **extra}
    VERDICT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0 if ok else 1


def main() -> int:
    if not ROLLUP_PATH.exists():
        return verdict(False, error="missing_rollup", path=str(ROLLUP_PATH))
    try:
        data = json.loads(ROLLUP_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        return verdict(False, error="invalid_json", detail=str(e))

    schema = data.get("schema", {})
    sid = schema.get("id")
    ver = schema.get("version")

    if not isinstance(sid, str) or not re.fullmatch(r"atlas\.graph\.rollup\.v\d+", sid or ""):
        return verdict(False, error="bad_schema_id", value=sid)

    if not isinstance(ver, int) or ver < 1:
        return verdict(False, error="bad_schema_version", value=ver)

    if "generated_at" not in data:
        return verdict(False, error="missing_generated_at")

    return verdict(True, schema=schema, has_generated_at=True)


if __name__ == "__main__":
    raise SystemExit(main())
