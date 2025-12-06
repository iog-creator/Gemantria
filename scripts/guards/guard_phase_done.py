#!/usr/bin/env python3
"""
guard_phase_done.py

Minimal guard for phase-level "DONE" checklist.

- Reads a phase number (e.g. 23) and mode (HINT or STRICT).
- Verifies key docs exist under share/ (phase index and checklist).
- Emits a JSON verdict describing any missing artifacts.

During Phase 23, this guard is intended to run in HINT mode only.
STRICT mode is available for future governance phases.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SHARE_DIR = REPO_ROOT / "share"


@dataclass
class PhaseDoneIssue:
    kind: str
    message: str
    path: str | None = None


@dataclass
class PhaseDoneVerdict:
    ok: bool
    phase: str
    mode: str
    issues: list[PhaseDoneIssue]


def build_verdict(phase: str, mode: str) -> PhaseDoneVerdict:
    issues: list[PhaseDoneIssue] = []

    phase_index = SHARE_DIR / f"PHASE{phase}_INDEX.md"
    checklist = SHARE_DIR / "PHASE23_PHASE_DONE_CHECKLIST.md"

    if not phase_index.exists():
        issues.append(
            PhaseDoneIssue(
                kind="missing_phase_index",
                message=f"Expected phase index doc at {phase_index}",
                path=str(phase_index),
            )
        )

    # For now, we rely on a single Phase 23 checklist doc that governs 23+.
    if not checklist.exists():
        issues.append(
            PhaseDoneIssue(
                kind="missing_checklist",
                message="Phase-DONE checklist doc (PHASE23_PHASE_DONE_CHECKLIST.md) not found",
                path=str(checklist),
            )
        )

    ok = not issues
    return PhaseDoneVerdict(ok=ok, phase=phase, mode=mode, issues=issues)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Guard for phase-level DONE checklist.")
    parser.add_argument(
        "--phase",
        required=True,
        help="Phase number, e.g., 23",
    )
    parser.add_argument(
        "--mode",
        choices=["HINT", "STRICT"],
        default="HINT",
        help="Enforcement mode. Phase 23 uses HINT only.",
    )

    args = parser.parse_args(argv)
    phase = args.phase
    mode = args.mode

    verdict = build_verdict(phase=phase, mode=mode)

    payload = asdict(verdict)
    # Convert dataclasses inside list to dicts
    payload["issues"] = [asdict(issue) for issue in verdict.issues]

    print(json.dumps(payload, indent=2, sort_keys=True))

    if verdict.ok:
        return 0

    # In HINT mode, we never fail the build.
    if mode == "HINT":
        return 0

    # STRICT mode: fail if any issues.
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
