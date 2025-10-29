#!/usr/bin/env python3
import json
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


KIND_IMPL = {
    "print": task_print,
    "verify_files": task_verify_files,
    "grep": task_grep,
    "ref_integrity": task_ref_integrity,
    "json_shape": task_json_shape,
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
