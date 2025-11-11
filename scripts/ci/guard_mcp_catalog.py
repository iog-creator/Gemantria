#!/usr/bin/env python3
"""
guard.mcp.catalog — HINT mode

Checks that MCP catalog, endpoints SQL, and Atlas flow diagram exist.
Non-fatal (HINT-only); used for housekeeping and validation.
"""

import json
import pathlib
import sys

root = pathlib.Path(".")

sentinels = {
    "catalog": root / "docs" / "ops" / "mcp_catalog.sql",
    "endpoints_sql": root / "docs" / "ops" / "mcp_endpoints.sql",
    "atlas_flow": root / "docs" / "atlas" / "mcp_flow.mmd",
}

exists = {k: p.exists() for k, p in sentinels.items()}

report = {
    "ok_repo": all(exists.values()),
    "exists": exists,
    "notes": [
        "HINT: Catalog + endpoints + atlas flow should be present.",
        "HINT: Budget<=12 endpoints; outputs must be bounded JSON (k<=25).",
        "HINT: RO-on-tag DSN policy enforced by STRICT guard and CI.",
    ],
}

print(json.dumps(report, indent=2))
sys.exit(0)
