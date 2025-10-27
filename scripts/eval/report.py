#!/usr/bin/env python3
import glob
import json
import pathlib
import re
import sys
import time
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "eval" / "manifest.yml"
THRESHOLDS = ROOT / "eval" / "thresholds.yml"
OUTDIR = ROOT / "share" / "eval"
JSON_OUT = OUTDIR / "report.json"
MD_OUT = OUTDIR / "report.md"


def _read_yaml(path: pathlib.Path) -> Any:
    try:
        import yaml  # type: ignore  # noqa: E402

        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise RuntimeError(
            "PyYAML is required for eval.report. Please `pip install pyyaml`."
        ) from e


def _load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_all(doc: Any, path: str) -> list[Any]:
    parts = path.split(".") if path else []
    cur = [doc]
    for seg in parts:
        arr = seg.endswith("[*]")
        key = seg[:-3] if arr else seg
        nxt = []
        for node in cur:
            if isinstance(node, dict) and key in node:
                val = node[key]
                if arr and isinstance(val, list):
                    nxt.extend(val)
                else:
                    nxt.append(val)
        cur = nxt
    return cur


# ---------- thresholds substitution ----------
def _lookup_threshold(k: str, t: dict[str, Any]) -> Any:
    p = k.split(".")
    cur: Any = t
    for seg in p:
        if isinstance(cur, dict) and seg in cur:
            cur = cur[seg]
        else:
            raise KeyError(f"thresholds path not found: {k}")
    return cur


def _resolve_thresholds(obj: Any, t: dict[str, Any]) -> Any:
    # resolves strings of the form "${thresholds:foo.bar.baz}"
    if isinstance(obj, str):
        m = re.fullmatch(r"\$\{thresholds:([A-Za-z0-9_.]+)\}", obj.strip())
        if m:
            return _lookup_threshold(m.group(1), t)
    if isinstance(obj, list):
        return [_resolve_thresholds(x, t) for x in obj]
    if isinstance(obj, dict):
        return {k: _resolve_thresholds(v, t) for k, v in obj.items()}
    return obj


def _load_whitelist(path: str) -> set[Any]:
    ids: set[Any] = set()
    if path:
        p = ROOT / path
        if p.exists():
            for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    # keep raw token; ids may be strings or integers; we store both
                    try:
                        ids.add(int(line))
                    except Exception:
                        ids.add(line)
    return ids


# ---------- Task impls ----------
def task_print(args: dict[str, Any]) -> dict[str, Any]:
    msg = str(args.get("message", ""))
    return {"status": "OK", "stdout": msg}


def task_grep(args: dict[str, Any]) -> dict[str, Any]:
    file = ROOT / args["file"]
    pats = [re.compile(p) for p in args.get("patterns", [])]
    if not file.exists():
        return {"status": "FAIL", "error": f"no such file: {file}"}
    text = file.read_text(encoding="utf-8", errors="ignore")
    misses = [p.pattern for p in pats if not p.search(text)]
    return {"status": "OK" if not misses else "FAIL", "misses": misses}


def task_file_glob(args: dict[str, Any]) -> dict[str, Any]:
    globspecs = args.get("globs", [])
    missing = []
    for g in globspecs:
        matches = glob.glob(str(ROOT / g))
        if not matches:
            missing.append(g)
    return {"status": "OK" if not missing else "FAIL", "missing": missing}


def _assert_not_null_all(vals: list[Any]) -> dict[str, Any]:
    bad = [i for i, v in enumerate(vals) if v is None]
    return {"status": "OK" if not bad else "FAIL", "null_indices": bad}


def _assert_frac_in_range(
    vals: list[Any], lo: float, hi: float, min_frac: float
) -> dict[str, Any]:
    nums = [v for v in vals if isinstance(v, int | float)]
    if not nums:
        return {"status": "FAIL", "error": "no numeric values"}
    ok = [v for v in nums if lo <= float(v) <= hi]
    frac = len(ok) / max(1, len(nums))
    res = {
        "observed_frac": round(frac, 4),
        "n": len(nums),
        "ok_n": len(ok),
        "range": [lo, hi],
        "min_frac": min_frac,
    }
    res["status"] = "OK" if frac >= min_frac else "FAIL"
    return res


