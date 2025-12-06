#!/usr/bin/env python3
"""
Ledger Verify - System State Ledger Verification

Compares current file hashes against the control.system_state_ledger,
fails if any tracked artifacts are stale/missing.

Rule References: Rule 006 (AGENTS.md Governance), Rule 027 (Docs Sync Gate),
Rule 030 (Share Sync), Rule 069 (Reality Green)

Usage:
    python -m pmagent.scripts.state.ledger_verify
    pmagent state verify
    make state.verify
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.config.env import get_rw_dsn  # noqa: E402
import psycopg  # noqa: E402


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of file content."""
    content = file_path.read_bytes()
    return hashlib.sha256(content).hexdigest()


def get_artifact_list() -> list[tuple[Path, str, str]]:
    """Get list of artifacts to track (shared with ledger_sync.py)."""
    repo_root = ROOT
    return [
        # Root AGENTS.md
        (repo_root / "AGENTS.md", "AGENTS.md", "root"),
        # SSOT docs
        (repo_root / "docs/SSOT/MASTER_PLAN.md", "MASTER_PLAN.md", "docs/SSOT"),
        (repo_root / "docs/runbooks/DB_HEALTH.md", "DB_HEALTH.md", "docs/runbooks"),
        (
            repo_root / "docs/runbooks/PM_SNAPSHOT_CURRENT.md",
            "PM_SNAPSHOT_CURRENT.md",
            "docs/runbooks",
        ),
        (repo_root / "RULES_INDEX.md", "RULES_INDEX.md", "root"),
        # Share exports (control-plane)
        (
            repo_root / "share/atlas/control_plane/system_health.json",
            "system_health.json",
            "share/atlas/control_plane",
        ),
        (
            repo_root / "share/atlas/control_plane/lm_indicator.json",
            "lm_indicator.json",
            "share/atlas/control_plane",
        ),
        # Share exports (docs-control)
        (
            repo_root / "share/exports/docs-control/canonical.json",
            "canonical.json",
            "share/exports/docs-control",
        ),
        (
            repo_root / "share/exports/docs-control/summary.json",
            "summary.json",
            "share/exports/docs-control",
        ),
    ]


def verify_ledger() -> tuple[int, dict]:
    """Verify system state ledger against current artifact hashes."""
    artifacts = get_artifact_list()

    # Get DSN
    try:
        dsn = get_rw_dsn()
    except Exception as e:
        print(f"ERROR: Failed to get DSN: {e}", file=sys.stderr)
        return 1, {"ok": False, "error": f"DSN error: {e}"}

    if not dsn:
        print("SKIP: GEMATRIA_DSN not set", file=sys.stderr)
        return 0, {"ok": True, "skipped": True, "reason": "DSN not set"}

    # Connect to database
    try:
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                results = []
                all_current = True
                stale = []
                missing = []

                for file_path, name, source_of_truth in artifacts:
                    # Check if file exists
                    if not file_path.exists():
                        status = "missing"
                        current_hash = None
                        ledger_hash = None
                        all_current = False
                        missing.append(name)
                        results.append(
                            {
                                "name": name,
                                "source_of_truth": source_of_truth,
                                "status": status,
                                "ledger_hash": ledger_hash,
                                "current_hash": current_hash,
                            }
                        )
                        continue

                    # Compute current hash
                    current_hash = compute_file_hash(file_path)

                    # Look up most recent row in ledger
                    cur.execute(
                        """
                        SELECT hash, status, generated_at
                        FROM control.system_state_ledger
                        WHERE name = %s AND source_of_truth = %s
                        ORDER BY generated_at DESC
                        LIMIT 1
                        """,
                        (name, source_of_truth),
                    )

                    row = cur.fetchone()

                    if row is None:
                        # No ledger entry found
                        status = "missing"
                        ledger_hash = None
                        all_current = False
                        missing.append(name)
                    else:
                        ledger_hash = row[0]
                        if current_hash == ledger_hash:
                            status = "current"
                        else:
                            status = "stale"
                            all_current = False
                            stale.append(name)

                    results.append(
                        {
                            "name": name,
                            "source_of_truth": source_of_truth,
                            "status": status,
                            "ledger_hash": ledger_hash[:16] + "..." if ledger_hash else None,
                            "current_hash": current_hash[:16] + "..." if current_hash else None,
                        }
                    )

                # Print summary table
                print("=" * 80)
                print("LEDGER VERIFICATION SUMMARY")
                print("=" * 80)
                print(f"{'Name':<40} {'Source':<30} {'Status':<10}")
                print("-" * 80)

                for result in results:
                    status_icon = "✓" if result["status"] == "current" else "✗"
                    print(f"{result['name']:<40} {result['source_of_truth']:<30} {status_icon} {result['status']:<10}")

                print("-" * 80)
                print(
                    f"Total: {len(results)}, Current: {len([r for r in results if r['status'] == 'current'])}, "
                    f"Stale: {len(stale)}, Missing: {len(missing)}"
                )
                print("=" * 80)
                print()

                if not all_current:
                    print("❌ LEDGER VERIFICATION FAILED")
                    if stale:
                        print(f"   Stale artifacts ({len(stale)}): {', '.join(stale)}")
                        print("   Run 'make state.sync' to update ledger")
                    if missing:
                        print(f"   Missing artifacts ({len(missing)}): {', '.join(missing)}")
                        print("   Run 'make state.sync' to add missing entries")
                    print()
                else:
                    print("✅ LEDGER VERIFICATION PASSED")
                    print("   All tracked artifacts are current")
                    print()

                # Return JSON summary
                summary = {
                    "ok": all_current,
                    "total": len(results),
                    "current": len([r for r in results if r["status"] == "current"]),
                    "stale": stale,
                    "missing": missing,
                    "results": results,
                }

                return 0 if all_current else 1, summary

    except Exception as e:
        print(f"ERROR: Database connection failed: {e}", file=sys.stderr)
        return 1, {"ok": False, "error": f"Database error: {e}"}


def main() -> int:
    """CLI entrypoint."""
    exit_code, summary = verify_ledger()

    # Print JSON summary
    print("JSON Summary:")
    print(json.dumps(summary, indent=2))

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
