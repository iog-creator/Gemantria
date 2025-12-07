#!/usr/bin/env python
"""
guard_github_state.py

Phase 26.5 — GitHub reality check (design-level guard).

Purpose:
Make it harder for agents to "forget" GitHub when planning work.

Behavior (non-destructive):
- Prints branch, tracking info, and a simple phase↔branch sanity check.
- Exits 0 in all cases for now (Phase 27 can tighten this to fail-closed).

Future versions (Phase 27+):
- Compare PM_KERNEL.json.current_phase against branch naming.
- Exit non-zero on obvious phase/branch mismatch.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> str:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        return out.decode().strip()
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"[guard_github_state] Command failed: {' '.join(cmd)}\n")
        sys.stderr.write(e.output.decode())
        return ""


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]

    try:
        branch = run(["git", "-C", str(repo_root), "rev-parse", "--abbrev-ref", "HEAD"])
        status = run(["git", "-C", str(repo_root), "status", "-sb"])
        branches = run(["git", "-C", str(repo_root), "branch", "-vv"])

        kernel_path = repo_root / "share" / "handoff" / "PM_KERNEL.json"
        current_phase = None
        if kernel_path.exists():
            try:
                data = json.loads(kernel_path.read_text())
                current_phase = data.get("current_phase")
            except Exception:
                current_phase = None

        sys.stdout.write("[guard_github_state] Git status:\n")
        sys.stdout.write(status + "\n\n")
        sys.stdout.write(f"[guard_github_state] Current branch: {branch}\n\n")
        sys.stdout.write("[guard_github_state] Branch tracking info:\n")
        sys.stdout.write(branches + "\n\n")

        if current_phase is not None and branch:
            sys.stdout.write(
                f"[guard_github_state] Kernel reports current_phase={current_phase}; you are on branch '{branch}'.\n"
            )
            sys.stdout.write("TODO (Phase 27): enforce phase↔branch alignment and fail-closed on mismatch.\n")
        else:
            sys.stdout.write(
                "[guard_github_state] Could not determine kernel phase or branch cleanly; manual review required.\n"
            )

        # Phase 26.5: informational only, do not block.
        return 0

    except Exception as e:
        sys.stderr.write(f"[guard_github_state] Unexpected error: {e}\n")
        # Still do not block in Phase 26.5.
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
