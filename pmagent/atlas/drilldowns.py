from __future__ import annotations

import json, os, sys, time

from pathlib import Path

from typing import List, Dict, Any

SCHEMA_ID = "atlas.nodes.drilldown.v1"

SCHEMA_VERSION = 1


def sample_nodes() -> List[Dict[str, Any]]:
    # Minimal, deterministic sample; future slices may read a manifest.
    ids = ["node-001", "node-002", "node-003"]
    items = []
    for nid in ids:
        items.append(
            {
                "id": nid,
                "page_url": f"/atlas/nodes/{nid}.html",
                "backlinks": ["/atlas/index.html"],
            }
        )
    return items


def generate(output_path: Path, mode: str = "HINT") -> Dict[str, Any]:
    payload = {
        "schema": {"id": SCHEMA_ID, "version": SCHEMA_VERSION},
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mode": mode,
        "items": sample_nodes(),
        "ok": True,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def main(argv):
    out = Path(os.environ.get("DRILL_PATH", "share/atlas/nodes/drilldown.sample.json"))
    mode = os.environ.get("STRICT_MODE", "HINT").upper()
    generate(out, mode=mode)
    print(f"wrote: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
