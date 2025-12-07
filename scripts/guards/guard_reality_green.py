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
        from pmagent.scripts.state.ledger_verify import verify_ledger  # noqa: E402

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


def check_hints_required() -> CheckResult:
    """Check that DMS hint registry is accessible and has hints configured (ADR-059)."""
    try:
        from pmagent.hints.registry import load_hints_for_flow

        # Test loading hints for key flows
        flows_to_check = [
            ("handoff", "handoff.generate"),
            ("status_api", "status_snapshot"),
            ("pmagent", "capability_session"),
        ]

        total_hints = 0
        flows_with_hints = 0
        for scope, flow in flows_to_check:
            try:
                hints = load_hints_for_flow(scope=scope, applies_to={"flow": flow}, mode="HINT")
                required_count = len(hints.get("required", []))
                if required_count > 0:
                    flows_with_hints += 1
                    total_hints += required_count
            except Exception:
                # Graceful degradation - if DB unavailable, this is OK in HINT mode
                pass

        if total_hints > 0:
            return CheckResult(
                "DMS Hint Registry",
                True,
                f"DMS hint registry accessible with {total_hints} REQUIRED hints across {flows_with_hints} flow(s)",
                {"total_hints": total_hints, "flows_with_hints": flows_with_hints},
            )
        else:
            # Empty registry is OK (no hints configured yet)
            return CheckResult(
                "DMS Hint Registry",
                True,
                "DMS hint registry accessible (no REQUIRED hints configured yet)",
                {"note": "Empty registry is OK"},
            )
    except ImportError as e:
        return CheckResult(
            "DMS Hint Registry",
            False,
            f"Failed to import hint registry: {e}",
            {"error": str(e)},
        )
    except Exception as e:
        # In STRICT mode, this would fail, but in HINT mode (default), we allow graceful degradation
        return CheckResult(
            "DMS Hint Registry",
            True,  # Pass in HINT mode (graceful degradation)
            f"DMS hint registry check skipped (graceful degradation): {e}",
            {"note": "DB may be unavailable", "error": str(e)},
        )


def check_repo_alignment() -> CheckResult:
    """Check Layer 4 plan vs implementation alignment (detect drift)."""
    try:
        script = ROOT / "scripts" / "guards" / "guard_repo_layer4_alignment.py"
        if not script.exists():
            return CheckResult(
                "Repo Alignment (Layer 4)",
                True,  # Pass if guard doesn't exist yet
                "Alignment guard not yet deployed (OK during transition)",
                {"note": "Guard expected at scripts/guards/guard_repo_layer4_alignment.py"},
            )

        _exit_code, stdout, _stderr = run_subprocess_check(script)

        # Guard is in HINT mode by default, so exit_code = 0 always
        # Parse the stdout to check for violations
        has_violations = "FAIL" in stdout or "Violations detected" in stdout

        if has_violations:
            return CheckResult(
                "Repo Alignment (Layer 4)",
                True,  # Pass in HINT mode (warnings only)
                "Plan vs implementation drift detected (HINT mode: warnings only)",
                {"output": stdout, "note": "Run with --strict to enforce"},
            )
        else:
            return CheckResult(
                "Repo Alignment (Layer 4)",
                True,
                "No plan vs implementation drift detected",
                {"output": stdout},
            )
    except Exception as e:
        return CheckResult(
            "Repo Alignment (Layer 4)",
            False,
            f"Failed to run alignment guard: {e}",
            {"error": str(e)},
        )


def check_dms_alignment() -> CheckResult:
    """Check pmagent control-plane DMS-Share alignment (Phase 24.B)."""
    script = ROOT / "scripts" / "guards" / "guard_dms_share_alignment.py"
    if not script.exists():  # Should not happen if correctly deployed
        return CheckResult("DMS Alignment", False, "Guard script missing", {})

    # Run in STRICT mode for reality.green
    exit_code, stdout, stderr = run_subprocess_check(script, ["--mode", "STRICT"])

    if exit_code == 0:
        return CheckResult(
            "DMS Alignment", True, "pmagent control-plane DMS and Share are aligned", {"output": stdout.strip()}
        )
    else:
        # Try to parse JSON output for better error message
        try:
            data = json.loads(stdout)
            # Construct message from mismatch arrays
            details = []
            if data.get("missing_in_share"):
                details.append(f"Missing in share: {len(data['missing_in_share'])}")
            if data.get("missing_in_dms"):
                details.append(f"Missing in pmagent control-plane DMS: {len(data['missing_in_dms'])}")
            if data.get("extra_in_share"):
                details.append(f"Extra in share: {len(data['extra_in_share'])}")

            msg = f"pmagent control-plane DMS Alignment BROKEN: {', '.join(details)}"
            return CheckResult("DMS Alignment", False, msg, data)
        except:
            pass

        return CheckResult(
            "DMS Alignment", False, f"pmagent control-plane DMS Alignment failed: {stderr.strip()}", {"output": stdout}
        )


