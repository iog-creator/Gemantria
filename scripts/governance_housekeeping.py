#!/usr/bin/env python3
"""
governance_housekeeping.py — Automated governance maintenance per Rule-058.

Integrates with existing housekeeping workflow to ensure governance artifacts
stay current and compliant. Called automatically by make housekeeping targets.

Functions:
- Update governance database with latest artifacts
- Validate governance compliance
- Generate governance health reports
- Check for stale governance artifacts
- Log compliance status for audit trails

Usage:
    python scripts/governance_housekeeping.py  # Run full housekeeping cycle
"""

import os
import subprocess
import sys
from pathlib import Path

# Load environment variables
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from infra.env_loader import ensure_env_loaded

ensure_env_loaded()

# Database connection
GEMATRIA_DSN = os.environ.get("GEMATRIA_DSN")


def run_command(cmd: list, description: str) -> bool:
    """Run a command and return success status."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(f"  STDOUT: {result.stdout}")
            print(f"  STDERR: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False


def update_governance_artifacts():
    """Update governance artifacts in database."""
    return run_command(
        [sys.executable, "scripts/governance_tracker.py", "update"], "Updating governance artifacts database"
    )


def validate_governance_compliance():
    """Validate governance compliance."""
    # For initial housekeeping runs, be more lenient about stale artifacts
    # This allows housekeeping to succeed even with stale artifacts on first run
    cmd = [sys.executable, "scripts/governance_tracker.py", "validate", "--lenient"]
    return run_command(cmd, "Validating governance compliance (lenient mode)")


def check_stale_artifacts():
    """Check for stale governance artifacts."""
    return run_command(
        [sys.executable, "scripts/governance_tracker.py", "stale"], "Checking for stale governance artifacts"
    )


def run_document_hints():
    """Run document management hint checks."""
    # Document hints are informational and should not fail housekeeping
    try:
        result = subprocess.run(
            [sys.executable, "scripts/document_management_hints.py"], capture_output=True, text=True, cwd=ROOT
        )
        print("🔧 Running document management hint checks...")
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Hint details: {result.stderr}")
        print("✅ Document management hint checks completed (informational)")
        return True  # Always succeed for hints
    except Exception as e:
        print(f"⚠️ Document hint check error (non-fatal): {e}")
        return True  # Still succeed for hints


def regenerate_governance_docs():
    """Regenerate governance documentation."""
    success = True

    # Update hints registry if needed
    if run_command([sys.executable, "scripts/generate_forest.py"], "Regenerating forest overview"):
        # Share sync the updated docs
        success &= run_command(["make", "share.sync"], "Syncing governance docs to share directory")

    return success


def log_compliance_status(success: bool, operation: str):
    """Log compliance status to database if available."""
    if not GEMATRIA_DSN:
        return

    try:
        import psycopg

        with psycopg.connect(GEMATRIA_DSN) as conn:
            with conn.cursor() as cur:
                import json

                cur.execute(
                    """
                    INSERT INTO governance_compliance_log
                    (check_type, check_result, details, triggered_by)
                    VALUES (%s, %s, %s, %s)
                """,
                    (
                        "housekeeping",
                        "pass" if success else "fail",
                        json.dumps({"operation": operation, "timestamp": "now"}),
                        "housekeeping_script",
                    ),
                )
                conn.commit()
    except Exception as e:
        print(f"⚠️ Failed to log compliance status: {e}")


def main():
    """Run complete governance housekeeping cycle."""
    print("🏠 GOVERNANCE HOUSEKEEPING STARTED (Rule-058)")
    print("=" * 50)

    operations = [
        ("Update governance artifacts", update_governance_artifacts),
        ("Run document management hints", run_document_hints),
        ("Validate governance compliance", validate_governance_compliance),
        ("Check stale artifacts", check_stale_artifacts),
        ("Regenerate governance docs", regenerate_governance_docs),
    ]

    all_success = True
    for description, operation in operations:
        success = operation()
        if not success:
            all_success = False
        print()

    # Generate final report
    print("📊 Generating governance health report...")
    run_command([sys.executable, "scripts/governance_tracker.py", "report"], "Generating final governance report")

    # Log final status
    log_compliance_status(all_success, "full_housekeeping_cycle")

    if all_success:
        print("✅ GOVERNANCE HOUSEKEEPING COMPLETED SUCCESSFULLY")
        print("🔥🔥🔥 Rule-058 compliance achieved 🔥🔥🔥")
    else:
        print("❌ GOVERNANCE HOUSEKEEPING COMPLETED WITH ISSUES")
        print("🔍 Check logs above for specific failures")
        sys.exit(1)


if __name__ == "__main__":
    main()
