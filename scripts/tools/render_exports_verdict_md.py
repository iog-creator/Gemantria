#!/usr/bin/env python3

from __future__ import annotations

import json, sys, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parents[2]
VERDICT = ROOT / "evidence" / "exports_guard.verdict.json"
OUT = ROOT / "evidence" / "exports_guard.verdict.md"

def tick(b: bool) -> str: return "✅" if b else "❌"

def main():
    if not VERDICT.exists():
        print("no verdict at evidence/exports_guard.verdict.json", file=sys.stderr)
        return 1
    v = json.loads(VERDICT.read_text())
    ok = bool(v.get("ok"))
    strict = bool(v.get("strict"))
    gen = v.get("generated_at")
    files = v.get("files", {})

    # Header line
    title = f"### Exports JSON {'✅ PASS' if ok else '❌ FAIL'} {'(STRICT)' if strict else '(HINT)'}"
    lines = [title, ""]

    lines.append(f"- Generated: `{gen}`")
    lines.append(f"- Mode: `{'STRICT' if strict else 'HINT'}`")
    lines.append("")

    lines.append("| File | Exists | JSON | Schema |")
    lines.append("|---|:---:|:---:|:---:|")
    for name in sorted(files.keys()):
        f = files[name] or {}
        lines.append(f"| `{name}` | {tick(f.get('exists', False))} | {tick(f.get('json_ok', False))} | {tick(f.get('schema_ok', False))} |")
    lines.append("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"WROTE {OUT}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