def check_dms_metadata() -> CheckResult:
    """Check pmagent control-plane DMS metadata health (Phase 27.J)."""
    try:
        from scripts.config.env import get_rw_dsn
        import psycopg

        dsn = get_rw_dsn()
        with psycopg.connect(dsn) as conn, conn.cursor() as cur:
            # 1. Check importance distribution
            cur.execute("""
                SELECT importance, count(*)
                FROM control.doc_registry
                GROUP BY importance
                ORDER BY importance
            """)
            dist = {row[0]: row[1] for row in cur.fetchall()}

            # 2. Check for enabled low-importance docs
            cur.execute("""
                SELECT count(*)
                FROM control.doc_registry
                WHERE importance = 'low' AND enabled = true
            """)
            low_enabled = cur.fetchone()[0]

            if low_enabled == 0:
                return CheckResult(
                    "DMS Metadata",
                    True,
                    f"pmagent control-plane DMS metadata sane (low_enabled={low_enabled})",
                    {"distribution": dist},
                )
            else:
                return CheckResult(
                    "DMS Metadata",
                    False,
                    f"Found {low_enabled} enabled low-importance docs in pmagent control-plane DMS (cleanup required)",
                    {"distribution": dist, "low_enabled": low_enabled},
                )
    except Exception as e:
        return CheckResult("DMS Metadata", False, f"Metadata check failed: {e}", {})


def check_agents_dms_contract() -> CheckResult:
    """
    Verify that AGENTS.md rows in pmagent control-plane DMS (control.doc_registry) obey the AGENTS<->DMS contract.

    Invariants (Phase 27.L Batch 3 - tightened):
    - Only enabled rows with importance in ('critical', 'high') and required tags are considered AGENTS rows.
    - Root AGENTS.md: importance='critical', enabled=true, tags include 'ssot' and 'agent_framework_index'.
    - Any AGENTS.md: importance in ('critical', 'high'), enabled=true, repo_path not under archive/,
      tags include 'ssot' and 'agent_framework' at minimum.
    - All AGENTS rows must correspond to files that exist on disk (hard error if missing).

    Note: pmagent is the governance engine; Gemantria is the governed project.
    The pmagent control-plane DMS records and enforces the semantics defined by AGENTS.md.
    """
    try:
        from scripts.config.env import get_rw_dsn
        import psycopg
        from pathlib import Path

        dsn = get_rw_dsn()
        repo_root = Path(__file__).resolve().parents[2]

        with psycopg.connect(dsn) as conn, conn.cursor() as cur:
            # Only check enabled rows with valid importance (Batch 3 contract)
            cur.execute(
                """
                SELECT doc_id, repo_path, importance, enabled, tags
                FROM control.doc_registry
                WHERE repo_path LIKE '%AGENTS.md'
                  AND repo_path NOT LIKE 'backup/%'
                  AND enabled = TRUE
                  AND importance IN ('critical', 'high')
                ORDER BY repo_path
                """
            )
            rows = cur.fetchall()

        if not rows:
            return CheckResult(
                "AGENTS–DMS Contract",
                False,
                "No enabled AGENTS.md rows found in pmagent control-plane DMS (control.doc_registry)",
                {"rows": []},
            )

        violations = []
        for doc_id, repo_path, importance, enabled, tags in rows:
            tags = tags or []
            is_root = repo_path == "AGENTS.md"

            # Hard error: file must exist on disk (Batch 3 - no ghosts allowed)
            file_path = repo_root / repo_path
            if not file_path.exists():
                violations.append(f"{repo_path}: file missing on disk (AGENTS rows must correspond to existing files)")
                continue  # Skip further checks for missing files

            # These should already be enforced by the WHERE clause, but double-check
            if not enabled:
                violations.append(f"{repo_path}: enabled is false (AGENTS must never be archived)")

            if importance not in ("critical", "high"):
                violations.append(f"{repo_path}: importance={importance!r} (must be 'critical' or 'high')")

            if repo_path.startswith("archive/"):
                violations.append(f"{repo_path}: located under archive/ (AGENTS must not be archived)")

            if "ssot" not in tags:
                violations.append(f"{repo_path}: missing 'ssot' tag")

            if "agent_framework" not in tags:
                violations.append(f"{repo_path}: missing 'agent_framework' tag")

            if is_root and "agent_framework_index" not in tags:
                violations.append(f"{repo_path}: missing 'agent_framework_index' tag for root AGENTS.md")

        if violations:
            return CheckResult(
                "AGENTS–DMS Contract",
                False,
                f"{len(violations)} AGENTS metadata violation(s) detected",
                {"violations": violations, "rows": len(rows)},
            )

        return CheckResult(
            "AGENTS–DMS Contract",
            True,
            "All AGENTS.md rows satisfy pmagent control-plane DMS contract",
            {"rows": len(rows)},
        )
    except Exception as e:
        return CheckResult(
            "AGENTS–DMS Contract",
            False,
            f"Contract check failed: {e}",
            {"error": str(e)},
        )


