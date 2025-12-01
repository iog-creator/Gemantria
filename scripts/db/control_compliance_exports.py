#!/usr/bin/env python3
"""
Control-plane compliance exports.

Exports three JSON artifacts:
- compliance.head.json: Overall compliance summary from both 7d and 30d windows
- top_violations_7d.json: Top violations from 7-day window
- top_violations_30d.json: Top violations from 30-day window

Uses centralized DSN loader (never os.getenv directly).
Tolerates empty/nonexistent DB (exits 0, writes JSON with ok=false for CI tolerance).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, UTC
from pathlib import Path

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.config.env import get_rw_dsn

try:
    import psycopg
except ImportError:
    print(
        "WARN: psycopg not available; skipping compliance exports (CI empty-DB tolerance).",
        file=sys.stderr,
    )
    # Write empty exports for CI tolerance
    output_dir = REPO / "share" / "atlas" / "control_plane"
    output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC).isoformat()
    for filename, window in [
        ("compliance.head.json", None),
        ("top_violations_7d.json", "7d"),
        ("top_violations_30d.json", "30d"),
    ]:
        payload = {
            "schema": "control",
            "generated_at": now,
            "ok": False,
            "connection_ok": False,
            "error": "psycopg not available",
        }
        if window:
            payload["window"] = window
            payload["violations"] = []
        else:
            payload["summary"] = None
        (output_dir / filename).write_text(json.dumps(payload, indent=2))
    sys.exit(0)

DSN = get_rw_dsn()
if not DSN:
    print("SKIP: GEMATRIA_DSN not set (empty-DB tolerance).", file=sys.stderr)
    # Write empty exports for CI tolerance
    output_dir = REPO / "share" / "atlas" / "control_plane"
    output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC).isoformat()
    for filename, window in [
        ("compliance.head.json", None),
        ("top_violations_7d.json", "7d"),
        ("top_violations_30d.json", "30d"),
    ]:
        payload = {
            "schema": "control",
            "generated_at": now,
            "ok": False,
            "connection_ok": False,
            "error": "DSN not set",
        }
        if window:
            payload["window"] = window
            payload["violations"] = []
        else:
            payload["summary"] = None
        (output_dir / filename).write_text(json.dumps(payload, indent=2))
    sys.exit(0)


def export_compliance_head(cur: psycopg.Cursor) -> dict:
    """Export overall compliance summary from both 7d and 30d windows."""
    try:
        # Query both MVs
        cur.execute("SELECT * FROM control.mv_compliance_7d LIMIT 1")
        row_7d = cur.fetchone()
        cur.execute("SELECT * FROM control.mv_compliance_30d LIMIT 1")
        row_30d = cur.fetchone()

        if not row_7d or not row_30d:
            return {
                "summary": None,
                "error": "Materialized views empty or not found",
            }

        # Extract data from rows
        # Row structure: (window, runs, por_ok_ratio, schema_ok_ratio, provenance_ok_ratio, violations_top, updated_at)
        summary = {
            "window_7d": {
                "runs": row_7d[1] if row_7d[1] is not None else 0,
                "por_ok_ratio": float(row_7d[2]) if row_7d[2] is not None else 0.0,
                "schema_ok_ratio": float(row_7d[3]) if row_7d[3] is not None else 0.0,
                "provenance_ok_ratio": float(row_7d[4]) if row_7d[4] is not None else 0.0,
                "updated_at": row_7d[6].isoformat() if row_7d[6] else None,
            },
            "window_30d": {
                "runs": row_30d[1] if row_30d[1] is not None else 0,
                "por_ok_ratio": float(row_30d[2]) if row_30d[2] is not None else 0.0,
                "schema_ok_ratio": float(row_30d[3]) if row_30d[3] is not None else 0.0,
                "provenance_ok_ratio": float(row_30d[4]) if row_30d[4] is not None else 0.0,
                "updated_at": row_30d[6].isoformat() if row_30d[6] else None,
            },
        }

        return {"summary": summary}
    except Exception as e:
        return {"summary": None, "error": str(e)}


def export_top_violations(cur: psycopg.Cursor, window: str) -> dict:
    """Export top violations for a given window (7d or 30d)."""
    mv_name = f"mv_compliance_{window}"
    try:
        cur.execute(f"SELECT violations_top FROM control.{mv_name} LIMIT 1")
        row = cur.fetchone()

        if not row or not row[0]:
            return {
                "window": window,
                "violations": [],
            }

        violations_top = row[0]  # jsonb object
        if not violations_top:
            return {
                "window": window,
                "violations": [],
            }

        # Convert jsonb object to list of {violation_code, count} dicts
        violations = [
            {"violation_code": code, "count": count} for code, count in violations_top.items()
        ]
        # Sort by count descending
        violations.sort(key=lambda x: x["count"], reverse=True)

        return {
            "window": window,
            "violations": violations,
        }
    except Exception as e:
        return {
            "window": window,
            "violations": [],
            "error": str(e),
        }


def main() -> int:
    """Generate compliance exports."""
    parser = argparse.ArgumentParser(description="Export control-plane compliance data")
    parser.add_argument(
        "--only",
        choices=["head", "7d", "30d"],
        help="Export only one artifact (default: all)",
    )
    args = parser.parse_args()

    output_dir = REPO / "share" / "atlas" / "control_plane"
    output_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(UTC).isoformat()

    # Determine which exports to generate
    export_head = args.only is None or args.only == "head"
    export_7d = args.only is None or args.only == "7d"
    export_30d = args.only is None or args.only == "30d"

    try:
        with psycopg.connect(DSN, autocommit=True) as conn:
            with conn.cursor() as cur:
                # Check if schema exists
                cur.execute(
                    "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = 'control')"
                )
                schema_exists = cur.fetchone()[0]

                if not schema_exists:
                    print(
                        "WARN: Control schema does not exist; writing DB-off exports.",
                        file=sys.stderr,
                    )
                    # Write DB-off exports
                    if export_head:
                        payload = {
                            "schema": "control",
                            "generated_at": now,
                            "ok": False,
                            "connection_ok": True,
                            "summary": None,
                            "error": "Schema does not exist",
                        }
                        (output_dir / "compliance.head.json").write_text(
                            json.dumps(payload, indent=2)
                        )

                    for filename, window in [
                        ("top_violations_7d.json", "7d"),
                        ("top_violations_30d.json", "30d"),
                    ]:
                        if (window == "7d" and export_7d) or (window == "30d" and export_30d):
                            payload = {
                                "schema": "control",
                                "generated_at": now,
                                "ok": False,
                                "connection_ok": True,
                                "window": window,
                                "violations": [],
                                "error": "Schema does not exist",
                            }
                            (output_dir / filename).write_text(json.dumps(payload, indent=2))
                    return 0

                # Generate exports
                if export_head:
                    result = export_compliance_head(cur)
                    payload = {
                        "schema": "control",
                        "generated_at": now,
                        "ok": result.get("summary") is not None and "error" not in result,
                        "connection_ok": True,
                        "summary": result.get("summary"),
                    }
                    if "error" in result:
                        payload["error"] = result["error"]
                    (output_dir / "compliance.head.json").write_text(json.dumps(payload, indent=2))
                    print("[control_compliance_exports] Wrote compliance.head.json")

                if export_7d:
                    result = export_top_violations(cur, "7d")
                    payload = {
                        "schema": "control",
                        "generated_at": now,
                        "ok": "error" not in result,
                        "connection_ok": True,
                        "window": result["window"],
                        "violations": result["violations"],
                    }
                    if "error" in result:
                        payload["error"] = result["error"]
                    (output_dir / "top_violations_7d.json").write_text(
                        json.dumps(payload, indent=2)
                    )
                    print(
                        f"[control_compliance_exports] Wrote top_violations_7d.json ({len(result['violations'])} violations)"
                    )

                if export_30d:
                    result = export_top_violations(cur, "30d")
                    payload = {
                        "schema": "control",
                        "generated_at": now,
                        "ok": "error" not in result,
                        "connection_ok": True,
                        "window": result["window"],
                        "violations": result["violations"],
                    }
                    if "error" in result:
                        payload["error"] = result["error"]
                    (output_dir / "top_violations_30d.json").write_text(
                        json.dumps(payload, indent=2)
                    )
                    print(
                        f"[control_compliance_exports] Wrote top_violations_30d.json ({len(result['violations'])} violations)"
                    )

                return 0

    except psycopg.Error as e:
        print(f"ERROR: Database error: {e}", file=sys.stderr)
        # Write error exports for CI tolerance
        if export_head:
            payload = {
                "schema": "control",
                "generated_at": now,
                "ok": False,
                "connection_ok": False,
                "summary": None,
                "error": str(e),
            }
            (output_dir / "compliance.head.json").write_text(json.dumps(payload, indent=2))

        for filename, window in [
            ("top_violations_7d.json", "7d"),
            ("top_violations_30d.json", "30d"),
        ]:
            if (window == "7d" and export_7d) or (window == "30d" and export_30d):
                payload = {
                    "schema": "control",
                    "generated_at": now,
                    "ok": False,
                    "connection_ok": False,
                    "window": window,
                    "violations": [],
                    "error": str(e),
                }
                (output_dir / filename).write_text(json.dumps(payload, indent=2))
        return 0  # Exit 0 for CI tolerance
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        # Write error exports for CI tolerance
        if export_head:
            payload = {
                "schema": "control",
                "generated_at": now,
                "ok": False,
                "connection_ok": False,
                "summary": None,
                "error": str(e),
            }
            (output_dir / "compliance.head.json").write_text(json.dumps(payload, indent=2))

        for filename, window in [
            ("top_violations_7d.json", "7d"),
            ("top_violations_30d.json", "30d"),
        ]:
            if (window == "7d" and export_7d) or (window == "30d" and export_30d):
                payload = {
                    "schema": "control",
                    "generated_at": now,
                    "ok": False,
                    "connection_ok": False,
                    "window": window,
                    "violations": [],
                    "error": str(e),
                }
                (output_dir / filename).write_text(json.dumps(payload, indent=2))
        return 0  # Exit 0 for CI tolerance


if __name__ == "__main__":
    sys.exit(main())
