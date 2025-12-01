#!/usr/bin/env python3
"""
Governance Freshness Export for PM Share Package

Generates summary format with:
- Latest emission timestamps per rule
- Rule update dates
- Stale artifact counts (per rule and per artifact type)

Uses centralized DSN loader (never os.getenv directly).
Tolerates empty/nonexistent DB (exits 0, writes empty export for CI tolerance).
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, UTC
from pathlib import Path
from typing import Any

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.config.env import get_rw_dsn

try:
    import psycopg
except ImportError:
    psycopg = None

OUT_DIR = REPO / "share"
OUT_FILE = OUT_DIR / "governance_freshness.json"

# Staleness threshold: artifacts older than 24 hours are considered stale
STALENESS_HOURS = 24


def now_iso() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now(UTC).isoformat()


def db_off_export(error: str) -> dict[str, Any]:
    """Generate empty export for DB-off scenarios."""
    return {
        "schema": "governance_freshness.v1",
        "generated_at": now_iso(),
        "summary": {
            "artifacts_total": 0,
            "artifacts_stale": 0,
            "hints_total": 0,
            "hints_stale": 0,
            "rules_total": 0,
            "rules_with_stale_artifacts": 0,
            "max_staleness_days": 0,
        },
        "by_rule": [],
        "by_artifact_type": [],
        "db_off": True,
        "error": error,
    }


def export_governance_freshness(conn: psycopg.Connection) -> dict[str, Any]:
    """Export governance freshness summary."""
    staleness_threshold = datetime.now(UTC) - timedelta(hours=STALENESS_HOURS)

    with conn.cursor() as cur:
        # Get all governance artifacts
        cur.execute(
            """
            SELECT
                artifact_type,
                artifact_name,
                rule_references,
                updated_at,
                created_at
            FROM governance_artifacts
            ORDER BY updated_at DESC
            """
        )
        artifacts = cur.fetchall()

        # Get all hint emissions
        cur.execute(
            """
            SELECT
                rule_reference,
                emitted_at
            FROM hint_emissions
            WHERE rule_reference IS NOT NULL
            ORDER BY emitted_at DESC
            """
        )
        hint_emissions = cur.fetchall()

    # Process artifacts by rule
    rule_data: dict[str, dict[str, Any]] = {}
    artifact_type_data: dict[str, dict[str, Any]] = {}

    for artifact in artifacts:
        artifact_type, _artifact_name, rule_refs, updated_at, _created_at = artifact
        is_stale = updated_at < staleness_threshold if updated_at else True

        # Process by rule
        if rule_refs:
            for rule_ref in rule_refs:
                if rule_ref not in rule_data:
                    rule_data[rule_ref] = {
                        "rule": rule_ref,
                        "last_artifact_update": None,
                        "last_hint_emission": None,
                        "artifacts_stale": 0,
                        "artifacts_total": 0,
                        "stale": False,
                    }
                rule_data[rule_ref]["artifacts_total"] += 1
                if is_stale:
                    rule_data[rule_ref]["artifacts_stale"] += 1
            last_update_str = rule_data[rule_ref]["last_artifact_update"]
            if last_update_str:
                last_update_dt = datetime.fromisoformat(last_update_str.replace("Z", "+00:00"))
            else:
                last_update_dt = None
            if last_update_dt is None or (updated_at and updated_at > last_update_dt):
                rule_data[rule_ref]["last_artifact_update"] = updated_at.isoformat() if updated_at else None
                if is_stale:
                    rule_data[rule_ref]["stale"] = True

        # Process by artifact type
        if artifact_type not in artifact_type_data:
            artifact_type_data[artifact_type] = {
                "type": artifact_type,
                "fresh": 0,
                "stale": 0,
                "oldest_stale": None,
            }
        if is_stale:
            artifact_type_data[artifact_type]["stale"] += 1
            oldest_stale_str = artifact_type_data[artifact_type]["oldest_stale"]
            if oldest_stale_str:
                oldest_stale_dt = datetime.fromisoformat(oldest_stale_str.replace("Z", "+00:00"))
            else:
                oldest_stale_dt = None
            if oldest_stale_dt is None or (updated_at and updated_at < oldest_stale_dt):
                artifact_type_data[artifact_type]["oldest_stale"] = updated_at.isoformat() if updated_at else None
        else:
            artifact_type_data[artifact_type]["fresh"] += 1

    # Process hint emissions by rule
    for hint_emission in hint_emissions:
        rule_ref, emitted_at = hint_emission
        if rule_ref:
            if rule_ref not in rule_data:
                rule_data[rule_ref] = {
                    "rule": rule_ref,
                    "last_artifact_update": None,
                    "last_hint_emission": None,
                    "artifacts_stale": 0,
                    "artifacts_total": 0,
                    "stale": False,
                }
            last_hint_str = rule_data[rule_ref]["last_hint_emission"]
            if last_hint_str:
                last_hint_dt = datetime.fromisoformat(last_hint_str.replace("Z", "+00:00"))
            else:
                last_hint_dt = None
            if last_hint_dt is None or (emitted_at and emitted_at > last_hint_dt):
                rule_data[rule_ref]["last_hint_emission"] = emitted_at.isoformat() if emitted_at else None

    # Calculate summary
    artifacts_total = len(artifacts)
    artifacts_stale = sum(1 for a in artifacts if a[3] and a[3] < staleness_threshold)
    hints_total = len(hint_emissions)
    hints_stale = sum(1 for h in hint_emissions if h[1] and h[1] < staleness_threshold)
    rules_total = len(rule_data)
    rules_with_stale = sum(1 for r in rule_data.values() if r["stale"])

    # Calculate max staleness in days
    max_staleness_days = 0
    for artifact in artifacts:
        if artifact[3] and artifact[3] < staleness_threshold:
            days = (staleness_threshold - artifact[3]).total_seconds() / 86400
            max_staleness_days = max(max_staleness_days, days)

    return {
        "schema": "governance_freshness.v1",
        "generated_at": now_iso(),
        "summary": {
            "artifacts_total": artifacts_total,
            "artifacts_stale": artifacts_stale,
            "hints_total": hints_total,
            "hints_stale": hints_stale,
            "rules_total": rules_total,
            "rules_with_stale_artifacts": rules_with_stale,
            "max_staleness_days": round(max_staleness_days, 2),
        },
        "by_rule": sorted(rule_data.values(), key=lambda x: x["rule"]),
        "by_artifact_type": sorted(artifact_type_data.values(), key=lambda x: x["type"]),
        "db_off": False,
    }


def main() -> int:
    """Main entrypoint."""
    # Ensure output directory exists
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if psycopg is None:
        print(
            "WARN: psycopg not available; writing empty export (CI empty-DB tolerance).",
            file=sys.stderr,
        )
        export_data = db_off_export("psycopg not available")
        OUT_FILE.write_text(
            json.dumps(export_data, indent=2, default=str),
            encoding="utf-8",
        )
        return 0

    dsn = get_rw_dsn()
    if not dsn:
        print("SKIP: GEMATRIA_DSN not set (empty-DB tolerance).", file=sys.stderr)
        export_data = db_off_export("DSN not set")
        OUT_FILE.write_text(
            json.dumps(export_data, indent=2, default=str),
            encoding="utf-8",
        )
        return 0

    try:
        with psycopg.connect(dsn) as conn:
            export_data = export_governance_freshness(conn)
            OUT_FILE.write_text(
                json.dumps(export_data, indent=2, default=str),
                encoding="utf-8",
            )
            print(
                f"✅ Exported governance freshness: {export_data['summary']['rules_total']} rules, "
                f"{export_data['summary']['artifacts_total']} artifacts"
            )
    except Exception as exc:
        print(f"ERROR: Failed to export governance freshness: {exc}", file=sys.stderr)
        export_data = db_off_export(f"database error: {exc!s}")
        OUT_FILE.write_text(
            json.dumps(export_data, indent=2, default=str),
            encoding="utf-8",
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
