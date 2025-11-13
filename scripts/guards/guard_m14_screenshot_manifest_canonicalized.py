from __future__ import annotations

import json, re

from pathlib import Path

from typing import Any, Dict, List


MANIFEST = Path("share/atlas/screenshots/manifest.json")

VERDICT = Path("evidence/guard_m14_screenshot_manifest_canonicalized.verdict.json")


def v(ok: bool, **extra: Any) -> int:
    VERDICT.parent.mkdir(parents=True, exist_ok=True)
    VERDICT.write_text(json.dumps({"ok": ok, **extra}, indent=2) + "\n", encoding="utf-8")
    return 0 if ok else 1


def main() -> int:
    if not MANIFEST.exists():
        return v(False, error="missing_manifest", path=str(MANIFEST))
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception as e:
        return v(False, error="invalid_json", detail=str(e))

    schema = data.get("schema", {})
    if schema.get("id") != "atlas.screenshots.manifest.v1":
        return v(False, error="bad_schema_id", value=schema.get("id"))
    if not isinstance(schema.get("version"), int) or schema["version"] < 1:
        return v(False, error="bad_schema_version", value=schema.get("version"))

    items: List[Dict[str, Any]] = data.get("items", [])
    if not isinstance(items, list) or not items:
        return v(False, error="no_items")

    allowed = {"path", "page_url", "width", "height"}
    path_re = re.compile(r"^/atlas/screenshots/[A-Za-z0-9\-_]+\.png$")
    page_re = re.compile(r"^/atlas/nodes/[A-Za-z0-9\-_]+\.html$")

    seen = set()
    for it in items:
        if set(it.keys()) != allowed:
            return v(False, error="non_canonical_keys", keys=list(it.keys()))
        p = it.get("path")
        pg = it.get("page_url")
        if not isinstance(p, str) or not path_re.fullmatch(p or ""):
            return v(False, error="bad_path", value=p)
        if not isinstance(pg, str) or not page_re.fullmatch(pg or ""):
            return v(False, error="bad_page_url", value=pg)
        w, h = it.get("width"), it.get("height")
        if not isinstance(w, int) or not isinstance(h, int) or w <= 0 or h <= 0:
            return v(False, error="bad_dims", value=(w, h))
        if p in seen:
            return v(False, error="duplicate_path", value=p)
        seen.add(p)

    if not all(items[i]["path"] <= items[i + 1]["path"] for i in range(len(items) - 1)):
        return v(False, error="not_sorted_by_path")

    return v(True, count=len(items), schema=schema, sorted_by="path")


if __name__ == "__main__":
    raise SystemExit(main())
