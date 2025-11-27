#!/usr/bin/env python3
"""
Completion Envelope Generator.

Generate structured completion envelope with:
- Work summary
- Verification results
- Next steps (from `pmagent plan next`)
- Handoff instructions for next session
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def get_next_steps_from_pmagent() -> list[dict[str, Any]]:
    """Get next steps from `pmagent plan next`."""
    try:
        result = subprocess.run(
            ["pmagent", "plan", "next"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        # Parse output - this is a simplified parser
        # In practice, pmagent plan next should return JSON
        next_steps = []
        for line in result.stdout.strip().split("\n"):
            if line.strip() and not line.startswith("#"):
                next_steps.append(
                    {
                        "id": f"NEXT_STEPS:{len(next_steps) + 1}",
                        "title": line.strip(),
                        "source": "pmagent",
                    }
                )
        return next_steps
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        # Fallback: return empty list
        return []


def generate_completion_envelope(
    work_summary: dict[str, Any],
    verification_status: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate structured completion envelope.

    Args:
        work_summary: Work summary dict
        verification_status: Verification results dict

    Returns:
        Completion envelope dict
    """
    timestamp = datetime.now(UTC).isoformat()

    # Get next steps from pmagent
    next_steps = get_next_steps_from_pmagent()

    # If pmagent didn't return steps, create a default one
    if not next_steps:
        next_steps = [
            {
                "id": "NEXT_STEPS:1",
                "title": "Review completion envelope and proceed with next work item",
                "source": "default",
            }
        ]

    envelope: dict[str, Any] = {
        "type": "work_completion",
        "version": "1.0",
        "timestamp": timestamp,
        "work": {
            "type": work_summary.get("work_type", "unknown"),
            "description": work_summary.get("description", ""),
            "files_changed": work_summary.get("files_changed", []),
            "tests_passed": work_summary.get("tests_passed", False),
        },
        "verification": {
            "hermetic": verification_status.get("hermetic", {}),
            "live": verification_status.get("live", {}),
            "ui": verification_status.get("ui", {}),
            "lm_slots": verification_status.get("lm_slots", {}),
        },
        "next_steps": next_steps,
        "handoff": {
            "status": "ready" if verification_status.get("ok", False) else "needs_review",
            "instructions": (
                "Work completed successfully. Review verification results and proceed with next steps."
                if verification_status.get("ok", False)
                else "Work completed with warnings. Review verification results before proceeding."
            ),
        },
    }

    return envelope


def main() -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate completion envelope")
    parser.add_argument("--work-summary", required=True, help="JSON work summary")
    parser.add_argument("--verification-status", required=True, help="JSON verification status")

    args = parser.parse_args()

    work_summary = json.loads(args.work_summary)
    verification_status = json.loads(args.verification_status)

    envelope = generate_completion_envelope(work_summary, verification_status)
    print(json.dumps(envelope, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
