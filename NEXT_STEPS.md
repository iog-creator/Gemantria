# NEXT_STEPS (author: GPT-5)

## Branch
feature/phase8-eval-report-001

## Tasks (Cursor executes these)

### 1) Add an eval manifest (docs-only data source)
- [ ] Create `eval/manifest.yml` with **exact** content:
```yaml
version: 0.1
run_id: local-dev
tasks:
  - key: smoke_hello
    kind: print
    args:
      message: "hello, gemantria"
  - key: gate_presence_rules
    kind: verify_files
    args:
      must_exist:
        - "AGENTS.md"
        - "Makefile"
        - ".github"
  - key: rule_names_sanity
    kind: grep
    args:
      file: "RULES_INDEX.md"
      patterns:
        - "037"
        - "038"
success_policy:
  mode: all_must_pass
```

### 2) Add a local-only report generator (no CI wiring)

* [ ] Create `scripts/eval/report.py` with **exact** content:

```python
#!/usr/bin/env python3
import json, sys, pathlib, time, re
from typing import Any, Dict, List
import yaml  # Requires PyYAML available in dev env; not wired into CI

ROOT = pathlib.Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "eval" / "manifest.yml"
OUTDIR = ROOT / "share" / "eval"
JSON_OUT = OUTDIR / "report.json"
MD_OUT = OUTDIR / "report.md"

def task_print(args: Dict[str, Any]) -> Dict[str, Any]:
    msg = str(args.get("message", ""))
    return {"status": "OK", "stdout": msg}

def task_verify_files(args: Dict[str, Any]) -> Dict[str, Any]:
    missing = []
    for p in args.get("must_exist", []):
        if not (ROOT / p).exists():
            missing.append(p)
    return {"status": "OK" if not missing else "FAIL", "missing": missing}

def task_grep(args: Dict[str, Any]) -> Dict[str, Any]:
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

def load_manifest() -> Dict[str, Any]:
    with open(MANIFEST, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

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
            results.append({"key": key, "kind": kind, "status": "FAIL", "error": "unknown kind"})
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
    lines.append(f"*run_id:* `{report['run_id']}`  •  *tasks:* {report['summary']['task_count']}  •  *ok:* {report['summary']['ok_count']}  •  *fail:* {report['summary']['fail_count']}")
    lines.append("")
    for r in results:
        status = r.get("status")
        badge = "✅" if status == "OK" else "❌"
        lines.append(f"## {badge} {r['key']} ({r['kind']})")
        payload = {k: v for k, v in r.items() if k not in ("key","kind","status")}
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
```

### 3) Makefile targets (local-only)

* [ ] Append the following to `Makefile` **without changing existing order or CI wiring**:

```
.PHONY: eval.report ci.eval.report

# Manifest-driven local report (writes to share/eval/)
eval.report:
	@python3 scripts/eval/report.py

# Not wired into CI; identical to local for now
ci.eval.report:
	@python3 scripts/eval/report.py
```

### 4) Share scaffold (tracked, minimal)

* [ ] Create `share/eval/.gitkeep` (empty file)

### 5) Docs

* [ ] Create `docs/PHASE8_EVAL.md` with **exact** content:

```md
# Phase-8 Eval (Local Manifest → Report)

Local-only evaluation flow. No CI gates or `make go` changes.

## Usage
1. Edit tasks in `eval/manifest.yml`
2. Run:
   ```bash
   make eval.report
```

3. Artifacts:

   * `share/eval/report.json`
   * `share/eval/report.md`

## Notes

* Deterministic and fast; suited for PR evidence.
* Do **not** wire into CI until stabilized.
* Governance: 037/038 unchanged; share drift remains read-only in CI.

```

- [ ] Append to **AGENTS.md** under "Operations → Evaluation":
```

* **Phase-8 manifest eval**: `make eval.report` loads `eval/manifest.yml` and emits `share/eval/report.{json,md}`. Keep this **local-only** until stabilized; no CI wiring and no `make go` edits.

```

### 6) Open PR
- [ ] Head: `feature/phase8-eval-report-001` → Base: `main`
- [ ] Title: `docs/eval: manifest-driven local report (no CI changes)`
- [ ] Body states:
  - Adds `eval/manifest.yml`, `scripts/eval/report.py`, `docs/PHASE8_EVAL.md`, Makefile targets, and `share/eval/.gitkeep`.
  - Produces deterministic `share/eval/report.json` + `.md`.
  - No CI/gate/order changes; local-only flow.

### 7) Evidence tails (paste in PR)
- [ ] Show Makefile target lines:
```bash
rg -n "eval\.report" Makefile
```

* [ ] Run report and show tails:

```bash
make eval.report
```

**Expected decisive lines:**

* `[eval.report] starting`
* `wrote share/eval/report.json`
* `wrote share/eval/report.md`
* `[eval.report] OK`
* [ ] Show JSON summary head:

```bash
jq -r '.summary | @json' share/eval/report.json
# expected contains: {"task_count":3,"ok_count":3,"fail_count":0}
```

* [ ] Prove Markdown header exists:

```bash
sed -n '1,5p' share/eval/report.md
# expected first line: "# Gemantria Eval Report"
```

### 8) Merge

* [ ] **Squash & Merge** with title:

```
docs/eval: manifest-driven local report (no CI changes)
```

## Acceptance checks (Cursor pastes under Evidence tails)

* `rg` tail shows `eval.report` targets present
* `make eval.report` tails show **OK** and both artifact paths
* JSON summary equals `task_count=3, ok_count=3, fail_count=0`
* Markdown first line is `# Gemantria Eval Report`
* PR merged with the exact title

## Status

* Cursor sets to **Done** when merged and evidence is pasted.