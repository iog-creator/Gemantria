#!/usr/bin/env python3
import sys, pathlib, json, time, shutil
from typing import Any, Dict

ROOT = pathlib.Path(__file__).resolve().parents[2]
BASE = ROOT / "eval" / "thresholds.yml"
PROFILES = ROOT / "eval" / "profiles"
REPORT = ROOT / "scripts" / "eval" / "report.py"

def _read_yaml(p: pathlib.Path) -> Dict[str, Any]:
    import yaml
    return yaml.safe_load(p.read_text(encoding="utf-8"))

def _deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out

def main() -> int:
    if len(sys.argv) != 2:
        print("[eval.profile] usage: run_with_profile.py <strict|dev>")
        return 2
    name = sys.argv[1]
    prof = PROFILES / f"{name}.yml"
    if not prof.exists():
        print(f"[eval.profile] FAIL no such profile: {prof}")
        return 2

    print(f"[eval.profile] starting profile={name}")
    base = _read_yaml(BASE)
    overlay = _read_yaml(prof)
    eff = _deep_merge(base, overlay)

    # write effective thresholds and temporarily swap thresholds.yml
    tmp = BASE.parent / "_thresholds.effective.yml"
    tmp.write_text(__import__("yaml").safe_dump(eff, sort_keys=True), encoding="utf-8")

    backup = BASE.read_text(encoding="utf-8")
    try:
        BASE.write_text(tmp.read_text(encoding="utf-8"), encoding="utf-8")
        # run report.py using subprocess
        import subprocess
        result = subprocess.run(["python3", str(REPORT)], cwd=ROOT)
        if result.returncode != 0:
            print(f"[eval.profile] report failed with code {result.returncode}")
            return result.returncode
    finally:
        BASE.write_text(backup, encoding="utf-8")
        tmp.unlink(missing_ok=True)

    print("[eval.profile] OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
