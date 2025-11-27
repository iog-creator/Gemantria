#!/usr/bin/env python3
"""
Query Knowledge MCP Catalog (PLAN-073 M1 E04)

Executes a minimal query against mcp.v_catalog and outputs JSON array.
Deterministic ordering: ORDER BY name LIMIT 10.

Rule References: RFC-078 (Postgres Knowledge MCP), Rule 050 (OPS Contract),
Rule 039 (Execution Contract)

Usage:
    python scripts/mcp/query_catalog.py
    make mcp.query
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

try:
    import psycopg
    from scripts.config.env import get_ro_dsn
except ImportError as e:
    print(f"ERROR: Failed to import required modules: {e}", file=sys.stderr)
    sys.exit(1)


def main() -> int:
    """Query mcp.v_catalog and output JSON array."""
    strict_mode = os.getenv("STRICT_MODE", "0") == "1"

    # Get RO DSN
    dsn = get_ro_dsn()
    if not dsn:
        if strict_mode:
            print("ERROR: No RO DSN available (STRICT mode)", file=sys.stderr)
            return 1
        else:
            print("HINT: No RO DSN available (HINT mode)", file=sys.stderr)
            print("[]")  # Empty array for hermetic-friendly behavior
            return 0

    # Query catalog
    try:
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT name, "desc", tags, cost_est, visibility, path, method, auth
                    FROM mcp.v_catalog
                    ORDER BY name
                    LIMIT 10
                    """
                )
                rows = cur.fetchall()
                columns = [desc[0] for desc in cur.description]

                # Convert rows to JSON-serializable format
                results = []
                for row in rows:
                    item = {}
                    for i, col in enumerate(columns):
                        value = row[i]
                        # Convert list-like types to lists
                        if isinstance(value, (list, tuple)):
                            item[col] = list(value)
                        else:
                            item[col] = value
                    results.append(item)

                # Output JSON array
                print(json.dumps(results, indent=2))
                return 0

    except psycopg.errors.UndefinedTable as e:
        if strict_mode:
            print(f"ERROR: View mcp.v_catalog does not exist: {e}", file=sys.stderr)
            return 1
        else:
            print(f"HINT: View mcp.v_catalog does not exist: {e} (HINT mode)", file=sys.stderr)
            print("[]")  # Empty array for hermetic-friendly behavior
            return 0
    except psycopg.OperationalError as e:
        if strict_mode:
            print(f"ERROR: Database connection failed: {e}", file=sys.stderr)
            return 1
        else:
            print(f"HINT: Database connection failed: {e} (HINT mode)", file=sys.stderr)
            print("[]")  # Empty array for hermetic-friendly behavior
            return 0
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
