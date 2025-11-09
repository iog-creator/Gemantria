#!/usr/bin/env python3

from __future__ import annotations

import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

VERDICT = ROOT / "evidence" / "exports_rfc3339.verdict.json"

OUT = ROOT / "evidence" / "exports_rfc3339.verdict.md"

def tick(x: bool) -> str: return "✅" if x else "❌"

def main():

    if not VERDICT.exists():

        print("no verdict at evidence/exports_rfc3339.verdict.json", file=sys.stderr); return 1

    v = json.loads(VERDICT.read_text())

    ok = bool(v.get("ok")); strict = bool(v.get("strict")); gen = v.get("generated_at")

    files = v.get("files", {})

    lines = [f"### RFC3339 ✅ PASS (STRICT)" if ok and strict else

             f"### RFC3339 ✅ PASS (HINT)" if ok else

             f"### RFC3339 ❌ FAIL", ""]

    lines.append(f"- Generated: `{gen}`")

    lines.append(f"- Mode: `{'STRICT' if strict else 'HINT'}`")

    lines += ["", "| File | Exists | has generated_at | RFC3339 |",

              "|---|:---:|:---:|:---:|"]

    for name in sorted(files.keys()):

        f = files[name] or {}

        lines.append(f"| `{name}` | {tick(f.get('exists',False))} | {tick(f.get('has_generated_at',False))} | {tick(f.get('rfc3339_ok',False))} |")

    OUT.parent.mkdir(parents=True, exist_ok=True)

    OUT.write_text("\n".join(lines), encoding="utf-8")

    print(f"WROTE {OUT}")

if __name__ == "__main__": raise SystemExit(main())
