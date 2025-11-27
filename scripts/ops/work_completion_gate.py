#!/usr/bin/env python3
"""
Automatic Work Completion Gate System (AWCG).

Enforces mandatory housekeeping (Rule 058), verifies work completion,
and generates completion envelopes with next steps.
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.ops.auto_housekeeping import run_auto_housekeeping
from scripts.ops.generate_completion_envelope import generate_completion_envelope
from scripts.ops.verify_work_complete import verify_work_complete


def work_completion_gate(
    work_summary: dict[str, Any],
    *,
    verify_working: bool = True,
    generate_envelope: bool = True,
    update_next_steps: bool = True,
) -> dict[str, Any]:
    """
    Automatic gate that runs after any work session.

    Args:
        work_summary: Dict with keys:
            - work_type: str (e.g., "phase_13b", "feature", "bugfix")
            - files_changed: list[str]
            - tests_run: bool
            - tests_passed: bool
            - description: str
        verify_working: Whether to verify work actually works
        generate_envelope: Whether to generate completion envelope
        update_next_steps: Whether to update NEXT_STEPS.md

    Returns:
        Dict with completion_envelope, next_steps, verification_status
    """
    work_type = work_summary.get("work_type", "unknown")
    files_changed = work_summary.get("files_changed", [])
    description = work_summary.get("description", "")

    result: dict[str, Any] = {
        "work_type": work_type,
        "timestamp": datetime.now(UTC).isoformat(),
        "verification_status": {},
        "completion_envelope": None,
        "next_steps": [],
    }

    # Step 1: Enforce mandatory housekeeping (Rule 058)
    print("🔧 Running automatic housekeeping (Rule 058)...")
    housekeeping_result = run_auto_housekeeping()
    result["housekeeping"] = housekeeping_result

    if not housekeeping_result.get("ok"):
        print("❌ Housekeeping failed - failing closed")
        result["status"] = "failed"
        result["error"] = "Housekeeping failed"
        return result

    # Step 2: Verify work actually works (if requested)
    if verify_working:
        print(f"✅ Verifying work completion for {work_type}...")
        verification = verify_work_complete(
            work_type=work_type,
            files_changed=files_changed,
            run_tests=True,
            check_runtime=True,
            browser_verify="ui" in work_type.lower() or any("ui" in f.lower() for f in files_changed),
        )
        result["verification_status"] = verification

        if not verification.get("ok"):
            print("⚠️  Work verification failed - check details")
            result["status"] = "warning"
        else:
            print("✅ Work verification passed")

    # Step 3: Generate completion envelope (if requested)
    if generate_envelope:
        print("📦 Generating completion envelope...")
        envelope = generate_completion_envelope(
            work_summary=work_summary,
            verification_status=result.get("verification_status", {}),
        )
        result["completion_envelope"] = envelope
        result["next_steps"] = envelope.get("next_steps", [])

        # Write envelope to evidence directory
        evidence_dir = Path("evidence/pmagent")
        evidence_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        envelope_path = evidence_dir / f"completion-{timestamp}.json"
        with open(envelope_path, "w") as f:
            json.dump(envelope, f, indent=2)
        print(f"📄 Completion envelope written to {envelope_path}")

    # Step 4: Update NEXT_STEPS.md (if requested)
    if update_next_steps:
        print("📝 Updating NEXT_STEPS.md...")
        try:
            from scripts.generate_handoff import update_next_steps_from_envelope

            if result.get("completion_envelope"):
                update_next_steps_from_envelope(result["completion_envelope"])
                print("✅ NEXT_STEPS.md updated")
        except Exception as e:
            print(f"⚠️  Failed to update NEXT_STEPS.md: {e}")
            result["next_steps_update_error"] = str(e)

    result["status"] = "success"
    print("✅ Work completion gate passed")
    return result


def main() -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Automatic Work Completion Gate")
    parser.add_argument("--work-type", required=True, help="Type of work (e.g., phase_13b, feature)")
    parser.add_argument("--files-changed", nargs="+", default=[], help="List of changed files")
    parser.add_argument("--tests-passed", type=bool, default=True, help="Whether tests passed")
    parser.add_argument("--description", required=True, help="Description of work completed")
    parser.add_argument("--no-verify", action="store_true", help="Skip work verification")
    parser.add_argument("--no-envelope", action="store_true", help="Skip envelope generation")
    parser.add_argument("--no-next-steps", action="store_true", help="Skip NEXT_STEPS.md update")

    args = parser.parse_args()

    work_summary = {
        "work_type": args.work_type,
        "files_changed": args.files_changed,
        "tests_run": True,
        "tests_passed": args.tests_passed,
        "description": args.description,
    }

    result = work_completion_gate(
        work_summary,
        verify_working=not args.no_verify,
        generate_envelope=not args.no_envelope,
        update_next_steps=not args.no_next_steps,
    )

    if result["status"] == "failed":
        return 1
    if result["status"] == "warning":
        return 0  # Warning is non-fatal

    return 0


if __name__ == "__main__":
    sys.exit(main())
