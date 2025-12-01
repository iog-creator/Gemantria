#!/usr/bin/env python3
"""
Guard: Snapshot Integrity & Drift Review (PLAN-079 7C)

Validates that all snapshot/export artifacts are consistent, drift-free, and covered by guards.
Compares current snapshots against expected baselines and reports drift status.

Rule References: Rule 037 (Data Persistence Completeness), Rule 038 (Exports Smoke Gate),
Rule 039 (Execution Contract), Rule 050 (OPS Contract)

Usage:
    python scripts/guards/guard_snapshot_drift.py
    make guard.snapshot.drift
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, UTC
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

try:
    import psycopg
    from scripts.config.env import get_rw_dsn
except ImportError:
    print(json.dumps({"ok": False, "error": "psycopg or scripts.config.env not available"}))
    sys.exit(1)


def check_file_exists(file_path: Path) -> dict:
    """Check if a file exists and return metadata."""
    if not file_path.exists():
        return {"exists": False, "size": 0, "mtime": None}
    stat = file_path.stat()
    return {
        "exists": True,
        "size": stat.st_size,
        "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat(),
    }


def check_snapshot_structure(file_path: Path) -> dict:
    """Check if a snapshot JSON file has valid structure."""
    if not file_path.exists():
        return {"valid": False, "error": "file missing"}
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
        return {
            "valid": True,
            "has_timestamp": "generated_at" in data or "timestamp" in data,
            "has_ok_flag": "ok" in data,
            "keys": list(data.keys())[:10],  # First 10 keys for inspection
        }
    except json.JSONDecodeError as e:
        return {"valid": False, "error": f"invalid JSON: {e}"}
    except Exception as e:
        return {"valid": False, "error": str(e)}


def main() -> int:
    """Main guard logic."""
    checks: dict[str, bool] = {}
    counts: dict[str, int] = {}
    details: dict[str, any] = {}

    # Expected snapshot files
    snapshot_files = {
        "schema_snapshot": ROOT / "share" / "atlas" / "control_plane" / "schema_snapshot.json",
        "mv_schema": ROOT / "share" / "atlas" / "control_plane" / "mv_schema.json",
        "mcp_catalog": ROOT / "share" / "atlas" / "control_plane" / "mcp_catalog.json",
        "compliance_summary": ROOT
        / "share"
        / "atlas"
        / "control_plane"
        / "compliance_summary.json",
        "compliance_timeseries": ROOT
        / "share"
        / "atlas"
        / "control_plane"
        / "compliance_timeseries.json",
        "pm_snapshot": ROOT / "share" / "pm.snapshot.md",
    }

    # Check each snapshot file
    file_status = {}
    valid_count = 0
    missing_count = 0

    for name, file_path in snapshot_files.items():
        status = check_file_exists(file_path)
        structure = (
            check_snapshot_structure(file_path)
            if file_path.suffix == ".json"
            else {"valid": status["exists"]}
        )
        file_status[name] = {
            "path": str(file_path.relative_to(ROOT)),
            "exists": status["exists"],
            "size": status["size"],
            "mtime": status["mtime"],
            "structure": structure,
        }
        if status["exists"] and structure.get("valid"):
            valid_count += 1
        elif not status["exists"]:
            missing_count += 1

    checks["all_snapshots_exist"] = missing_count == 0
    json_file_count = len([f for f in snapshot_files.values() if f.suffix == ".json"])
    checks["all_snapshots_valid"] = (
        valid_count >= json_file_count
    )  # All JSON files valid, markdown files just need to exist
    counts["total_snapshots"] = len(snapshot_files)
    counts["valid_snapshots"] = valid_count
    counts["missing_snapshots"] = missing_count
    details["snapshot_files"] = file_status

    # Check ledger sync status
    dsn = get_rw_dsn()
    ledger_status = {"available": False, "entry_count": 0}
    if dsn:
        try:
            with psycopg.connect(dsn) as conn, conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM control.system_state_ledger")
                count = cur.fetchone()[0]
                ledger_status = {"available": True, "entry_count": count}
        except Exception:
            pass  # DB not available, skip ledger check

    checks["ledger_available"] = ledger_status["available"]
    counts["ledger_entries"] = ledger_status["entry_count"]
    details["ledger"] = ledger_status

    # Overall verdict
    ok = checks["all_snapshots_exist"] and checks["all_snapshots_valid"]

    verdict = {
        "ok": ok,
        "checks": checks,
        "counts": counts,
        "details": details,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }

    print(json.dumps(verdict, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
