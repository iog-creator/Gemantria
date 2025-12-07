#!/usr/bin/env python
"""
guard_kernel_boot.py

Phase 26.5: Enforce kernel-first boot for OPS.

This script is intended to be called before any destructive OPS action.
It must:

* Call `pmagent handoff status-handoff --json`
* Fail non-zero if:
  * `ok` is false
  * `kernel` is missing or malformed
  * mode is DEGRADED and the caller requested non-remediation work

NOTE: This is a stub. Implement behavior according to:

* docs/SSOT/PHASE26_OPS_BOOT_SPEC.md
* docs/SSOT/ORCHESTRATOR_REALITY.md
* docs/SSOT/EXECUTION_CONTRACT.md (Section for kernel-aware preflight)
"""

import json
import subprocess
import sys


def main() -> int:
    try:
        result = subprocess.run(
            ["pmagent", "handoff", "status-handoff", "--json"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        print("guard_kernel_boot: pmagent not found on PATH", file=sys.stderr)
        return 1

    if result.returncode != 0:
        print("guard_kernel_boot: pmagent status-handoff failed", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        return result.returncode or 1

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("guard_kernel_boot: invalid JSON from status-handoff", file=sys.stderr)
        return 1

    ok = data.get("ok")
    kernel = data.get("kernel") or {}
    mode = data.get("mode") or data.get("health", {}).get("mode")

    if not ok:
        print("guard_kernel_boot: status-handoff returned ok=false", file=sys.stderr)
        return 1

    if not kernel.get("current_phase") or not kernel.get("branch"):
        print("guard_kernel_boot: kernel missing current_phase or branch", file=sys.stderr)
        return 1

    # NOTE: Mode semantics and remediation vs normal-work behavior are defined
    # in PHASE26_OPS_BOOT_SPEC.md. For now we only validate presence and ok=true.
    # Future work: add CLI flag to guard different operation types (remediation vs normal).
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
