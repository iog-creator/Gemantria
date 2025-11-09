#!/usr/bin/env python3

from __future__ import annotations

import json, os, sys, pathlib
from jsonschema_min import validate as _validate_schema

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXPORTS = ROOT / "exports"
TARGETS = [
    ("graph_latest.scored.json", "graph.schema.json"),
    ("ai_nouns.json", "ai-nouns.schema.json"),
    ("graph_stats.json", "graph-stats.schema.json"),
    ("graph_patterns.json", "graph-patterns.schema.json"),
]


def is_tag_ctx() -> bool:
    return (
        os.getenv("GITHUB_REF_TYPE", "").lower() == "tag"
        or os.getenv("GITHUB_REF", "").startswith("refs/tags/")
        or os.getenv("STRICT_TAG_CONTEXT") == "1"
    )


def _find_schema_path(fname: str) -> pathlib.Path | None:
    # Search common locations for the schema file by name
    candidates = [
        ROOT / fname,
        ROOT / "schemas" / fname,
        ROOT / "spec" / fname,
        ROOT / "docs" / "schemas" / fname,
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def main() -> int:
    strict = is_tag_ctx() or os.getenv("STRICT_EXPORTS_JSON") == "1"
    errors = []
    hints = []
    schema_pass = 0
    schema_fail = 0
    checked = []
    for fname, schema_name in TARGETS:
        f = EXPORTS / fname
        checked.append(fname)
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
            # --- JSON Schema validation (if schema file found) ---
            if schema_name:
                sp = _find_schema_path(schema_name)
                if sp is None:
                    hints.append(f"schema: {schema_name} not found (skipping)")
                else:
                    try:
                        sch = json.loads(sp.read_text())
                        verrs = _validate_schema(obj, sch)
                        if verrs:
                            schema_fail += 1
                            msg = f"schema: {fname} does not match {schema_name}: " + "; ".join(verrs[:5])
                            (errors if strict else hints).append(msg)
                        else:
                            schema_pass += 1
                    except Exception as e:
                        (errors if strict else hints).append(f"schema: {schema_name} invalid or unreadable: {e}")
        except Exception as e:
            msg = f"invalid json: exports/{fname}: {e}"
            (errors if strict else hints).append(msg)
    for h in hints:
        print("HINT: exports.json:", h, file=sys.stderr)
    if errors:
        for e in errors:
            print("ERROR: exports.json:", e, file=sys.stderr)
        return 2
    print(json.dumps({"ok": True, "strict": strict, "checked": checked, "schema_checks":{"passed": schema_pass, "failed": schema_fail}}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