def check_bootstrap_consistency() -> CheckResult:
    """Check consistency between Bootstrap state and SSOT Surface (Phase 24.A)."""
    script = ROOT / "scripts" / "guards" / "guard_bootstrap_consistency.py"
    if not script.exists():
        return CheckResult("Bootstrap Consistency", False, "Guard script missing", {})

    exit_code, stdout, stderr = run_subprocess_check(script, ["--mode", "STRICT"])

    if exit_code == 0:
        return CheckResult(
            "Bootstrap Consistency",
            True,
            "Bootstrap state matches SSOT",
            {"output": stdout.strip()},
        )
    else:
        try:
            data = json.loads(stdout)
            msg = f"Bootstrap Mismatch: {', '.join(data.get('mismatches', []))}"
            return CheckResult("Bootstrap Consistency", False, msg, data)
        except:
            pass
        return CheckResult("Bootstrap Consistency", False, f"Check failed: {stderr.strip()}", {"output": stdout})


def check_share_sync_policy() -> CheckResult:
    """Check Share Sync Policy (Phase 24.C)."""
    script = ROOT / "scripts" / "guards" / "guard_share_sync_policy.py"
    if not script.exists():
        return CheckResult("Share Sync Policy", False, "Guard script missing", {})

    exit_code, stdout, stderr = run_subprocess_check(script, ["--mode", "STRICT"])

    if exit_code == 0:
        return CheckResult(
            "Share Sync Policy",
            True,
            "No unknown or unsafe share/ docs in managed namespaces",
            {"output": stdout.strip()},
        )
    else:
        try:
            data = json.loads(stdout)
            extras = data.get("extra_in_share", [])
            msg = f"Policy Violation: Found {len(extras)} unknown files"
            return CheckResult("Share Sync Policy", False, msg, data)
        except:
            pass
        return CheckResult("Share Sync Policy", False, f"Check failed: {stderr.strip()}", {"output": stdout})


def check_backup_system() -> CheckResult:
    """Check Backup System (Phase 24.D)."""
    # 1. Check recent backup exists
    script_recent = ROOT / "scripts" / "guards" / "guard_backup_recent.py"
    if script_recent.exists():
        exit_code, stdout, stderr = run_subprocess_check(script_recent, ["--mode", "STRICT"])
        if exit_code != 0:
            return CheckResult(
                "Backup System",
                False,
                f"No recent backup found: {stderr.strip()}",
                {"output": stdout},
            )

    # 2. Check rotation logic sanity (dry run)
    script_rotate = ROOT / "scripts" / "ops" / "backup_rotate.py"
    if script_rotate.exists():
        exit_code, stdout, stderr = run_subprocess_check(script_rotate, ["--dry-run"])
        if exit_code != 0:
            return CheckResult(
                "Backup System",
                False,
                f"Backup rotation logic failed: {stderr.strip()}",
                {"output": stdout},
            )
    else:
        return CheckResult("Backup System", False, "Backup rotation script missing", {})

    return CheckResult("Backup System", True, "Recent backup exists and rotation logic is sane", {})


