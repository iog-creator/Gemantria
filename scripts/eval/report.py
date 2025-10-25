#!/usr/bin/env python3
import json
import pathlib
import re
import sys
import time
from typing import Any

import yaml  # type: ignore  # Requires PyYAML available in dev env; not wired into CI

ROOT = pathlib.Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "eval" / "manifest.yml"
OUTDIR = ROOT / "share" / "eval"
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


KIND_IMPL = {
    "print": task_print,
    "verify_files": task_verify_files,
    "grep": task_grep,
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
