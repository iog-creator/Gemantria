#!/usr/bin/env python3
import fnmatch
import json
import math
import pathlib
import re
import sys
import time
from typing import Any

import yaml  # type: ignore  # Requires PyYAML available in dev env; not wired into CI

# ---------- Thresholds substitution ----------
_THRESHOLDS_CACHE: dict[str, Any] | None = None
_THRESH_RE = re.compile(r"^\$\{thresholds:([A-Za-z0-9_.-]+)\}$")


def _load_thresholds() -> dict[str, Any]:
    global _THRESHOLDS_CACHE
    if _THRESHOLDS_CACHE is not None:
        return _THRESHOLDS_CACHE
    p = ROOT / "eval" / "thresholds.yml"
    data: dict[str, Any] = {}
    if p.exists() and yaml is not None:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    _THRESHOLDS_CACHE = data
    return data


def _th_get(path: str, default: Any = None) -> Any:
    cur: Any = _load_thresholds()
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def _subst_thresholds(value: Any) -> Any:
    """Recursively substitute ${thresholds:...} placeholders in task args."""
    if isinstance(value, str):
        m = _THRESH_RE.match(value)
        if m:
            v = _th_get(m.group(1))
            return v if v is not None else value
        return value
    if isinstance(value, dict):
        return {k: _subst_thresholds(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_subst_thresholds(v) for v in value]
    return value


def _prepare_args(raw: dict[str, Any]) -> dict[str, Any]:
    return _subst_thresholds(raw)  # type: ignore[no-any-return]


ROOT = pathlib.Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "eval" / "manifest.yml"
import os
DEFAULT_OUTDIR = ROOT / "share" / "eval"
ENV_OUTDIR = os.environ.get("EVAL_OUTDIR")
OUTDIR = (ROOT / ENV_OUTDIR) if ENV_OUTDIR else DEFAULT_OUTDIR
JSON_OUT = OUTDIR / "report.json"
MD_OUT = OUTDIR / "report.md"


def task_print(args: dict[str, Any]) -> dict[str, Any]:
    msg = str(args.get("message", ""))
    return {"status": "OK", "stdout": msg}


def task_verify_files(args: dict[str, Any]) -> dict[str, Any]:
    missing = []
    for p in args.get("must_exist", []):
        if not (ROOT / p).exists():
            missing.append(p)
    return {"status": "OK" if not missing else "FAIL", "missing": missing}


def task_grep(args: dict[str, Any]) -> dict[str, Any]:
    file = ROOT / args["file"]
    pats = [re.compile(p) for p in args.get("patterns", [])]
    if not file.exists():
        return {"status": "FAIL", "error": f"no such file: {file}"}
    text = file.read_text(encoding="utf-8", errors="ignore")
    misses = [p.pattern for p in pats if not p.search(text)]
    return {"status": "OK" if not misses else "FAIL", "misses": misses}


def task_ref_integrity(args: dict[str, Any]) -> dict[str, Any]:
    """Check reference integrity of exported graph data."""
    graph_file = ROOT / args.get("graph_file", "exports/graph_latest.json")
    if not graph_file.exists():
        return {"status": "FAIL", "error": f"graph file not found: {graph_file}"}

    try:
        with open(graph_file, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        return {"status": "FAIL", "error": f"failed to parse graph JSON: {exc}"}

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    # Check for self-loops
    self_loops = [e for e in edges if e.get("source") == e.get("target")]
    max_self_loops = args.get("max_self_loops", 0)
    if len(self_loops) > max_self_loops:
        return {
            "status": "FAIL",
            "error": f"too many self-loops: {len(self_loops)} > {max_self_loops}",
            "self_loops": len(self_loops),
        }

    # Check for duplicate edges
    edge_keys = [(e.get("source"), e.get("target")) for e in edges]
    unique_edges = set(edge_keys)
    duplicates = len(edge_keys) - len(unique_edges)
    max_duplicates = args.get("max_duplicate_edges", 0)
    if duplicates > max_duplicates:
        return {
            "status": "FAIL",
            "error": f"too many duplicate edges: {duplicates} > {max_duplicates}",
            "duplicate_edges": duplicates,
        }

    # Check concept coverage (concepts with relations)
    node_ids = {n.get("id") for n in nodes}
    connected_ids = set()
    for e in edges:
        connected_ids.add(e.get("source"))
        connected_ids.add(e.get("target"))

    orphaned = len(node_ids - connected_ids)
    max_orphaned = args.get("max_orphaned_concepts", 50)
    if orphaned > max_orphaned:
        return {
            "status": "FAIL",
            "error": f"too many orphaned concepts: {orphaned} > {max_orphaned}",
            "orphaned_concepts": orphaned,
        }

    # Check minimum coverage
    coverage = len(connected_ids) / len(node_ids) if node_ids else 0
    min_coverage = args.get("min_concept_coverage", 0.95)
    if coverage < min_coverage:
        return {
            "status": "FAIL",
            "error": f"concept coverage too low: {coverage:.3f} < {min_coverage}",
            "coverage": coverage,
        }

    return {
        "status": "OK",
        "nodes": len(nodes),
        "edges": len(edges),
        "self_loops": len(self_loops),
        "duplicate_edges": duplicates,
        "orphaned_concepts": orphaned,
        "coverage": coverage,
    }


def task_json_schema(args: dict[str, Any]) -> dict[str, Any]:
    """
    Lightweight, built-in graph export validator (no external deps).
    Validates a subset of the schema used by docs/SSOT/schemas/graph_export.schema.json:
      - top-level object has 'nodes' (array) and 'edges' (array)
      - node: {'id': str|int, ...}
      - edge: {'source': str|int, 'target': str|int, optional 'strength'/'rerank' in [0,1]}
    """
    def _is_id(v: Any) -> bool:
        return isinstance(v, (str, int))

    def _in_01(v: Any) -> bool:
        return isinstance(v, (int, float)) and 0.0 <= float(v) <= 1.0

    file = ROOT / args.get("file", "")
    schema_path = ROOT / args.get("schema", "")  # not parsed; presence only
    if not file.exists():
        return {"status": "FAIL", "error": f"no such file: {file}"}
    if not schema_path.exists():
        return {"status": "FAIL", "error": f"no such schema: {schema_path}"}

    try:
        with open(file, encoding="utf-8") as f:
            doc = json.load(f)
    except Exception as e:
        return {"status": "FAIL", "error": f"json parse error: {e}"}

    if not isinstance(doc, dict):
        return {"status": "FAIL", "error": "top-level must be object"}
    nodes = doc.get("nodes")
    edges = doc.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        return {"status": "FAIL", "error": "'nodes' and 'edges' must be arrays"}

    node_errs = []
    for i, n in enumerate(nodes):
        if not isinstance(n, dict):
            node_errs.append(f"nodes[{i}] not object")
            continue
        if "id" not in n or not _is_id(n["id"]):
            node_errs.append(f"nodes[{i}].id missing or invalid")

    edge_errs = []
    for i, e in enumerate(edges):
        if not isinstance(e, dict):
            edge_errs.append(f"edges[{i}] not object")
            continue
        if not _is_id(e.get("source")) or not _is_id(e.get("target")):
            edge_errs.append(f"edges[{i}].source/target invalid")
        if "strength" in e and not _in_01(e["strength"]):
            edge_errs.append(f"edges[{i}].strength out of [0,1]")
        if "rerank" in e and not _in_01(e["rerank"]):
            edge_errs.append(f"edges[{i}].rerank out of [0,1]")

    errs = node_errs + edge_errs
    return {"status": "OK"} if not errs else {"status": "FAIL", "errors": errs}


def task_json_shape(args: dict[str, Any]) -> dict[str, Any]:
    """Validate JSON file structure/shape against expected patterns."""
    file_path = ROOT / args["file"]
    expected_keys = set(args.get("required_keys", []))
    expected_types = args.get("key_types", {})

    if not file_path.exists():
        return {"status": "FAIL", "error": f"file not found: {file_path}"}

    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return {"status": "FAIL", "error": f"failed to parse JSON: {e}"}

    if not isinstance(data, dict):
        return {"status": "FAIL", "error": "expected top-level object"}

    # Check required keys
    missing_keys = expected_keys - set(data.keys())
    if missing_keys:
        return {"status": "FAIL", "error": f"missing required keys: {missing_keys}"}

    # Check key types
    type_errors = []
    for key, expected_type in expected_types.items():
        if key in data:
            actual_value = data[key]
            if expected_type == "array" and not isinstance(actual_value, list):
                type_errors.append(f"{key}: expected array, got {type(actual_value).__name__}")
            elif expected_type == "object" and not isinstance(actual_value, dict):
                type_errors.append(f"{key}: expected object, got {type(actual_value).__name__}")
            elif expected_type == "number" and not isinstance(actual_value, (int, float)):
                type_errors.append(f"{key}: expected number, got {type(actual_value).__name__}")
            elif expected_type == "string" and not isinstance(actual_value, str):
                type_errors.append(f"{key}: expected string, got {type(actual_value).__name__}")

    if type_errors:
        return {"status": "FAIL", "error": f"type validation errors: {type_errors}"}

    return {
        "status": "OK",
        "keys_found": len(data),
        "required_keys_present": len(expected_keys),
        "type_checks_passed": len(expected_types)
    }


def task_file_glob(args: dict[str, Any]) -> dict[str, Any]:
    """Ensure globs match at least one file, report missing patterns deterministically."""
    globs = args.get("globs", [])
    if not isinstance(globs, list) or not globs:
        return {"status": "FAIL", "error": "file_glob.globs must be a non-empty list"}

    matched: dict[str, list[str]] = {}
    missing: list[str] = []

    for pat in globs:
        found = []
        for p in ROOT.rglob("*"):
            if p.is_file():
                rel = str(p.relative_to(ROOT))
                if fnmatch.fnmatch(rel, pat):
                    found.append(rel)
        if found:
            matched[pat] = sorted(found)
        else:
            missing.append(pat)

    if missing:
        return {"status": "FAIL", "error": f"no files matched: {missing}", "matched": matched}
    return {"status": "OK", "matched": matched}


def _json_query_all(obj: Any, path: str) -> list[Any]:
    """
    Simple path evaluator to support patterns like:
      - "edges[*].strength"
      - "nodes[*].embedding_dim"
    Supports dotted keys and single-level '[*]' list expansion.
    """
    parts = path.split(".")
    cur: list[Any] = [obj]
    for part in parts:
        nxt: list[Any] = []
        if part.endswith("[*]"):
            key = part[:-3]
            for x in cur:
                if isinstance(x, dict) and key in x and isinstance(x[key], list):
                    nxt.extend(x[key])
        else:
            for x in cur:
                if isinstance(x, dict) and part in x:
                    nxt.append(x[part])
        cur = nxt
        if not cur:
            break
    # Flatten one level if still nested lists from '[*]'
    flat: list[Any] = []
    for v in cur:
        if isinstance(v, list):
            flat.extend(v)
        else:
            flat.append(v)
    return flat


def _op_frac_in_range(vals: list[Any], min_v: float, max_v: float, min_frac: float) -> tuple[bool, dict[str, Any]]:
    nums = [float(v) for v in vals if isinstance(v, (int, float))]
    if not nums:
        return False, {"reason": "no numeric values", "count": 0}
    within = [x for x in nums if min_v <= x <= max_v]
    frac = len(within) / len(nums)
    ok = frac >= min_frac
    return ok, {"count": len(nums), "within": len(within), "fraction": frac}


def _op_if_present_eq_all(vals: list[Any], value: Any) -> tuple[bool, dict[str, Any]]:
    present = [v for v in vals if v is not None]
    if not present:
        return True, {"present": 0, "note": "no values present → PASS"}
    all_eq = all(v == value for v in present)
    return all_eq, {"present": len(present), "expected": value}


def task_json_assert(args: dict[str, Any]) -> dict[str, Any]:
    """Validate JSON structure with various assertion operations."""
    p = args.get("file")
    if not p:
        return {"status": "FAIL", "error": "json_assert.file is required"}

    file_path = ROOT / p
    if not file_path.exists():
        return {"status": "FAIL", "error": f"file not found: {p}"}

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"status": "FAIL", "error": f"json parse error: {e}"}

    asserts = args.get("asserts", [])
    if not isinstance(asserts, list) or not asserts:
        return {"status": "FAIL", "error": "json_assert.asserts must be a non-empty list"}

    results: list[dict[str, Any]] = []
    all_ok = True

    for a in asserts:
        name = a.get("name", "(unnamed)")
        path = a.get("path")
        op = a.get("op")
        vals = _json_query_all(data, path) if path else []

        ok = False
        detail: dict[str, Any] = {"path": path, "op": op}

        if op == "frac_in_range":
            min_v = float(a.get("min", float("-inf")))
            max_v = float(a.get("max", float("inf")))
            min_frac = float(a.get("min_frac", 1.0))
            ok, extra = _op_frac_in_range(vals, min_v, max_v, min_frac)
            detail.update(extra)
        elif op == "if_present_eq_all":
            ok, extra = _op_if_present_eq_all(vals, a.get("value"))
            detail.update(extra)
        else:
            detail["error"] = f"unknown op: {op}"

        results.append({"name": name, "ok": ok, "detail": detail})
        all_ok = all_ok and ok

    return {"status": "OK" if all_ok else "FAIL", "results": results}


KIND_IMPL = {
    "print": task_print,
    "verify_files": task_verify_files,
    "grep": task_grep,
    "ref_integrity": task_ref_integrity,
    "json_shape": task_json_shape,
    "json_schema": task_json_schema,
    "file_glob": task_file_glob,
    "json_assert": task_json_assert,
}


def load_manifest() -> dict[str, Any]:
    with open(MANIFEST, encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}


def main() -> int:
    print("[eval.report] starting")
    if not MANIFEST.exists():
        print(f"[eval.report] FAIL no manifest at {MANIFEST}")
        return 2
    OUTDIR.mkdir(parents=True, exist_ok=True)

    m = load_manifest()
    results = []
    all_ok = True
    for t in m.get("tasks", []):
        key = t["key"]
        kind = t["kind"]
        args = t.get("args", {})
        # Substitute ${thresholds:...} placeholders before running the task
        try:
            args = _prepare_args(args)
        except Exception as e:
            results.append(
                {
                    "key": key,
                    "kind": kind,
                    "status": "FAIL",
                    "error": f"thresholds substitution error: {e}",
                }
            )
            all_ok = False
            continue
        impl = KIND_IMPL.get(kind)
        if not impl:
            results.append(
                {"key": key, "kind": kind, "status": "FAIL", "error": "unknown kind"}
            )
            all_ok = False
            continue
        r = impl(args)
        status = r.get("status", "FAIL")
        if status != "OK":
            all_ok = False
        results.append({"key": key, "kind": kind, **r})

    report = {
        "version": m.get("version", "0"),
        "run_id": m.get("run_id", f"run-{int(time.time())}"),
        "ts_unix": int(time.time()),
        "summary": {
            "task_count": len(results),
            "ok_count": sum(1 for r in results if r.get("status") == "OK"),
            "fail_count": sum(1 for r in results if r.get("status") != "OK"),
        },
        "results": results,
    }
    JSON_OUT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    lines = []
    lines.append("# Gemantria Eval Report")
    lines.append("")
    summary = report["summary"]
    run_id_part = f"*run_id:* `{report['run_id']}`"
    stats_part = f"  •  *tasks:* {summary['task_count']}  •  *ok:* {summary['ok_count']}  •  *fail:* {summary['fail_count']}"  # noqa: E501
    lines.append(run_id_part + stats_part)
    lines.append("")
    for r in results:
        status = r.get("status")
        badge = "✅" if status == "OK" else "❌"
        lines.append(f"## {badge} {r['key']} ({r['kind']})")
        payload = {k: v for k, v in r.items() if k not in ("key", "kind", "status")}
        if payload:
            lines.append("```json")
            lines.append(json.dumps(payload, indent=2, sort_keys=True))
            lines.append("```")
        lines.append("")
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")

    print(f"[eval.report] wrote {JSON_OUT.relative_to(ROOT)}")
    print(f"[eval.report] wrote {MD_OUT.relative_to(ROOT)}")
    print("[eval.report] OK" if all_ok else "[eval.report] DONE_WITH_FAILS")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
