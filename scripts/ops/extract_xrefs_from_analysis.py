#!/usr/bin/env python3
"""Light cross-reference extractor from analysis text.

Scans the 'analysis' field of enriched nouns for Bible references
(e.g., "Genesis 1:1", "Gen 1:1", "1 John 4:8", "Ps 23:1") and
populates the 'xrefs[]' field with structured references.

Usage:
    python3 scripts/ops/extract_xrefs_from_analysis.py

Reads:  exports/ai_nouns.enriched.json
Writes: exports/ai_nouns.enriched.json (in-place update)
Output: JSON summary to stdout
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
from typing import Any

SRC = pathlib.Path("exports/ai_nouns.enriched.json")
OUT = SRC  # in-place update

# Very light matcher: e.g., "Genesis 1:1", "Gen 1:1", "1 John 4:8", "Ps 23:1"
REF_RE = re.compile(r"\b((?:[1-3]\s*)?[A-Za-z][A-Za-z]+)\s+(\d{1,3}):(\d{1,3})\b")


def _dedup(xrefs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deduplicate cross-references by (book, chapter, verse) tuple."""
    seen: set[tuple[str, int, int]] = set()
    out: list[dict[str, Any]] = []
    for xr in xrefs:
        key = (
            xr.get("book", "").strip(),
            int(xr.get("chapter", 0)),
            int(xr.get("verse", 0)),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(xr)
    return out


def main() -> int:
    """Extract cross-references from analysis text."""
    if not SRC.exists():
        print(json.dumps({"ok": True, "note": "export missing; skipping"}))
        return 0

    data = json.loads(SRC.read_text())
    nodes = data.get("nodes", [])
    total, touched, xref_added = len(nodes), 0, 0

    for nd in nodes:
        # Collect text from both analysis (if string) and insights fields
        texts = []
        analysis = nd.get("analysis")
        if isinstance(analysis, str):
            texts.append(analysis)

        insights = nd.get("insights")
        if isinstance(insights, str):
            texts.append(insights)

        if not texts:
            continue

        combined_text = " ".join(texts)

        found = []
        for m in REF_RE.finditer(combined_text):
            book = m.group(1).strip()
            ch = int(m.group(2))
            vs = int(m.group(3))
            found.append({"book": book, "chapter": ch, "verse": vs, "ref": f"{book} {ch}:{vs}"})

        if not found:
            continue

        # merge with any existing xrefs or legacy links
        xrefs = nd.get("xrefs") or nd.get("links") or []
        if not isinstance(xrefs, list):
            xrefs = []

        merged = _dedup(list(xrefs) + found)
        if len(merged) > len(xrefs):
            nd["xrefs"] = merged
            touched += 1
            xref_added += len(merged) - len(xrefs)

    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(
        json.dumps(
            {
                "ok": True,
                "file": str(SRC),
                "total_nodes": total,
                "nodes_with_new_xrefs": touched,
                "new_xrefs_added": xref_added,
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
