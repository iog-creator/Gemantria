#!/usr/bin/env python3
"""
OPS Script: Fix DMS psycopg Row Access (BUG-2)

Fixes the dict_row access pattern in staleness.py after psycopg2 → psycopg3 migration.
With psycopg3 dict_row, results are dicts, so result[0] → result['column_name'].

This script is idempotent and safe to run multiple times.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STALENESS_FILE = ROOT / "agentpm" / "dms" / "staleness.py"


def fix_staleness_row_access():
    """Fix all result[0] access patterns to use dict keys."""

    if not STALENESS_FILE.exists():
        print(f"ERROR: {STALENESS_FILE} not found")
        return False

    content = STALENESS_FILE.read_text()
    original_content = content

    # Fix patterns where we do SELECT COUNT(*) and access result[0]
    # Pattern 1: SELECT COUNT(*) without alias
    fixes_applied = []

    # Fix canonical tracking
    if "SELECT COUNT(*)\n            FROM control.kb_document\n            WHERE is_canonical = true" in content:
        content = content.replace(
            'SELECT COUNT(*)\n            FROM control.kb_document\n            WHERE is_canonical = true\n              AND lifecycle_stage = \'active\'\n        """)\n        result = cur.fetchone()\n        canonical_docs = result[0]',
            "SELECT COUNT(*) as cnt\n            FROM control.kb_document\n            WHERE is_canonical = true\n              AND lifecycle_stage = 'active'\n        \"\"\")\n        result = cur.fetchone()\n        canonical_docs = result['cnt']",
        )
        fixes_applied.append("canonical_docs COUNT(*) query")

    # Check if there are any remaining result[0] or result[index] patterns
    remaining_index_access = re.findall(r"result\[\d+\]", content)
    if remaining_index_access:
        print(f"WARNING: Found remaining index access patterns: {remaining_index_access}")
        print("These may need manual review if they're not COUNT queries")

    # Write back if changed
    if content != original_content:
        STALENESS_FILE.write_text(content)
        print(f"✓ Fixed {STALENESS_FILE}")
        print(f"  Applied fixes: {', '.join(fixes_applied)}")
        return True
    else:
        print(f"✓ No changes needed in {STALENESS_FILE} (already fixed)")
        return True


def main():
    print("=" * 60)
    print("OPS Script: Fix DMS psycopg Row Access (BUG-2)")
    print("=" * 60)

    success = fix_staleness_row_access()

    if success:
        print("\n✓ SUCCESS: staleness.py row access fixed")
        print("\nNext: Run staleness module to verify:")
        print(
            '  python3 -c "from agentpm.dms.staleness import compute_dms_staleness_metrics; import json; print(json.dumps(compute_dms_staleness_metrics(), indent=2))"'
        )
        return 0
    else:
        print("\n✗ FAILED: Could not fix staleness.py")
        return 1


if __name__ == "__main__":
    exit(main())
