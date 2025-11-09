#!/usr/bin/env python3

from __future__ import annotations

import json, os, sys, pathlib, datetime
from jsonschema_min import validate as _validate_schema

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXPORTS = ROOT / "exports"
VERDICT_PATH = ROOT / "evidence" / "exports_guard.verdict.json"
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
    verdict = {
        "schema": "guard.exports-json.v1",
        "generated_at": datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "strict": bool(strict),
        "files": {},
        "ok": False,
    }
    for fname, schema_name in TARGETS:
        f = EXPORTS / fname
        checked.append(fname)
        exists = f.exists()
        json_ok = False
        schema_ok = False
        err = None
        if not exists:
            err = "missing"
            msg = f"missing: exports/{fname}"
            (errors if strict else hints).append(msg)
            verdict["files"][fname] = {
                "exists": False,
                "json_ok": False,
                "schema_ok": False,
                "error": err,
            }
            continue
        try:
            with f.open("r", encoding="utf-8") as fh:
                obj = json.load(fh)  # basic JSON validity
            json_ok = True
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
                            schema_ok = True
                    except Exception as e:
                        (errors if strict else hints).append(f"schema: {schema_name} invalid or unreadable: {e}")
        except Exception as e:
            msg = f"invalid json: exports/{fname}: {e}"
            err = f"json:{type(e).__name__}"
            (errors if strict else hints).append(msg)

        verdict["files"][fname] = {
            "exists": bool(exists),
            "json_ok": bool(json_ok),
            "schema_ok": bool(schema_ok),
            "error": err,
        }
    verdict["ok"] = len(errors) == 0

    for h in hints:
        print("HINT: exports.json:", h, file=sys.stderr)
    if errors:
        for e in errors:
            print("ERROR: exports.json:", e, file=sys.stderr)
        # Write verdict with final status before exit
        VERDICT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with VERDICT_PATH.open("w", encoding="utf-8") as fh:
            json.dump(verdict, fh, ensure_ascii=False, separators=(",", ":"))
        print(f"HINT: exports_json: wrote verdict → {VERDICT_PATH}", file=sys.stderr)
        return 2

    # No errors: write verdict and continue
    VERDICT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with VERDICT_PATH.open("w", encoding="utf-8") as fh:
        json.dump(verdict, fh, ensure_ascii=False, separators=(",", ":"))
    print(f"HINT: exports_json: wrote verdict → {VERDICT_PATH}", file=sys.stderr)

    # Preserve compact HINT-mode console object (unchanged shape for callers)
    print(
        json.dumps(
            {
                "ok": verdict["ok"],
                "strict": strict,
                "checked": checked,
                "schema_checks": {"passed": schema_pass, "failed": schema_fail},
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
