#!/usr/bin/env python3
"""
OPS Script: Fix DMS Test NOT NULL Constraints (BUG-3)

Adds required NOT NULL fields (content_hash, size_bytes) to test INSERT statements
in test_dms_edge_cases.py to match kb_document schema constraints.

This script is idempotent and safe to run multiple times.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEST_FILE = ROOT / "agentpm" / "tests" / "dms" / "test_dms_edge_cases.py"


def fix_test_inserts():
    """Add content_hash and size_bytes to test INSERT statements."""

    if not TEST_FILE.exists():
        print(f"ERROR: {TEST_FILE} not found")
        return False

    content = TEST_FILE.read_text()
    original_content = content

    fixes_applied = []

    # Fix E01: Active document stale test
    if "INSERT INTO control.kb_document (id, path, title, lifecycle_stage, mtime)" in content:
        content = content.replace(
            "INSERT INTO control.kb_document (id, path, title, lifecycle_stage, mtime)\n        VALUES (%s, %s, %s, %s, %s)",
            "INSERT INTO control.kb_document (id, path, title, lifecycle_stage, mtime, content_hash, size_bytes)\n        VALUES (%s, %s, %s, %s, %s, %s, %s)",
        )
        # Update the values tuple
        content = content.replace(
            '(test_id, f"test/dms_e01_{test_id}.md", "DMS-E01 Test Doc", "active", stale_mtime)',
            '(test_id, f"test/dms_e01_{test_id}.md", "DMS-E01 Test Doc", "active", stale_mtime, \n          hashlib.md5(b"DMS-E01 test content").hexdigest(), 1024)',
        )
        fixes_applied.append("E01: Added content_hash, size_bytes")

    # Fix E02: Phase misalignment test
    if "INSERT INTO control.kb_document (id, path, title, lifecycle_stage, phase_number)" in content:
        content = content.replace(
            "INSERT INTO control.kb_document (id, path, title, lifecycle_stage, phase_number)\n        VALUES (%s, %s, %s, %s, %s)",
            "INSERT INTO control.kb_document (id, path, title, lifecycle_stage, phase_number, content_hash, size_bytes, mtime)\n        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        )
        content = content.replace(
            '(test_id, f"test/dms_e02_{test_id}.md", "DMS-E02 Old Phase Doc", "active", 6)',
            '(test_id, f"test/dms_e02_{test_id}.md", "DMS-E02 Old Phase Doc", "active", 6,\n          hashlib.md5(b"DMS-E02 test content").hexdigest(), 512, datetime.now(UTC))',
        )
        fixes_applied.append("E02: Added content_hash, size_bytes, mtime")

    # Fix E03: Deprecated document test
    if (
        "INSERT INTO control.kb_document (id, path, title, lifecycle_stage, deprecated_at, deprecated_reason)"
        in content
    ):
        content = content.replace(
            "INSERT INTO control.kb_document (id, path, title, lifecycle_stage, deprecated_at, deprecated_reason)\n        VALUES (%s, %s, %s, %s, %s, %s)",
            "INSERT INTO control.kb_document (id, path, title, lifecycle_stage, deprecated_at, deprecated_reason, content_hash, size_bytes, mtime)\n        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        )
        content = content.replace(
            '(\n            test_id,\n            f"test/dms_e03_{test_id}.md",\n            "DMS-E03 Deprecated Doc",\n            "deprecated",\n            deprecated_at,\n            "Replaced by newer version",\n        )',
            '(\n            test_id,\n            f"test/dms_e03_{test_id}.md",\n            "DMS-E03 Deprecated Doc",\n            "deprecated",\n            deprecated_at,\n            "Replaced by newer version",\n            hashlib.md5(b"DMS-E03 test content").hexdigest(),\n            256,\n            deprecated_at,\n        )',
        )
        fixes_applied.append("E03: Added content_hash, size_bytes, mtime")

    # Ensure hashlib is imported
    if "import hashlib" not in content and fixes_applied:
        # Add hashlib import after datetime import
        content = content.replace(
            "from datetime import datetime, timedelta, UTC",
            "from datetime import datetime, timedelta, UTC\nimport hashlib",
        )
        fixes_applied.append("Added hashlib import")

    # Write back if changed
    if content != original_content:
        TEST_FILE.write_text(content)
        print(f"✓ Fixed {TEST_FILE}")
        print("  Applied fixes:")
        for fix in fixes_applied:
            print(f"    - {fix}")
        return True
    else:
        print(f"✓ No changes needed in {TEST_FILE} (already fixed)")
        return True


def main():
    print("=" * 60)
    print("OPS Script: Fix DMS Test NOT NULL Constraints (BUG-3)")
    print("=" * 60)

    success = fix_test_inserts()

    if success:
        print("\n✓ SUCCESS: Test INSERT statements fixed")
        print("\nNext: Run tests to verify:")
        print("  pytest agentpm/tests/dms/test_dms_edge_cases.py::test_dms_e01_active_document_stale -v")
        return 0
    else:
        print("\n✗ FAILED: Could not fix test file")
        return 1


if __name__ == "__main__":
    exit(main())
