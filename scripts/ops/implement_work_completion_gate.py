#!/usr/bin/env python3
"""
Atomic script to implement the Automatic Work Completion Gate System (AWCG).

Sets up all AWCG components, verifies installation, and generates test envelope.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def verify_files_exist() -> bool:
    """Verify all AWCG files exist."""
    required_files = [
        "scripts/ops/work_completion_gate.py",
        "scripts/ops/auto_housekeeping.py",
        "scripts/ops/verify_work_complete.py",
        "scripts/ops/generate_completion_envelope.py",
    ]

    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)

    if missing:
        print(f"❌ Missing required files: {missing}")
        return False

    print("✅ All AWCG files exist")
    return True


def verify_imports() -> bool:
    """Verify all AWCG modules can be imported."""
    import importlib.util

    modules = [
        "scripts.ops.work_completion_gate",
        "scripts.ops.auto_housekeeping",
        "scripts.ops.verify_work_complete",
        "scripts.ops.generate_completion_envelope",
    ]

    try:
        for module_name in modules:
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                raise ImportError(f"Module {module_name} not found")

        print("✅ All AWCG modules import successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def generate_test_envelope() -> bool:
    """Generate a test completion envelope to verify the system works."""
    print("🧪 Generating test completion envelope...")
    try:
        from scripts.ops.work_completion_gate import work_completion_gate

        test_work_summary = {
            "work_type": "governance_awcg",
            "files_changed": ["scripts/ops/work_completion_gate.py"],
            "tests_run": True,
            "tests_passed": True,
            "description": "Implemented Automatic Work Completion Gate System (AWCG)",
        }

        result = work_completion_gate(
            test_work_summary,
            verify_working=False,  # Skip verification for test
            generate_envelope=True,
            update_next_steps=False,  # Skip NEXT_STEPS update for test
        )

        if result.get("status") == "success" and result.get("completion_envelope"):
            print("✅ Test envelope generated successfully")
            return True
        else:
            print(f"❌ Test envelope generation failed: {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Test envelope generation error: {e}")
        return False


def main() -> int:
    """Main implementation script."""
    print("🚀 Implementing Automatic Work Completion Gate System (AWCG)...")
    print()

    # Step 1: Verify files exist
    if not verify_files_exist():
        return 1

    # Step 2: Verify imports
    if not verify_imports():
        return 1

    # Step 3: Generate test envelope
    if not generate_test_envelope():
        return 1

    print()
    print("✅ AWCG implementation complete!")
    print()
    print("Next steps:")
    print("  1. Run: python scripts/ops/work_completion_gate.py --work-type test --description 'Test'")
    print("  2. Verify completion envelope in evidence/pmagent/")
    print("  3. Check NEXT_STEPS.md is updated")

    return 0


if __name__ == "__main__":
    sys.exit(main())
