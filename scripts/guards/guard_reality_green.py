#!/usr/bin/env python3
"""
Guard: Reality Green - Full System Truth Gate (Option C)

This is the 110% signal that the system is up to date and consistent for the next agent.
Only passes when:
- DB is healthy (Option C: DB-down = failure when GEMATRIA_DSN set)
- Control-plane health checks pass
- AGENTS.md files are in sync with code
- Share directory is synced and required exports exist
- WebUI shell compiles (optional sanity check)

Rule References: Option C (DB is SSOT), Rule 006 (AGENTS.md Governance), Rule 027 (Docs Sync Gate),
Rule 030 (Share Sync), Rule 058 (Auto-Housekeeping)

Usage:
    python scripts/guards/guard_reality_green.py
    make reality.green
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Add project root to path for imports
sys.path.insert(0, str(ROOT))


class CheckResult:
    """Result of a single check."""

    def __init__(self, name: str, passed: bool, message: str = "", details: dict | None = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details or {}


def run_subprocess_check(script_path: Path, args: list[str] | None = None) -> tuple[int, str, str]:
    """Run a subprocess check and return (exit_code, stdout, stderr)."""
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, check=False)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def check_db_health() -> CheckResult:
    """Check DB health (Option C: fail if DSN set but DB unreachable)."""
    script = ROOT / "scripts" / "guards" / "guard_ci_empty_db.py"
    exit_code, stdout, stderr = run_subprocess_check(script)

    if exit_code == 0:
        return CheckResult("DB Health", True, "DB is reachable and healthy", {"output": stdout.strip()})
    else:
        error_msg = stderr.strip() or stdout.strip() or "Unknown error"
        return CheckResult("DB Health", False, f"DB health check failed: {error_msg}", {"exit_code": exit_code})


def check_control_plane_health() -> CheckResult:
    """Check control-plane health."""
    script = ROOT / "scripts" / "guards" / "guard_control_plane_health.py"
    exit_code, stdout, stderr = run_subprocess_check(script)

    if exit_code == 0:
        return CheckResult("Control-Plane Health", True, "Control plane is healthy", {"output": stdout.strip()})
    else:
        error_msg = stderr.strip() or stdout.strip() or "Unknown error"
        return CheckResult(
            "Control-Plane Health",
            False,
            f"Control-plane health check failed: {error_msg}",
            {"exit_code": exit_code},
        )


def check_agents_md_sync() -> CheckResult:
    """Check that AGENTS.md files are in sync with code changes."""
    script = ROOT / "scripts" / "check_agents_md_sync.py"
    exit_code, stdout, stderr = run_subprocess_check(script)

    if exit_code == 0:
        return CheckResult("AGENTS.md Sync", True, "All AGENTS.md files are in sync", {"output": stdout.strip()})
    else:
        error_msg = stderr.strip() or stdout.strip() or "Unknown error"
        return CheckResult(
            "AGENTS.md Sync",
            False,
            f"AGENTS.md sync check failed - files may be stale: {error_msg}",
            {"exit_code": exit_code},
        )


def check_share_sync() -> CheckResult:
    """Check that share/ directory is synced and required exports exist."""
    issues = []

    # Check required control-plane exports
    required_exports = [
        ROOT / "share" / "atlas" / "control_plane" / "system_health.json",
        ROOT / "share" / "atlas" / "control_plane" / "lm_indicator.json",
    ]

    for export_path in required_exports:
        if not export_path.exists():
            issues.append(f"Missing export: {export_path.relative_to(ROOT)}")

    # Check docs-control exports (at least summary.json should exist)
    docs_control_dir = ROOT / "share" / "exports" / "docs-control"
    if docs_control_dir.exists():
        summary_path = docs_control_dir / "summary.json"
        if not summary_path.exists():
            issues.append(f"Missing docs-control export: {summary_path.relative_to(ROOT)}")
    else:
        issues.append(f"Missing docs-control directory: {docs_control_dir.relative_to(ROOT)}")

    # Check webui public exports (should mirror share exports)
    webui_control_plane = ROOT / "webui" / "graph" / "public" / "exports" / "control-plane"
    if webui_control_plane.exists():
        for export_name in ["system_health.json", "lm_indicator.json"]:
            webui_export = webui_control_plane / export_name
            if not webui_export.exists():
                issues.append(f"Missing webui export: {webui_export.relative_to(ROOT)}")

    if issues:
        return CheckResult(
            "Share Sync & Exports",
            False,
            f"Missing required exports: {len(issues)} issue(s)",
            {"issues": issues},
        )

    return CheckResult("Share Sync & Exports", True, "All required exports present", {})


def check_webui_shell_sanity() -> CheckResult:
    """Optional: Check that WebUI shell compiles (static check only)."""
    # Check if orchestrator shell files exist
    shell_dir = ROOT / "webui" / "orchestrator-shell"
    if not shell_dir.exists():
        return CheckResult("WebUI Shell Sanity", True, "WebUI shell directory not present (skipped)", {})

    # Check for key TypeScript files
    key_files = ["MainCanvas.tsx", "LeftRail.tsx", "OrchestratorOverview.tsx"]
    missing_files = []
    for file_name in key_files:
        if not (shell_dir / file_name).exists():
            missing_files.append(file_name)

    if missing_files:
        return CheckResult(
            "WebUI Shell Sanity",
            False,
            f"Missing key WebUI shell files: {', '.join(missing_files)}",
            {"missing": missing_files},
        )

    # For now, just check file existence - actual compilation check would require npm/typescript
    return CheckResult("WebUI Shell Sanity", True, "WebUI shell files present", {})


def check_ledger_verification() -> CheckResult:
    """Check that system state ledger is current (all artifacts match ledger hashes)."""
    try:
        from agentpm.scripts.state.ledger_verify import verify_ledger  # noqa: E402

        exit_code, summary = verify_ledger()

        if exit_code == 0 and summary.get("ok"):
            return CheckResult(
                "Ledger Verification",
                True,
                f"All {summary.get('current', 0)} tracked artifacts are current",
                {"summary": summary},
            )
        else:
            stale = summary.get("stale", [])
            missing = summary.get("missing", [])
            issues = []
            if stale:
                issues.append(f"{len(stale)} stale: {', '.join(stale)}")
            if missing:
                issues.append(f"{len(missing)} missing: {', '.join(missing)}")
            error_msg = "; ".join(issues) if issues else "Ledger verification failed"
            return CheckResult(
                "Ledger Verification",
                False,
                error_msg,
                {"summary": summary, "stale": stale, "missing": missing},
            )
    except ImportError as e:
        return CheckResult(
            "Ledger Verification",
            False,
            f"Failed to import ledger_verify: {e}",
            {"error": str(e)},
        )
    except Exception as e:
        return CheckResult(
            "Ledger Verification",
            False,
            f"Ledger verification error: {e}",
            {"error": str(e)},
        )


def check_ketiv_primary_policy() -> CheckResult:
    """Check that Ketiv-primary policy is enforced (Phase 2, ADR-002)."""
    try:
        exit_code, stdout, stderr = run_subprocess_check(ROOT / "scripts" / "guards" / "guard_ketiv_primary.py", [])

        if exit_code == 0:
            return CheckResult(
                "Ketiv-Primary Policy",
                True,
                "Ketiv-primary policy enforced (gematria uses written form per ADR-002)",
                {"output": stdout},
            )
        else:
            return CheckResult(
                "Ketiv-Primary Policy",
                False,
                f"Ketiv-primary policy violation detected: {stderr[:200] if stderr else stdout[:200]}",
                {"exit_code": exit_code, "output": stdout, "error": stderr},
            )
    except Exception as e:
        return CheckResult(
            "Ketiv-Primary Policy",
            False,
            f"Failed to run Ketiv-primary guard: {e}",
            {"error": str(e)},
        )


def main() -> int:
    """Run all reality green checks and report results."""
    print("🔍 REALITY GREEN - Full System Truth Gate")
    print("=" * 60)
    print()

    checks = [
        check_db_health(),
        check_control_plane_health(),
        check_agents_md_sync(),
        check_share_sync(),
        check_ledger_verification(),  # Must pass: all artifacts must be current in ledger
        check_ketiv_primary_policy(),  # Phase 2: Ketiv-primary policy enforcement (ADR-002)
        check_webui_shell_sanity(),
    ]

    all_passed = True
    results_summary = []

    for check in checks:
        status = "✅ PASS" if check.passed else "❌ FAIL"
        print(f"{status}: {check.name}")
        if check.message:
            print(f"   {check.message}")
        if check.details and not check.passed:
            for key, value in check.details.items():
                if key == "issues" and isinstance(value, list):
                    for issue in value:
                        print(f"      - {issue}")
                elif key == "output" and value:
                    # Only show output if it's an error
                    if not check.passed:
                        print(f"      Output: {value[:200]}")
        print()

        results_summary.append(
            {
                "name": check.name,
                "passed": check.passed,
                "message": check.message,
                "details": check.details,
            }
        )

        if not check.passed:
            all_passed = False

    # Print summary
    print("=" * 60)
    if all_passed:
        print("✅ REALITY GREEN: All checks passed - system is ready")
        print()
        print("This system is up to date and consistent for the next agent.")
        print("DB is healthy, AGENTS.md is synced, share/ is synced, exports are present.")
    else:
        print("❌ REALITY RED: One or more checks failed")
        print()
        print("System is NOT ready. Fix the issues above before:")
        print("  - Declaring a feature 'complete'")
        print("  - Opening a PR for main")
        print("  - Generating a new share/ snapshot for other agents")
        print()
        print("Run individual checks to diagnose:")
        print("  - make book.smoke              # DB health")
        print("  - python scripts/guards/guard_control_plane_health.py  # Control-plane")
        print("  - python scripts/check_agents_md_sync.py --verbose     # AGENTS.md sync")
        print("  - make share.sync              # Share sync")
        print("  - make state.verify            # Ledger verification")
        print("  - make state.sync              # Update ledger if stale")

    # Output JSON summary to stdout (for automation)
    summary_json = {
        "reality_green": all_passed,
        "checks": results_summary,
        "timestamp": subprocess.run(
            ["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True, text=True, check=False
        ).stdout.strip(),
    }
    print()
    print("JSON Summary:")
    print(json.dumps(summary_json, indent=2))

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
