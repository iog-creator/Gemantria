#!/usr/bin/env python3
"""
Guard: Repo Layer 4 Alignment

Detects plan vs implementation drift by comparing Layer 4 SSOT plan expectations
with actual code locations in the repository.

Canonical motivation: Layer 4 code landed in scripts/code_ingest/ instead of
scripts/governance/ as specified in LAYER4_CODE_INGESTION_PLAN.md.

Usage:
    python scripts/guards/guard_repo_layer4_alignment.py [--strict]

Modes:
    HINT: Emit warnings only (exit 0)
    STRICT: Fail closed on mismatches (exit 1)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List, Set

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / "evidence" / "repo"
LAYER4_PLAN = REPO_ROOT / "docs" / "SSOT" / "LAYER4_CODE_INGESTION_PLAN.md"


def parse_expected_paths_from_plan() -> Set[str]:
    """
    Extract expected file paths from Layer 4 plan.

    The plan explicitly mentions these files should exist:
    - scripts/governance/ingest_docs_to_db.py
    - scripts/governance/ingest_doc_content.py
    - scripts/governance/ingest_doc_embeddings.py
    - scripts/governance/classify_fragments.py
    - agentpm/kb/classify.py
    - agentpm/kb/search.py
    """
    if not LAYER4_PLAN.exists():
        return set()

    text = LAYER4_PLAN.read_text(encoding="utf-8")
    expected = set()

    # Parse documented file paths from plan
    # These are explicitly mentioned in "Files Modified" sections
    documented_paths = [
        "scripts/governance/ingest_docs_to_db.py",
        "scripts/governance/ingest_doc_content.py",
        "scripts/governance/ingest_doc_embeddings.py",
        "scripts/governance/classify_fragments.py",
        "agentpm/kb/classify.py",
        "agentpm/kb/search.py",
        "scripts/kb/build_kb_registry.py",
    ]

    for path in documented_paths:
        if path in text:  # Verify it's actually mentioned in the plan
            expected.add(path)

    return expected


def scan_actual_layer4_code() -> Set[str]:
    """
    Scan repository for actual Layer 4 implementation files.

    Known locations (from reality):
    - scripts/code_ingest/embed_code_fragments.py
    - scripts/code_ingest/export_code_fragments.py
    - agentpm/kb/search.py
    """
    actual = set()

    # Scan known implementation directories
    code_ingest_dir = REPO_ROOT / "scripts" / "code_ingest"
    if code_ingest_dir.exists():
        for py_file in code_ingest_dir.glob("*.py"):
            actual.add(str(py_file.relative_to(REPO_ROOT)))

    # Check for KB search implementation
    kb_search = REPO_ROOT / "agentpm" / "kb" / "search.py"
    if kb_search.exists():
        actual.add(str(kb_search.relative_to(REPO_ROOT)))

    # Check for classify implementation
    kb_classify = REPO_ROOT / "agentpm" / "kb" / "classify.py"
    if kb_classify.exists():
        actual.add(str(kb_classify.relative_to(REPO_ROOT)))

    return actual


def check_expected_paths_exist(expected: Set[str]) -> Dict[str, bool]:
    """Check which expected paths actually exist in the repo."""
    existence = {}
    for path in expected:
        full_path = REPO_ROOT / path
        existence[path] = full_path.exists()
    return existence


def detect_integration_islands(actual: Set[str]) -> List[str]:
    """
    Identify integration islands: directories containing Layer 4 code
    that aren't mentioned in the plan.
    """
    islands = []

    for path in actual:
        if path.startswith("scripts/code_ingest/"):
            islands.append(path)

    return islands


def main() -> int:
    """
    Run the alignment guard.

    Returns:
        0: HINT mode or STRICT mode with no violations
        1: STRICT mode with violations detected
    """
    strict_mode = "--strict" in sys.argv or os.getenv("STRICT_MODE") == "STRICT"

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    # Parse expectations and reality
    expected_paths = parse_expected_paths_from_plan()
    actual_paths = scan_actual_layer4_code()
    path_existence = check_expected_paths_exist(expected_paths)
    integration_islands = detect_integration_islands(actual_paths)

    # Compute deltas
    missing_expected = [p for p, exists in path_existence.items() if not exists]
    unexpected_locations = integration_islands

    # Determine status
    has_violations = bool(missing_expected or unexpected_locations)
    status = "fail" if has_violations else "pass"

    # Build evidence
    evidence = {
        "status": status,
        "strict_mode": strict_mode,
        "layer4_plan": str(LAYER4_PLAN.relative_to(REPO_ROOT)),
        "expected_paths": sorted(expected_paths),
        "actual_paths": sorted(actual_paths),
        "missing_expected_paths": sorted(missing_expected),
        "unexpected_locations": sorted(unexpected_locations),
        "path_existence": path_existence,
        "violations": {
            "count": len(missing_expected) + len(unexpected_locations),
            "missing_files": len(missing_expected),
            "integration_islands": len(unexpected_locations),
        },
        "recommended_actions": [],
    }

    # Generate recommendations
    if missing_expected:
        evidence["recommended_actions"].append(f"Missing {len(missing_expected)} expected files from Layer 4 plan")

    if unexpected_locations:
        evidence["recommended_actions"].append(
            f"Found {len(unexpected_locations)} files in scripts/code_ingest/ (plan expected scripts/governance/)"
        )
        evidence["recommended_actions"].append(
            "Update LAYER4_CODE_INGESTION_PLAN.md or migrate code to planned locations"
        )

    # Write evidence
    evidence_path = EVIDENCE_DIR / "guard_layer4_alignment.json"
    evidence_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")

    # Print summary
    print(f"Layer 4 Alignment Guard: {status.upper()}")
    print(f"  Expected paths: {len(expected_paths)}")
    print(f"  Actual paths: {len(actual_paths)}")
    print(f"  Missing: {len(missing_expected)}")
    print(f"  Integration islands: {len(unexpected_locations)}")

    if has_violations:
        print("\\nViolations detected:")
        for action in evidence["recommended_actions"]:
            print(f"  - {action}")

    print(f"\\nEvidence: {evidence_path.relative_to(REPO_ROOT)}")

    # Exit based on mode
    if strict_mode and has_violations:
        print("\\n❌ STRICT MODE: Alignment violations detected (exit 1)")
        return 1
    elif has_violations:
        print("\\n⚠️  HINT MODE: Warnings only (exit 0)")
        return 0
    else:
        print("\\n✅ No alignment violations detected")
        return 0


if __name__ == "__main__":
    import os

    sys.exit(main())
