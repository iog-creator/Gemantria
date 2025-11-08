# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
REPORT_JSON = ROOT / "share" / "eval" / "report.json"


def main() -> int:
    print("[eval.gate.strict] starting")

    # Run strict profile evaluation directly (ignore make return code)
    subprocess.run(
        ["python3", "scripts/eval/run_with_profile.py", "strict"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    # Check if report was created (evaluation might succeed even with failures)
    if not REPORT_JSON.exists():
        print("[eval.gate.strict] FAIL: no report.json found after strict evaluation")
        return 2

    report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
    summary = report.get("summary", {})
    fail_count = summary.get("fail_count", 0)

    if fail_count > 0:
        allow_fail = os.getenv("ALLOW_FAIL", "0") == "1"
        if allow_fail:
            print(f"[eval.gate.strict] WARN: {fail_count} failures detected but ALLOW_FAIL=1")
            print("[eval.gate.strict] OK (override)")
            return 0
        else:
            print(f"[eval.gate.strict] FAIL: {fail_count} failures detected in strict profile")
            return 1

    print("[eval.gate.strict] OK: no failures in strict profile")
    return 0


if __name__ == "__main__":
    sys.exit(main())