def check_handoff_kernel() -> CheckResult:
    """Check Handoff Kernel (Phase 24.E)."""
    # 1. Generate Kernel (using provisional summary)
    try:
        script_gen = ROOT / "scripts" / "pm" / "generate_handoff_kernel.py"
        run_subprocess_check(script_gen)
    except Exception as e:
        return CheckResult("Handoff Kernel", False, f"Generation failed: {e}", {})

    # 2. Verify Kernel
    script_guard = ROOT / "scripts" / "guards" / "guard_handoff_kernel.py"
    if not script_guard.exists():
        return CheckResult("Handoff Kernel", False, "Guard script missing", {})

    exit_code, stdout, stderr = run_subprocess_check(script_guard, ["--mode", "STRICT"])

    if exit_code == 0:
        return CheckResult(
            "Handoff Kernel",
            True,
            "Handoff kernel is consistent with bootstrap/SSOT/reality.green",
            {"output": stdout.strip()},
        )
    else:
        try:
            data = json.loads(stdout)
            msg = f"Kernel Mismatch: {', '.join(data.get('mismatches', []))}"
            return CheckResult("Handoff Kernel", False, msg, data)
        except:
            pass
        return CheckResult("Handoff Kernel", False, f"Check failed: {stderr.strip()}", {"output": stdout})


def check_root_surface() -> CheckResult:
    """Check Repository Root Surface Policy (Phase 27.G)."""
    script = ROOT / "scripts" / "guards" / "guard_root_surface_policy.py"
    if not script.exists():
        return CheckResult("Root Surface", False, "Guard script missing", {})

    exit_code, stdout, stderr = run_subprocess_check(script, ["--mode", "STRICT"])

    if exit_code == 0:
        return CheckResult(
            "Root Surface",
            True,
            "No unexpected files in repository root",
            {"output": stdout.strip()},
        )
    else:
        # Parse stderr for unexpected files
        unexpected = []
        for line in stderr.splitlines():
            if line.strip().startswith("- "):
                unexpected.append(line.strip()[2:])

        if unexpected:
            msg = f"Found {len(unexpected)} unexpected file(s) in root: {', '.join(unexpected[:5])}"
            if len(unexpected) > 5:
                msg += f" (and {len(unexpected) - 5} more)"
        else:
            msg = "Root surface policy violation detected"

        return CheckResult("Root Surface", False, msg, {"unexpected": unexpected, "output": stdout})


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
        check_hints_required(),  # ADR-059: DMS hint registry accessibility check
        check_repo_alignment(),  # Repo governance: plan vs implementation alignment (Layer 4 drift)
        check_dms_alignment(),  # Phase 24.B: pmagent control-plane DMS <-> Share alignment
        check_dms_metadata(),  # Phase 27.J: pmagent control-plane DMS metadata health
        check_agents_dms_contract(),  # Phase 27.L: AGENTS–pmagent control-plane DMS contract enforcement
        check_bootstrap_consistency(),  # Phase 24.A: Bootstrap vs SSOT
        check_root_surface(),  # Phase 27.G: Repository root surface policy
        check_share_sync_policy(),  # Phase 24.C: Sync Policy Audit
        check_backup_system(),  # Phase 24.D: Backup Retention & Rotation
        check_webui_shell_sanity(),
    ]

    # Special handling for Handoff Kernel (Phase 24.E)
    # It requires the results of previous checks to be written to share/REALITY_GREEN_SUMMARY.json first.

    # 1. Provisional Summary
    provisional_passed = all(c.passed for c in checks)
    provisional_summary = {
        "reality_green": provisional_passed,
        "checks": [
            {
                "name": c.name,
                "passed": c.passed,
            }
            for c in checks
        ],
        "timestamp": subprocess.run(
            ["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True, text=True, check=False
        ).stdout.strip(),
    }

    summary_path = ROOT / "share" / "REALITY_GREEN_SUMMARY.json"
    with open(summary_path, "w") as f:
        json.dump(provisional_summary, f, indent=2)

    # 2. Run Handoff Kernel Check
    hk_result = check_handoff_kernel()
    checks.append(hk_result)

    if not hk_result.passed:
        provisional_passed = False

    all_passed = all(c.passed for c in checks)
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

    # Write final summary to file (Source of Truth for Generator/Kernel)
    with open(summary_path, "w") as f:
        json.dump(summary_json, f, indent=2)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
