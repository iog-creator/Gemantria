#!/usr/bin/env python3
"""
Control-plane capability rules export.

Exports capability_rule table data to share/atlas/control_plane/capability_rules.json
for Atlas integration.

Uses centralized DSN loader (never os.getenv directly).
Tolerates empty/nonexistent DB (exits 0, writes JSON with ok=false for CI tolerance).
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.config.env import get_rw_dsn

try:
    import psycopg
except ImportError:
    print(
        "WARN: psycopg not available; skipping capability rules export (CI empty-DB tolerance).",
        file=sys.stderr,
    )
    # Write empty export for CI tolerance
    output_dir = REPO / "share" / "atlas" / "control_plane"
    output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC).isoformat()
    payload = {
        "schema": "control",
        "generated_at": now,
        "ok": False,
        "connection_ok": False,
        "rules": [],
        "error": "psycopg not available",
    }
    (output_dir / "capability_rules.json").write_text(json.dumps(payload, indent=2))
    sys.exit(0)

DSN = get_rw_dsn()
if not DSN:
    print("SKIP: GEMATRIA_DSN not set (empty-DB tolerance).", file=sys.stderr)
    # Write empty export for CI tolerance
    output_dir = REPO / "share" / "atlas" / "control_plane"
    output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC).isoformat()
    payload = {
        "schema": "control",
        "generated_at": now,
        "ok": False,
        "connection_ok": False,
        "rules": [],
        "error": "DSN not set",
    }
    (output_dir / "capability_rules.json").write_text(json.dumps(payload, indent=2))
    sys.exit(0)


@dataclass
class CapabilityRulesExport:
    schema: str
    generated_at: str
    ok: bool
    connection_ok: bool
    rules: list[dict[str, Any]]
    error: str | None = None


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def db_off_payload(message: str) -> CapabilityRulesExport:
    return CapabilityRulesExport(
        schema="control",
        generated_at=now_iso(),
        ok=False,
        connection_ok=False,
        rules=[],
        error=message,
    )


def fetch_rules() -> CapabilityRulesExport:
    """Fetch capability rules from control.capability_rule table."""
    try:
        with psycopg.connect(DSN, autocommit=True) as conn:
            with conn.cursor() as cur:
                # Check if schema exists
                cur.execute(
                    "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = 'control')"
                )
                schema_exists = cur.fetchone()[0]

                if not schema_exists:
                    return db_off_payload("Control schema does not exist")

                # Check if table exists
                cur.execute(
                    "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_schema = 'control' AND table_name = 'capability_rule')"
                )
                table_exists = cur.fetchone()[0]

                if not table_exists:
                    return db_off_payload("control.capability_rule table does not exist")

                # row_to_json preserves all columns without us depending on schema details
                cur.execute(
                    "SELECT row_to_json(cr) FROM control.capability_rule AS cr ORDER BY cr.id;"
                )
                rows = cur.fetchall()

    except psycopg.Error as e:
        return db_off_payload(f"database error: {e}")
    except Exception as e:  # noqa: BLE001
        return db_off_payload(f"unexpected error: {e}")

    rules: list[dict[str, Any]] = []
    for row in rows:
        # row_to_json result is a single column
        obj = row[0]
        if isinstance(obj, dict):
            rules.append(obj)

    return CapabilityRulesExport(
        schema="control",
        generated_at=now_iso(),
        ok=True,
        connection_ok=True,
        rules=rules,
        error=None,
    )


def main() -> int:
    """Generate capability rules export."""
    output_dir = REPO / "share" / "atlas" / "control_plane"
    output_dir.mkdir(parents=True, exist_ok=True)

    export = fetch_rules()
    payload = asdict(export)
    output_path = output_dir / "capability_rules.json"
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=False),
        encoding="utf-8",
    )
    print(f"[control_capability_rules_export] Wrote {output_path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
