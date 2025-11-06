#!/usr/bin/env python3
import json, re, sys
from pathlib import Path

HTML = re.compile(r"<[^>]+>")
FIELDS = ("definition", "gloss", "transliteration")


def main():
    if len(sys.argv) < 2:
        print("Usage: guard_analysis_no_html.py <nouns_json>", file=sys.stderr)
        sys.exit(2)
    p = Path(sys.argv[1])
    data = json.loads(p.read_text(encoding="utf-8"))
    bad = []
    for i, n in enumerate(data.get("nodes", [])):
        a = n.get("analysis", {}) or {}
        for f in FIELDS:
            v = a.get(f)
            if isinstance(v, str) and HTML.search(v or ""):
                bad.append((i, f, v[:120]))
    if bad:
        print(f"ERROR: {len(bad)} analysis fields contain HTML tags:", file=sys.stderr)
        for i, (idx, f, sn) in enumerate(bad[:10], 1):
            print(f"  {i}. node[{idx}].analysis.{f} -> {sn!r}", file=sys.stderr)
        sys.exit(2)
    print("OK: no HTML tags in analysis fields.")


if __name__ == "__main__":
    main()
