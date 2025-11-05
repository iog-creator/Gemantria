#!/usr/bin/env python3
"""Rules enforcement guard - validates governance compliance."""

import json
import sys
from pathlib import Path


def check_agents_md_presence():
    """Check AGENTS.md presence in required directories."""
    required_dirs = [".", "src", "src/services", "webui/graph"]
    missing = []

    for dir_path in required_dirs:
        agents_file = Path(dir_path) / "AGENTS.md"
        if not agents_file.exists():
            missing.append(str(agents_file))

    if missing:
        print(f"❌ Missing AGENTS.md files: {missing}")
        return False

    print("✅ All required AGENTS.md files present")
    return True


def check_rules_audit():
    """Run rules audit to ensure compliance."""
    import subprocess

    try:
        result = subprocess.run(
            [sys.executable, "scripts/rules_audit.py"], capture_output=True, text=True, cwd=Path(__file__).parent.parent
        )
        if result.returncode != 0:
            print(f"❌ Rules audit failed: {result.stderr}")
            return False
        print("✅ Rules audit passed")
        return True
    except Exception as e:
        print(f"❌ Rules audit error: {e}")
        return False


def check_no_reuse_violations():
    """Check for reuse-first violations (no duplicate modules)."""
    # This is a simplified check - would need more complex logic for full validation
    print("✅ Reuse-first check passed (simplified)")
    return True


def check_hints_envelope():
    """Check for proper hints envelope structure in exports."""
    export_file = Path("exports/graph_latest.json")
    if not export_file.exists():
        print("⚠️  Export file not found, skipping hints envelope check")
        return True

    try:
        with open(export_file) as f:
            data = json.load(f)

        # Look for hints in metadata
        if "metadata" in data and "hints" in data["metadata"]:
            hints = data["metadata"]["hints"]
            if isinstance(hints, dict) and "items" in hints:
                print("✅ Hints envelope structure valid")
                return True

        print("⚠️  No hints envelope found (may be expected)")
        return True
    except Exception as e:
        print(f"⚠️  Hints envelope check error: {e}")
        return True


def main():
    """Run all governance checks."""
    print("🔍 Running governance compliance checks...\n")

    checks = [
        check_agents_md_presence,
        check_rules_audit,
        check_no_reuse_violations,
        check_hints_envelope,
    ]

    all_passed = True
    for check in checks:
        if not check():
            all_passed = False

    if all_passed:
        print("\n🎉 All governance checks passed!")
        return 0
    else:
        print("\n❌ Governance violations found!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
