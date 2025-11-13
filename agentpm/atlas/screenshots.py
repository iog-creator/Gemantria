from __future__ import annotations

import json, os, time

from pathlib import Path

from typing import Dict, Any, List


SCHEMA_ID = "atlas.screenshots.manifest.v1"

SCHEMA_VERSION = 1

ALLOWED_KEYS = ("path","page_url","width","height")


def _items() -> List[Dict[str, Any]]:
    ids = ["node-001","node-002","node-003"]
    items = [{
        "path": f"/atlas/screenshots/{nid}.png",
        "page_url": f"/atlas/nodes/{nid}.html",
        "width": 100,
        "height": 100,
    } for nid in ids]
    items.sort(key=lambda x: x["path"])
    return items


def _canonicalize(d: Dict[str, Any]) -> Dict[str, Any]:
    return {k: d[k] for k in ALLOWED_KEYS if k in d}


def generate(out: Path, mode: str = "HINT") -> Dict[str, Any]:
    payload = {
        "schema": {"id": SCHEMA_ID, "version": SCHEMA_VERSION},
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mode": mode,
        "items": [_canonicalize(i) for i in _items()],
        "ok": True,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def main():
    out = Path(os.environ.get("SCREENSHOT_MANIFEST", "share/atlas/screenshots/manifest.json"))
    mode = os.environ.get("STRICT_MODE", "HINT").upper()
    generate(out, mode=mode)
    print(f"wrote: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