def _assert_if_present_eq_all(vals: list[Any], value: Any) -> dict[str, Any]:
    present = [v for v in vals if v is not None]
    bad = [i for i, v in enumerate(present) if v != value]
    return {
        "status": "OK" if not bad else "FAIL",
        "present_n": len(present),
        "bad_indices": bad,
        "expected": value,
    }


def task_json_assert(args: dict[str, Any]) -> dict[str, Any]:
    file = ROOT / args["file"]
    if not file.exists():
        return {"status": "FAIL", "error": f"no such file: {file}"}
    doc = _load_json(file)
    checks = []
    all_ok = True
    for a in args.get("asserts", []):
        name = a.get("name", "assert")
        path = a["path"]
        vals = _extract_all(doc, path)
        op = a["op"]
        detail = {"name": name, "path": path, "op": op}
        if op == "not_null_all":
            r = _assert_not_null_all(vals)
        elif op == "frac_in_range":
            r = _assert_frac_in_range(
                vals, float(a["min"]), float(a["max"]), float(a["min_frac"])
            )
        elif op == "if_present_eq_all":
            r = _assert_if_present_eq_all(vals, a.get("value"))
        else:
            r = {"status": "FAIL", "error": f"unknown op: {op}"}
        status = r.get("status", "FAIL")
        if status != "OK":
            all_ok = False
        checks.append({**detail, **r})
    return {"status": "OK" if all_ok else "FAIL", "checks": checks}


def task_json_schema(args: dict[str, Any]) -> dict[str, Any]:
    try:
        import jsonschema  # type: ignore  # noqa: E402
    except Exception:
        return {
            "status": "FAIL",
            "error": "jsonschema not installed; run `pip install jsonschema`",
        }
    file = ROOT / args["file"]
    schema = ROOT / args["schema"]
    if not file.exists():
        return {"status": "FAIL", "error": f"no such file: {file}"}
    if not schema.exists():
        return {"status": "FAIL", "error": f"no such schema: {schema}"}
    doc = _load_json(file)
    sch = _load_json(schema)
    try:
        jsonschema.validate(instance=doc, schema=sch)
        return {"status": "OK"}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}


def task_json_shape(args: dict[str, Any]) -> dict[str, Any]:
    file = ROOT / args["file"]
    if not file.exists():
        return {"status": "FAIL", "error": f"no such file: {file}"}
    doc = _load_json(file)
    nodes = doc.get("nodes", [])
    edges = doc.get("edges", [])
    n_nodes = len(nodes) if isinstance(nodes, list) else 0
    n_edges = len(edges) if isinstance(edges, list) else 0
    mn = int(args.get("min_nodes", 0))
    mxn = int(args.get("max_nodes", 2**31 - 1))
    me = int(args.get("min_edges", 0))
    mxe = int(args.get("max_edges", 2**31 - 1))
    ok_nodes = mn <= n_nodes <= mxn
    ok_edges = me <= n_edges <= mxe
    status = "OK" if (ok_nodes and ok_edges) else "FAIL"
    return {
        "status": status,
        "nodes": n_nodes,
        "edges": n_edges,
        "limits": {"nodes": [mn, mxn], "edges": [me, mxe]},
    }


def task_ref_integrity(args: dict[str, Any]) -> dict[str, Any]:
    file = ROOT / args["file"]
    if not file.exists():
        return {"status": "FAIL", "error": f"no such file: {file}"}
    doc = _load_json(file)
    nodes = doc.get("nodes", [])
    edges = doc.get("edges", [])
    node_ids: list[Any] = []
    if isinstance(nodes, list):
        for n in nodes:
            if isinstance(n, dict) and "id" in n:
                node_ids.append(n.get("id"))
    node_set = set(node_ids)
    dup_node_ids = len(node_ids) - len(node_set)

    wl = _load_whitelist(args.get("whitelist_path", ""))

    def _ekey(e: dict[str, Any]) -> tuple[Any, Any]:
        return (e.get("source"), e.get("target"))

    missing_endpoints = 0
    self_loops = 0
    edge_pairs: list[tuple[Any, Any]] = []
    if isinstance(edges, list):
        for e in edges:
            if not isinstance(e, dict):
                continue
            s, t = e.get("source"), e.get("target")
            if s in wl or t in wl:
                edge_pairs.append(_ekey(e))
                continue  # ignore whitelist edges for counting violations
            if s == t:
                self_loops += 1
            if (s not in node_set) or (t not in node_set):
                missing_endpoints += 1
            edge_pairs.append(_ekey(e))
    dup_edge_pairs = len(edge_pairs) - len(set(edge_pairs))

    # thresholds (already substituted if using ${thresholds:...})
    allow_missing_endpoints = int(args.get("allow_missing_endpoints", 0))
    max_self_loops = int(args.get("max_self_loops", 0))
    max_dup_nodes = int(args.get("max_duplicate_node_ids", 0))
    max_dup_edges = int(args.get("max_duplicate_edge_pairs", 0))

    status = "OK"
    if (
        missing_endpoints > allow_missing_endpoints
        or self_loops > max_self_loops
        or dup_node_ids > max_dup_nodes
        or dup_edge_pairs > max_dup_edges
    ):
        status = "FAIL"

    return {
        "status": status,
        "counts": {
            "missing_endpoints": missing_endpoints,
            "self_loops": self_loops,
            "duplicate_node_ids": dup_node_ids,
            "duplicate_edge_pairs": dup_edge_pairs,
        },
        "limits": {
            "allow_missing_endpoints": allow_missing_endpoints,
            "max_self_loops": max_self_loops,
            "max_duplicate_node_ids": max_dup_nodes,
            "max_duplicate_edge_pairs": max_dup_edges,
        },
    }


