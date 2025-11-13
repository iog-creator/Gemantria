from __future__ import annotations

import json, re

from pathlib import Path

from typing import Any

DRILL_PATH = Path("share/atlas/nodes/drilldown.sample.json")

VERDICT_PATH = Path("evidence/guard_m14_node_drilldowns_links.verdict.json")


def write_verdict(ok: bool, **extra: Any) -> int:
    VERDICT_PATH.parent.mkdir(parents=True, exist_ok=True)
    VERDICT_PATH.write_text(json.dumps({"ok": ok, **extra}, indent=2) + "\n", encoding="utf-8")
    return 0 if ok else 1


def main() -> int:
    if not DRILL_PATH.exists():
        return write_verdict(False, error="missing_drilldown", path=str(DRILL_PATH))
    try:
        data = json.loads(DRILL_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        return write_verdict(False, error="invalid_json", detail=str(e))

    schema = data.get("schema", {})
    if schema.get("id") != "atlas.nodes.drilldown.v1":
        return write_verdict(False, error="bad_schema_id", value=schema.get("id"))

    if not isinstance(schema.get("version"), int) or schema["version"] < 1:
        return write_verdict(False, error="bad_schema_version", value=schema.get("version"))

    items = data.get("items", [])
    if not isinstance(items, list) or not items:
        return write_verdict(False, error="no_items")

    url_re = re.compile(r"^/atlas/nodes/[A-Za-z0-9\-_]+\.html$")
    for it in items:
        if not isinstance(it.get("id"), str):
            return write_verdict(False, error="bad_id", item=it)
        url = it.get("page_url")
        if not isinstance(url, str) or not url_re.fullmatch(url or ""):
            return write_verdict(False, error="bad_page_url", value=url)
        bl = it.get("backlinks")
        if not isinstance(bl, list) or not bl or not all(isinstance(b, str) and b.startswith("/atlas/") for b in bl):
            return write_verdict(False, error="bad_backlinks", value=bl)

    return write_verdict(True, count=len(items), schema=schema)


if __name__ == "__main__":
    raise SystemExit(main())
