#!/usr/bin/env python3
"""
Guard: Cross-References Database Count

Validates that cross-references are persisted to the database
and meet minimum count expectations.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.persist.crossref_writer import get_crossref_count


def main():
    """Validate cross-reference persistence to database."""
    if len(sys.argv) < 2:
        print("Usage: guard_crossrefs_db_count.py <run_id> [expected_count]", file=sys.stderr)
        sys.exit(1)

    run_id = sys.argv[1]
    expected_count = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    # Check if database is available
    dsn = os.getenv("GEMATRIA_DSN")
    if not dsn:
        print("SKIP: GEMATRIA_DSN not set (database persistence disabled)", file=sys.stderr)
        sys.exit(0)

    try:
        actual_count = get_crossref_count(run_id)
    except Exception as e:
        print(f"ERROR: Failed to query crossref count: {e}", file=sys.stderr)
        sys.exit(1)

    if expected_count > 0 and actual_count < expected_count:
        print(f"ERROR: Expected ≥{expected_count} crossrefs, found {actual_count}", file=sys.stderr)
        sys.exit(1)

    if actual_count == 0:
        print("SKIP: No crossrefs found (persistence may be disabled)", file=sys.stderr)
        sys.exit(0)

    print(f"OK: crossrefs rows {actual_count} ≥ expected {expected_count}")
    sys.exit(0)


if __name__ == "__main__":
    main()
