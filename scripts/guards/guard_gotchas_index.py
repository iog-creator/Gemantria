#!/usr/bin/env python
"""
guard_gotchas_index.py

Pre-OPS guard to surface known "gotchas" before doing feature work.

Behavior:
- Verifies docs/SSOT/GOTCHAS_INDEX.md exists.
- Scans code for TODO/FIXME/XXX markers via ripgrep (rg) if available.
- Prints a summary report.
- If STRICT_GOTCHAS=1 and any markers are found, exits with code 1.
  Otherwise exits 0.
"""

import os
import sys
import subprocess
from pathlib import Path
from textwrap import indent

# repo root (scripts/guards/ -> repo)
ROOT = Path(__file__).resolve().parents[2]
SSOT_GOTCHAS = ROOT / "docs" / "SSOT" / "GOTCHAS_INDEX.md"

CODE_DIRS = ["scripts", "src", "pmagent"]  # tweak if needed
PATTERN = r"TODO|FIXME|XXX"


def print_header() -> None:
    print("[guard_gotchas_index] Starting gotchas scan")
    print(f"[guard_gotchas_index] Repo root: {ROOT}")


def check_ssot_index() -> bool:
    if SSOT_GOTCHAS.exists():
        print(f"[guard_gotchas_index] Found SSOT gotchas index at {SSOT_GOTCHAS}")
        return True
    else:
        print(
            f"[guard_gotchas_index] ERROR: Missing SSOT gotchas index at {SSOT_GOTCHAS}",
            file=sys.stderr,
        )
        return False


def run_rg_scan() -> int:
    """Run ripgrep over CODE_DIRS and count matches. Return match count."""
    try:
        cmd = ["rg", PATTERN, "-n"] + CODE_DIRS
        print(f"[guard_gotchas_index] Running: {' '.join(cmd)}")
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        print(
            "[guard_gotchas_index] WARNING: rg (ripgrep) not found; skipping static gotchas scan",
            file=sys.stderr,
        )
        return 0

    if proc.returncode not in (0, 1):
        # 0 = matches, 1 = no matches; anything else is an error
        print(
            "[guard_gotchas_index] WARNING: rg returned non-standard code:",
            proc.returncode,
            file=sys.stderr,
        )
        if proc.stderr:
            print(indent(proc.stderr.strip(), prefix="  "), file=sys.stderr)
        return 0

    output = proc.stdout.strip()
    if not output:
        print("[guard_gotchas_index] No TODO/FIXME/XXX markers found in code dirs.")
        return 0

    lines = output.splitlines()
    count = len(lines)
    print(f"[guard_gotchas_index] Found {count} TODO/FIXME/XXX markers in code:")
    print(indent("\n".join(lines[:50]), prefix="  "))
    if count > 50:
        print(f"[guard_gotchas_index] (truncated output; total matches: {count})")
    return count


def main() -> int:
    print_header()
    ok = check_ssot_index()
    if not ok:
        # Missing SSOT index is itself a governance problem
        return 1

    match_count = run_rg_scan()

    strict = os.getenv("STRICT_GOTCHAS", "").strip()
    if strict and strict != "0":
        if match_count > 0:
            print(
                f"[guard_gotchas_index] STRICT_GOTCHAS is set; "
                f"{match_count} markers found. Treating as blocking failure.",
                file=sys.stderr,
            )
            return 1
        else:
            print("[guard_gotchas_index] STRICT_GOTCHAS is set and no markers found. OK.")
    else:
        print("[guard_gotchas_index] STRICT_GOTCHAS is not set or false; reporting gotchas but not failing build.")

    print("[guard_gotchas_index] Gotchas scan complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# --- Namespace Drift Check (Phase 3, Layer 3.6) ---
print("\n[guard_gotchas_index] Checking for namespace drift (agentpm)...")
try:
    cmd = ["rg", "agentpm", "-n", "scripts", "src", "pmagent", "docs"]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    ns_output = proc.stdout.strip()
    if ns_output:
        print("[guard_gotchas_index] ⚠️  NAMESPACE GOTCHAS FOUND:")
        for line in ns_output.split("\n")[:10]:  # Show first 10
            print(f"  {line}")
        lines = ns_output.split("\n")
        if len(lines) > 10:
            print(f"  ... and {len(lines) - 10} more")
        if os.environ.get("STRICT_GOTCHAS") == "1":
            print("[guard_gotchas_index] STRICT mode: failing due to namespace drift")
            sys.exit(1)
    else:
        print("[guard_gotchas_index] ✓ No namespace drift detected")
except FileNotFoundError:
    print(
        "[guard_gotchas_index] WARNING: ripgrep not found; namespace check skipped.",
        file=sys.stderr,
    )
