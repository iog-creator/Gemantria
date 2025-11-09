#!/usr/bin/env python3

from __future__ import annotations

import json, os, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXPORTS = ROOT / "exports"
TARGETS = [
    ("graph_latest.scored.json", None),  # schema optional
    ("ai_nouns.json", None),
    ("graph_stats.json", None),
    ("graph_patterns.json", None),
]


def is_tag_ctx() -> bool:
    return (
        os.getenv("GITHUB_REF_TYPE", "").lower() == "tag"
        or os.getenv("GITHUB_REF", "").startswith("refs/tags/")
        or os.getenv("STRICT_TAG_CONTEXT") == "1"
    )


def main() -> int:
    strict = is_tag_ctx() or os.getenv("STRICT_EXPORTS_JSON") == "1"
    errors = []
    hints = []
    for fname, _schema in TARGETS:
        f = EXPORTS / fname
        if not f.exists():
            msg = f"missing: exports/{fname}"
            (errors if strict else hints).append(msg)
            continue
        try:
            with f.open("r", encoding="utf-8") as fh:
                obj = json.load(fh)  # basic JSON validity
            # --- Minimal shape checks (dependency-free) ---
            if fname == "ai_nouns.json":
                if not isinstance(obj, dict) or "nodes" not in obj or not isinstance(obj["nodes"], list):
                    (errors if strict else hints).append("ai_nouns.json: expected object with list 'nodes'")
            elif fname == "graph_stats.json":
                if not isinstance(obj, dict) or not all(k in obj for k in ("nodes", "edges")):
                    (errors if strict else hints).append(
                        "graph_stats.json: expected object with numeric 'nodes' and 'edges'"
                    )
                else:
                    n, e = obj["nodes"], obj["edges"]
                    if not (isinstance(n, int) and n >= 0 and isinstance(e, int) and e >= 0):
                        (errors if strict else hints).append(
                            "graph_stats.json: 'nodes'/'edges' must be non-negative integers"
                        )
            elif fname == "graph_patterns.json":
                if not ((isinstance(obj, list)) or (isinstance(obj, dict) and isinstance(obj.get("patterns"), list))):
                    (errors if strict else hints).append("graph_patterns.json: expected list or object{patterns: list}")
            elif fname == "graph_latest.scored.json":
                if not isinstance(obj, dict):
                    (errors if strict else hints).append("graph_latest.scored.json: expected top-level object")
        except Exception as e:
            msg = f"invalid json: exports/{fname}: {e}"
            (errors if strict else hints).append(msg)
    for h in hints:
        print("HINT: exports.json:", h, file=sys.stderr)
    if errors:
        for e in errors:
            print("ERROR: exports.json:", e, file=sys.stderr)
        return 2
    print(json.dumps({"ok": True, "strict": strict, "checked": [t[0] for t in TARGETS]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
