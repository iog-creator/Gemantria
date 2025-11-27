#!/usr/bin/env python3
"""
OPS Script: Register BibleScholar Tools in Control Plane
========================================================
Registers `search_bible_verses` and `lookup_lexicon_entry` in `control.tool_catalog`.
This ensures they are discoverable via the MCP Tool Catalog (Rule 052).
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.config.env import get_rw_dsn
import psycopg

TOOLS = [
    {
        "name": "search_bible_verses",
        "ring": 0,
        "io_schema": {
            "input": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search keyword (minimum 2 characters)"},
                    "translation": {"type": "string", "default": "KJV", "description": "Translation identifier"},
                    "limit": {"type": "integer", "default": 10, "description": "Maximum number of results"},
                },
                "required": ["query"],
            },
            "output": {
                "type": "object",
                "properties": {
                    "ok": {"type": "boolean"},
                    "results": {"type": "array"},
                    "count": {"type": "integer"},
                    "error": {"type": ["string", "null"]},
                },
            },
        },
    },
    {
        "name": "lookup_lexicon_entry",
        "ring": 0,
        "io_schema": {
            "input": {
                "type": "object",
                "properties": {"strongs_id": {"type": "string", "description": "Strong's number (e.g., 'H1', 'G1')"}},
                "required": ["strongs_id"],
            },
            "output": {
                "type": "object",
                "properties": {
                    "ok": {"type": "boolean"},
                    "entry": {"type": ["object", "null"]},
                    "found": {"type": "boolean"},
                    "error": {"type": ["string", "null"]},
                },
            },
        },
    },
]


def register_tools():
    dsn = get_rw_dsn()
    if not dsn:
        print("ERROR: GEMATRIA_DSN not set")
        sys.exit(1)

    try:
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                # Default project ID
                project_id = 1

                for tool in TOOLS:
                    print(f"Registering tool: {tool['name']}...")
                    cur.execute(
                        """
                        INSERT INTO control.tool_catalog (project_id, name, ring, io_schema, enabled, created_at)
                        VALUES (%s, %s, %s, %s, TRUE, NOW())
                        ON CONFLICT (project_id, name) DO UPDATE SET
                            io_schema = EXCLUDED.io_schema,
                            ring = EXCLUDED.ring,
                            enabled = TRUE
                        """,
                        (project_id, tool["name"], tool["ring"], json.dumps(tool["io_schema"])),
                    )
                conn.commit()
                print("✅ Tools registered successfully")
    except Exception as e:
        print(f"ERROR: Failed to register tools: {e}")
        sys.exit(1)


if __name__ == "__main__":
    register_tools()
