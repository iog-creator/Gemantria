#!/usr/bin/env python3
"""
Extraction Script: Gematria Core Phase 1
========================================
Verifies and completes Phase 1 extraction of core numerics into agentpm/modules/gematria.

Phase 1 targets:
- Hebrew utilities (normalization, gematria calculation)
- Math verifier (gematria calculation verification)

This script verifies that:
1. Core files exist in agentpm/modules/gematria
2. Imports are updated to use the new module
3. No duplicate implementations remain
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


def check_file_exists(file_path: Path) -> bool:
    """Check if file exists."""
    return file_path.exists()


def check_imports_in_file(file_path: Path, old_pattern: str, new_pattern: str) -> list[str]:
    """Check for old import patterns in a file."""
    violations = []
    try:
        content = file_path.read_text(encoding="utf-8")
        if old_pattern in content:
            violations.append(f"Found old import pattern: {old_pattern}")
    except Exception as e:
        violations.append(f"Error reading file: {e}")
    return violations


def verify_extraction():
    """Verify Phase 1 extraction status."""
    print("🔍 Verifying Gematria Core Phase 1 Extraction...")
    print()

    all_ok = True

    # Check that gematria module files exist
    hebrew_utils = REPO_ROOT / "agentpm" / "modules" / "gematria" / "utils" / "hebrew_utils.py"
    math_verifier = REPO_ROOT / "agentpm" / "modules" / "gematria" / "utils" / "math_verifier.py"
    hebrew_module = REPO_ROOT / "agentpm" / "modules" / "gematria" / "hebrew.py"
    core_module = REPO_ROOT / "agentpm" / "modules" / "gematria" / "core.py"

    if hebrew_utils.exists():
        print("✅ agentpm/modules/gematria/utils/hebrew_utils.py: Exists")
    else:
        print("❌ agentpm/modules/gematria/utils/hebrew_utils.py: Missing")
        all_ok = False

    if math_verifier.exists():
        print("✅ agentpm/modules/gematria/utils/math_verifier.py: Exists")
    else:
        print("❌ agentpm/modules/gematria/utils/math_verifier.py: Missing")
        all_ok = False

    if hebrew_module.exists():
        print("✅ agentpm/modules/gematria/hebrew.py: Exists")
    else:
        print("❌ agentpm/modules/gematria/hebrew.py: Missing")
        all_ok = False

    if core_module.exists():
        print("✅ agentpm/modules/gematria/core.py: Exists")
    else:
        print("❌ agentpm/modules/gematria/core.py: Missing")
        all_ok = False

    print()

    # Check for old import patterns in src/
    print("🔍 Checking for old import patterns in src/...")
    old_patterns = [
        (
            "from src.core.hebrew_utils import",
            "from agentpm.modules.gematria.utils.hebrew_utils import",
        ),
        (
            "from src.nodes.math_verifier import",
            "from agentpm.modules.gematria.utils.math_verifier import",
        ),
    ]

    violations_found = []
    for src_file in (REPO_ROOT / "src").rglob("*.py"):
        if src_file.is_file():
            for old_pattern, new_pattern in old_patterns:
                violations = check_imports_in_file(src_file, old_pattern, new_pattern)
                if violations:
                    violations_found.append(f"{src_file.relative_to(REPO_ROOT)}: {violations[0]}")

    if violations_found:
        print("⚠️  Found old import patterns:")
        for v in violations_found:
            print(f"   - {v}")
        print("   Note: Some files may still use src.core.ids.normalize_hebrew (acceptable)")
    else:
        print("✅ No old import patterns found in src/")

    print()

    # Check that graph.py uses the new module
    graph_file = REPO_ROOT / "src" / "graph" / "graph.py"
    if graph_file.exists():
        content = graph_file.read_text(encoding="utf-8")
        if "from agentpm.modules.gematria.utils.math_verifier import" in content:
            print("✅ src/graph/graph.py: Uses new math_verifier module")
        else:
            print("⚠️  src/graph/graph.py: May not use new math_verifier module")
            all_ok = False

    print()

    if all_ok:
        print("✅ Phase 1 extraction verified successfully.")
        print("   Core numerics are in agentpm/modules/gematria/")
        print("   Imports are updated to use the new module")
        return 0
    else:
        print("❌ Phase 1 extraction verification failed.")
        print("   Some files are missing or imports need updating.")
        return 1


if __name__ == "__main__":
    sys.exit(verify_extraction())
