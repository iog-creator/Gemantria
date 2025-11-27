#!/usr/bin/env python3
"""
Guard: DB Health Check

Checks database driver availability, connection status, and graph_stats table readiness.
Returns JSON verdict summarizing DB posture (ready, db_off, partial).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from sqlalchemy import text
    from sqlalchemy.exc import OperationalError, ProgrammingError

    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

    # Define dummy classes/functions when sqlalchemy is not available
    def text(query_str):
        return query_str

    class OperationalError(Exception):
        pass

    class ProgrammingError(Exception):
        pass


# Add project root to path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from agentpm.db.loader import (
    DbDriverMissingError,
    DbUnavailableError,
    get_control_engine,
)


def check_db_health() -> dict:
    """
    Check database health posture.

    Returns:
        Dictionary with health status:
        {
            "ok": bool,
            "mode": "ready" | "db_off" | "partial",
            "checks": {
                "driver_available": bool,
                "connection_ok": bool,
                "graph_stats_ready": bool,
            },
            "details": {
                "errors": list[str],
            },
        }
    """
    result: dict = {
        "ok": False,
        "mode": "db_off",
        "checks": {
            "driver_available": False,
            "connection_ok": False,
            "graph_stats_ready": False,
        },
        "details": {
            "errors": [],
        },
    }

    # Check 1: Driver availability
    try:
        engine = get_control_engine()
        result["checks"]["driver_available"] = True
    except DbDriverMissingError as e:
        result["details"]["errors"].append(f"driver_missing: {e}")
        return result
    except DbUnavailableError as e:
        result["details"]["errors"].append(f"dsn_missing: {e}")
        return result
    except Exception as e:
        result["details"]["errors"].append(f"driver_check_error: {e}")
        return result

    # Check 2: Connection
    try:
        with engine.connect() as conn:
            # Simple connectivity test
            conn.execute(text("SELECT 1"))
            result["checks"]["connection_ok"] = True
    except OperationalError as e:
        result["details"]["errors"].append(f"connection_failed: {e}")
        result["mode"] = "db_off"
        return result
    except Exception as e:
        result["details"]["errors"].append(f"connection_error: {e}")
        result["mode"] = "db_off"
        return result

    # Check 3: graph_stats table
    try:
        with engine.connect() as conn:
            # Check if graph_stats_snapshots table exists and is queryable
            query = text(
                "SELECT 1 FROM gematria.graph_stats_snapshots LIMIT 1",
            )
            conn.execute(query)
            result["checks"]["graph_stats_ready"] = True
    except ProgrammingError as e:
        if "does not exist" in str(e) or "relation" in str(e).lower():
            result["details"]["errors"].append(
                "graph_stats_table_missing: gematria.graph_stats_snapshots does not exist"
            )
            result["mode"] = "partial"
            return result
        result["details"]["errors"].append(f"graph_stats_query_error: {e}")
        result["mode"] = "partial"
        return result
    except OperationalError as e:
        result["details"]["errors"].append(f"graph_stats_connection_error: {e}")
        result["mode"] = "partial"
        return result
    except Exception as e:
        result["details"]["errors"].append(f"graph_stats_error: {e}")
        result["mode"] = "partial"
        return result

    # All checks passed
    result["ok"] = True
    result["mode"] = "ready"
    return result


def main() -> int:
    """Main entry point."""
    health = check_db_health()
    print(json.dumps(health, indent=2))
    # Always exit 0 (safe for CI; JSON indicates status)
    return 0


if __name__ == "__main__":
    sys.exit(main())
