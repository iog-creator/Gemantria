#!/usr/bin/env python3
import json, sys
from pathlib import Path


def main():
    if len(sys.argv) < 3:
        print("Usage: guard_book_scope.py <nouns_json> <osis_prefix>", file=sys.stderr)
        sys.exit(2)
    p = Path(sys.argv[1])
    prefix = sys.argv[2]
    if not p.exists():
        print(f"FAIL: file not found: {p}", file=sys.stderr)
        sys.exit(2)
    env = json.loads(p.read_text(encoding="utf-8"))
    nodes = env.get("nodes", [])
    bad = [n for n in nodes if not any(s.get("ref", "").startswith(prefix) for s in n.get("sources", []))]
    if bad:
        print(f"FAIL: {len(bad)} nodes outside {prefix}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: {len(nodes)} nodes within scope {prefix}")


if __name__ == "__main__":
    main()
