#!/usr/bin/env python3
import json
import os
import pathlib
import subprocess
import time
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
REMEDIATION_PLAN = ROOT / "share" / "eval" / "remediation_plan.json"
REMEDIATION_LOG = ROOT / "share" / "eval" / "remediation_applied.json"


def _load_plan() -> dict[str, Any]:
    if not REMEDIATION_PLAN.exists():
        return {}
    data = json.loads(REMEDIATION_PLAN.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _run_command(cmd: str, description: str) -> dict[str, Any]:
    """Run a command and return structured result."""
    print(f"[eval.apply.remediation] executing: {description}")
    print(f"[eval.apply.remediation] command: {cmd}")

    try:
        # Use shell=True to support complex commands like "make go"
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        success = result.returncode == 0
        output = {
            "command": cmd,
            "description": description,
            "returncode": result.returncode,
            "success": success,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "timestamp": int(time.time()),
        }

        if success:
            print(f"[eval.apply.remediation] ✅ SUCCESS: {description}")
        else:
            print(f"[eval.apply.remediation] ❌ FAILED: {description}")
            if result.stderr:
                print(f"[eval.apply.remediation] stderr: {result.stderr.strip()}")

        return output

    except subprocess.TimeoutExpired:
        print(f"[eval.apply.remediation] ⏰ TIMEOUT: {description}")
        return {
            "command": cmd,
            "description": description,
            "returncode": -1,
            "success": False,
            "stdout": "",
            "stderr": "Command timed out after 300 seconds",
            "timestamp": int(time.time()),
        }
    except Exception as e:
        print(f"[eval.apply.remediation] 💥 ERROR: {description} - {e}")
        return {
            "command": cmd,
            "description": description,
            "returncode": -1,
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "timestamp": int(time.time()),
        }


def _apply_automated_fixes(plan: dict[str, Any]) -> list[dict[str, Any]]:
    """Apply all automated fixes from the remediation plan."""
    remediations = plan.get("remediations", [])
    automated_fixes = [
        r for r in remediations if r.get("automated_fix_available", False)
    ]

    applied_fixes = []

    for fix in automated_fixes:
        task_key = fix["task_key"]
        fix_command = fix["fix_command"]
        description = f"Auto-fix for {task_key}: {fix['issue'][:50]}..."

        result = _run_command(fix_command, description)
        result["task_key"] = task_key
        result["fix_type"] = "automated"
        result["severity"] = fix.get("severity", "unknown")
        result["category"] = fix.get("category", "unknown")

        applied_fixes.append(result)

        # If this was a pipeline regeneration, wait a moment for files to settle
        if "make go" in fix_command:
            print("[eval.apply.remediation] waiting for pipeline completion...")
            time.sleep(5)

    return applied_fixes


def _validate_fixes(applied_fixes: list[dict[str, Any]]) -> dict[str, Any]:
    """Run evaluation again to validate that fixes worked."""
    print("[eval.apply.remediation] validating fixes with re-evaluation...")

    # Re-run the evaluation
    result = _run_command("make eval.report", "Re-evaluate after applying fixes")

    # Load the new report if it was generated successfully
    validation = {
        "validation_attempted": True,
        "validation_success": result["success"],
        "validation_command": result["command"],
        "validation_timestamp": int(time.time()),
    }

    if result["success"]:
        try:
            # Load the updated report
            if (ROOT / "share" / "eval" / "report.json").exists():
                new_report = json.loads(
                    (ROOT / "share" / "eval" / "report.json").read_text(
                        encoding="utf-8"
                    )
                )
                summary = new_report.get("summary", {})
                validation.update(
                    {
                        "post_fix_ok_count": summary.get("ok_count", 0),
                        "post_fix_fail_count": summary.get("fail_count", 0),
                        "improvement": True,  # We'll compare with original in the summary
                    }
                )
        except Exception as e:
            validation["validation_error"] = str(e)

    return validation


def main() -> int:
    print("[eval.apply.remediation] starting")

    if not REMEDIATION_PLAN.exists():
        print(
            "[eval.apply.remediation] FAIL no remediation_plan.json found (run make eval.remediation first)"
        )
        return 2

    plan = _load_plan()
    if not plan:
        print("[eval.apply.remediation] FAIL could not load remediation plan")
        return 2

    # Check if user wants to skip automated fixes
    skip_auto = os.getenv("SKIP_AUTO_FIXES", "0") == "1"
    if skip_auto:
        print("[eval.apply.remediation] SKIP_AUTO_FIXES=1, skipping automated fixes")
        applied_fixes = []
    else:
        # Apply automated fixes
        applied_fixes = _apply_automated_fixes(plan)

    # Validate fixes (if any were applied)
    validation = {}
    if applied_fixes:
        validation = _validate_fixes(applied_fixes)
    else:
        validation = {
            "validation_attempted": False,
            "validation_success": True,
            "note": "No automated fixes were applied",
        }

    # Generate summary
    successful_fixes = [f for f in applied_fixes if f["success"]]
    failed_fixes = [f for f in applied_fixes if not f["success"]]

    summary = {
        "applied_at": int(time.time()),
        "total_fixes_attempted": len(applied_fixes),
        "successful_fixes": len(successful_fixes),
        "failed_fixes": len(failed_fixes),
        "validation": validation,
        "applied_fixes": applied_fixes,
    }

    # Add improvement metrics if validation worked
    original_plan = plan
    if validation.get("validation_success") and "post_fix_ok_count" in validation:
        orig_ok = original_plan.get("based_on_report", {}).get("ok_count", 0)
        orig_fail = original_plan.get("based_on_report", {}).get("fail_count", 0)
        new_ok = validation.get("post_fix_ok_count", 0)
        new_fail = validation.get("post_fix_fail_count", 0)

        summary["improvement"] = {
            "original_ok": orig_ok,
            "original_fail": orig_fail,
            "new_ok": new_ok,
            "new_fail": new_fail,
            "ok_improvement": new_ok - orig_ok,
            "fail_reduction": orig_fail - new_fail,
        }

    # Write log
    REMEDIATION_LOG.write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )

    print(f"[eval.apply.remediation] applied {len(applied_fixes)} fixes")
    print(
        f"[eval.apply.remediation] {len(successful_fixes)} successful, {len(failed_fixes)} failed"
    )
    print(f"[eval.apply.remediation] wrote {REMEDIATION_LOG.relative_to(ROOT)}")

    if failed_fixes:
        print(
            "[eval.apply.remediation] WARNING: Some fixes failed - check log for details"
        )
        return 1

    print("[eval.apply.remediation] OK")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
