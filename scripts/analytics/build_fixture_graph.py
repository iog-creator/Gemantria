#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import time

TRUTH = pathlib.Path("tests/fixtures/extraction_truth.json")
OUT = pathlib.Path("exports/graph_latest.scored.json")


def main() -> int:
    items = []
    if TRUTH.exists():
        data = json.loads(TRUTH.read_text(encoding="utf-8"))
        for i, it in enumerate(data.get("items", []), 1):
            vid = str(it.get("verse_id"))
            nouns = [str(x) for x in (it.get("nouns") or [])]
            if vid:
                items.append({"id": f"N:{i}", "verse_id": vid, "nouns": nouns})
    graph = {
        "schema": "graph.vfixture",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "nodes": items,
        "edges": [],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[fixture-graph] wrote {OUT} (nodes={len(items)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
