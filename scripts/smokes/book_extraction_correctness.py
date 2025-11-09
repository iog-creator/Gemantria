#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import time

GRAPH_CANDIDATES = [
    pathlib.Path("exports/graph_latest.scored.json"),
    pathlib.Path("exports/graph_latest.json"),
]


def _load_graph():
    for p in GRAPH_CANDIDATES:
        if p.exists():
            d = json.loads(p.read_text(encoding="utf-8"))
            return d, str(p)
    return {"nodes": [], "edges": []}, "missing"


def _guess_book(n: dict) -> str | None:
    # Heuristics to stay hermetic across schemas
    for k in ("book", "book_id", "book_name"):
        if k in n:
            return str(n[k])
    meta = n.get("meta") or n.get("metadata") or {}
    for k in ("book", "book_id", "book_name"):
        if k in meta:
            return str(meta[k])
    return None


def main() -> int:
    graph, src = _load_graph()
    nodes = graph.get("nodes", [])
    # Collect simple book coverage + duplicate verse id heuristic
    books, verse_ids = set(), set()
    dup_verses = 0
    for n in nodes:
        b = _guess_book(n)
        if b:
            books.add(b)
        vid = n.get("verse_id") or (n.get("meta") or {}).get("verse_id")
        if vid is not None:
            if vid in verse_ids:
                dup_verses += 1
            else:
                verse_ids.add(vid)
    ok = bool(nodes) and (dup_verses == 0)
    out = {
        "schema": "smoke.book-extraction.v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": {"mode": "file_first", "input": src},
        "counts": {"nodes": len(nodes), "books": len(books), "verse_ids": len(verse_ids)},
        "issues": {"duplicate_verse_ids": dup_verses},
        "ok": ok,
        "note": "HINT-only smoke; returns 0 regardless",
    }
    pathlib.Path("evidence").mkdir(exist_ok=True)
    pathlib.Path("evidence/book_extraction_smoke.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
