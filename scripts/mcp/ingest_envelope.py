#!/usr/bin/env python3
"""
Ingest Knowledge MCP Envelope (PLAN-073 M1 E03)

Reads envelope JSON, validates against schema, and inserts/updates mcp.tools and mcp.endpoints.
Idempotent: same envelope → same final DB state.

Rule References: RFC-078 (Postgres Knowledge MCP), Rule 050 (OPS Contract),
Rule 039 (Execution Contract)

Usage:
    python scripts/mcp/ingest_envelope.py --envelope share/mcp/envelope.json
    make mcp.ingest.default
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

try:
    import psycopg
    from jsonschema import ValidationError, validate
    from scripts.config.env import get_rw_dsn
except ImportError as e:
    print(f"ERROR: Failed to import required modules: {e}", file=sys.stderr)
    sys.exit(1)

SCHEMA_PATH = ROOT / "schemas" / "mcp_ingest_envelope.v1.schema.json"
DEFAULT_ENVELOPE = ROOT / "share" / "mcp" / "envelope.json"


def load_schema() -> dict:
    """Load JSON schema for validation."""
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")
    return json.loads(SCHEMA_PATH.read_text())


def validate_envelope(data: dict, schema: dict) -> None:
    """Validate envelope data against schema."""
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        raise ValueError(f"Envelope validation failed: {e.message}") from e


def ingest_tools(conn: psycopg.Connection, tools: list[dict]) -> dict[str, int]:
    """Ingest tools into mcp.tools table."""
    counts = {"inserted": 0, "updated": 0, "skipped": 0}

    with conn.cursor() as cur:
        for tool in tools:
            name = tool["name"]
            description = tool["description"]
            tags = tool.get("tags", [])
            cost_est = tool.get("cost_est")
            visibility = tool.get("visibility", "public")

            # Check if tool exists
            cur.execute("SELECT name FROM mcp.tools WHERE name = %s", (name,))
            exists = cur.fetchone() is not None

            if exists:
                # Update existing tool
                cur.execute(
                    """
                    UPDATE mcp.tools
                    SET "desc" = %s, tags = %s, cost_est = %s, visibility = %s
                    WHERE name = %s
                    """,
                    (description, tags, cost_est, visibility, name),
                )
                if cur.rowcount > 0:
                    counts["updated"] += 1
                else:
                    counts["skipped"] += 1
            else:
                # Insert new tool
                cur.execute(
                    """
                    INSERT INTO mcp.tools (name, "desc", tags, cost_est, visibility)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (name, description, tags, cost_est, visibility),
                )
                counts["inserted"] += 1

    return counts


def ingest_endpoints(conn: psycopg.Connection, endpoints: list[dict]) -> dict[str, int]:
    """Ingest endpoints into mcp.endpoints table."""
    counts = {"inserted": 0, "updated": 0, "skipped": 0}

    with conn.cursor() as cur:
        for endpoint in endpoints:
            name = endpoint["name"]
            path = endpoint["path"]
            method = endpoint.get("method", "GET")
            auth = endpoint.get("auth", "none")
            notes = endpoint.get("notes", "")

            # Check if endpoint exists
            cur.execute("SELECT name FROM mcp.endpoints WHERE name = %s", (name,))
            exists = cur.fetchone() is not None

            if exists:
                # Update existing endpoint
                cur.execute(
                    """
                    UPDATE mcp.endpoints
                    SET path = %s, method = %s, auth = %s, notes = %s
                    WHERE name = %s
                    """,
                    (path, method, auth, notes, name),
                )
                if cur.rowcount > 0:
                    counts["updated"] += 1
                else:
                    counts["skipped"] += 1
            else:
                # Insert new endpoint
                cur.execute(
                    """
                    INSERT INTO mcp.endpoints (name, path, method, auth, notes)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (name, path, method, auth, notes),
                )
                counts["inserted"] += 1

    return counts


def main() -> int:
    """Main ingest logic."""
    parser = argparse.ArgumentParser(description="Ingest Knowledge MCP envelope")
    parser.add_argument(
        "--envelope",
        type=str,
        default=str(DEFAULT_ENVELOPE),
        help=f"Path to envelope JSON file (default: {DEFAULT_ENVELOPE})",
    )
    args = parser.parse_args()

    strict_mode = os.getenv("STRICT_MODE", "0") == "1"

    # Load and validate envelope
    envelope_path = Path(args.envelope)
    if not envelope_path.exists():
        if strict_mode:
            print(f"ERROR: Envelope file not found: {envelope_path}", file=sys.stderr)
            return 1
        else:
            print(f"HINT: Envelope file not found: {envelope_path} (HINT mode)", file=sys.stderr)
            return 0

    try:
        envelope_data = json.loads(envelope_path.read_text())
    except json.JSONDecodeError as e:
        error_msg = str(e).lower()
        if strict_mode:
            print(f"ERROR: Invalid JSON in envelope: {e}", file=sys.stderr)
            return 1
        else:
            print(f"HINT: Invalid JSON in envelope: {e} (HINT mode)", file=sys.stderr)
            return 0

    # Validate against schema
    try:
        schema = load_schema()
        validate_envelope(envelope_data, schema)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    # Get DSN
    dsn = get_rw_dsn()
    if not dsn:
        if strict_mode:
            print("ERROR: No RW DSN available (STRICT mode)", file=sys.stderr)
            return 1
        else:
            print("HINT: No RW DSN available (HINT mode)", file=sys.stderr)
            return 0

    # Ingest into database
    try:
        with psycopg.connect(dsn) as conn:
            tools = envelope_data.get("tools", [])
            endpoints = envelope_data.get("endpoints", [])

            tools_counts = ingest_tools(conn, tools)
            endpoints_counts = ingest_endpoints(conn, endpoints)

            conn.commit()

            # Print summary
            print(
                f"Tools: {tools_counts['inserted']} inserted, {tools_counts['updated']} updated, {tools_counts['skipped']} skipped"
            )
            print(
                f"Endpoints: {endpoints_counts['inserted']} inserted, {endpoints_counts['updated']} updated, {endpoints_counts['skipped']} skipped"
            )

            return 0

    except psycopg.Error as e:
        if strict_mode:
            print(f"ERROR: Database error: {e}", file=sys.stderr)
            return 1
        else:
            print(f"HINT: Database error: {e} (HINT mode)", file=sys.stderr)
            return 0
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
