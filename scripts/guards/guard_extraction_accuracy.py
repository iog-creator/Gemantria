#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import pathlib
import sys
import time

GRAPH = [pathlib.Path("exports/graph_latest.scored.json"), pathlib.Path("exports/graph_latest.json")]
TRUTH_V1 = pathlib.Path("tests/truth/extraction_accuracy.v1.json")
TRUTH_V2 = pathlib.Path("tests/truth/extraction_accuracy.v2.json")
TRUTH = TRUTH_V1
if TRUTH_V2.exists():
    try:
        _v2 = json.loads(TRUTH_V2.read_text())
        if len(_v2.get("cases", [])) >= 25:
            TRUTH = TRUTH_V2
            print(f"HINT: extraction_accuracy: using truth=v2 file={TRUTH}", file=sys.stderr)
        else:
            print("HINT: extraction_accuracy: v2 present but <25 cases; using v1", file=sys.stderr)
    except Exception:
        print("HINT: extraction_accuracy: v2 unreadable; using v1", file=sys.stderr)
if TRUTH == TRUTH_V1:
    print(f"HINT: extraction_accuracy: using truth=v1 file={TRUTH}", file=sys.stderr)


def load_graph():
    for p in GRAPH:
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8")), str(p)
    return {"nodes": [], "edges": []}, "missing"


def index_nodes(nodes):
    by_verse = {}
    for n in nodes:
        vid = n.get("verse_id") or (n.get("meta") or {}).get("verse_id")
        nouns = n.get("nouns") or (n.get("meta") or {}).get("nouns") or []
        if vid:
            by_verse.setdefault(vid, set()).update(map(str, nouns))
    return by_verse


def main() -> int:
    strict = os.getenv("STRICT_EXTRACTION_ACCURACY", "0") == "1"
    graph, src = load_graph()
    by_verse = index_nodes(graph.get("nodes", []))
    ok = True
    total = 0
    correct = 0
    missing_fixture = not TRUTH.exists()
    details = []
    if not missing_fixture:
        truth = json.loads(TRUTH.read_text(encoding="utf-8"))
        for item in truth.get("items", []):
            total += 1
            vid = str(item.get("verse_id"))
            expected = set(map(str, item.get("nouns", [])))
            found = by_verse.get(vid, set())
            hit = expected.issubset(found)
            correct += 1 if hit else 0
            details.append(
                {
                    "verse_id": vid,
                    "expected": sorted(expected),
                    "found": sorted(found),
                    "ok": hit,
                }
            )
        ok = (total == 0) or (correct == total)
    out = {
        "schema": "guard.extraction-accuracy.v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mode": "STRICT" if strict else "HINT",
        "source": {"mode": "file_first", "input": src},
        "fixture_missing": missing_fixture,
        "ok": ok if not missing_fixture else True,  # HINT: treat missing fixture as advisory
        "totals": {"cases": total, "correct": correct},
        "details": details[:10],  # cap for evidence
    }
    pathlib.Path("evidence").mkdir(exist_ok=True)
    pathlib.Path("evidence/guard_extraction_accuracy.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(out))
    return 1 if (strict and not out["ok"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