def task_id_type_audit(args: dict[str, Any]) -> dict[str, Any]:
    file = ROOT / args["file"]
    if not file.exists():
        return {"status": "FAIL", "error": f"no such file: {file}"}
    doc = _load_json(file)
    nodes = doc.get("nodes", [])
    wl = _load_whitelist(args.get("whitelist_path", ""))
    ids: list[Any] = []
    if isinstance(nodes, list):
        for n in nodes:
            if isinstance(n, dict) and "id" in n:
                nid = n.get("id")
                if nid in wl:
                    continue
                ids.append(nid)

    def _type_name(v: Any) -> str:
        if isinstance(v, bool):  # keep bool separate from integer semantic confusion
            return "boolean"
        if isinstance(v, int):
            return "integer"
        if isinstance(v, float):
            return "number"
        if isinstance(v, str):
            return "string"
        if v is None:
            return "null"
        return "other"

    types = [_type_name(v) for v in ids]
    from collections import Counter  # noqa: E402

    counts = Counter(types)

    allowed: list[str] = list(args.get("allowed_node_id_types", []))
    require_single = int(args.get("require_single_id_type", 0)) == 1
    max_nonconf = int(args.get("max_nonconforming_ids", 0))

    # Nonconforming = ids whose type not in allowed
    nonconf = sum(1 for t in types if t not in allowed)

    # If require_single, then among allowed types used by any id, must be exactly one unique
    used_allowed = sorted(set(t for t in types if t in allowed))
    single_ok = (len(used_allowed) == 1) if require_single else True

    status = "OK"
    if nonconf > max_nonconf or not single_ok:
        status = "FAIL"

    return {
        "status": status,
        "id_count": len(ids),
        "type_counts": dict(counts),
        "allowed_types": allowed,
        "require_single": require_single,
        "max_nonconforming_ids": max_nonconf,
        "observed_allowed_used": used_allowed,
        "nonconforming_ids": nonconf,
    }


KIND_IMPL = {
    "print": task_print,
    "grep": task_grep,
    "file_glob": task_file_glob,
    "json_assert": task_json_assert,
    "json_schema": task_json_schema,
    "json_shape": task_json_shape,
    "ref_integrity": task_ref_integrity,
    "id_type_audit": task_id_type_audit,
}


# ---------- Driver ----------
def main() -> int:
    print("[eval.report] starting")
    if not MANIFEST.exists():
        print(f"[eval.report] FAIL no manifest at {MANIFEST}")
        return 2
    OUTDIR.mkdir(parents=True, exist_ok=True)

    m = _read_yaml(MANIFEST)
    t = _read_yaml(THRESHOLDS) if THRESHOLDS.exists() else {}
    m = _resolve_thresholds(m, t)  # substitute ${thresholds:...}

    results = []
    all_ok = True
    for tsk in m.get("tasks", []):
        key = tsk["key"]
        kind = tsk["kind"]
        args = tsk.get("args", {})
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
    lines.append(
        f"*run_id:* `{report['run_id']}`  •  "
        f"*tasks:* {report['summary']['task_count']}  •  "
        f"*ok:* {report['summary']['ok_count']}  •  "
        f"*fail:* {report['summary']['fail_count']}"
    )
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
