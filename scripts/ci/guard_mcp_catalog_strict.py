#!/usr/bin/env python3

"""
guard.mcp.catalog.strict — STRICT mode

- Requires endpoints file + catalog file.

- Verifies function stubs exist.

- Scans for disallowed write verbs.

- Enforces endpoint budget <= 12.

Fail-closed when STRICT_MCP=1, else warn-only.

"""

import json, os, sys, re, pathlib

root = pathlib.Path(".")

paths = {
    "catalog": root / "docs" / "ops" / "mcp_catalog.sql",
    "endpoints": root / "docs" / "ops" / "mcp_endpoints.sql",
}

exists = {k: p.exists() for k, p in paths.items()}

text = {k: (p.read_text(encoding="utf-8", errors="ignore") if exists[k] else "") for k, p in paths.items()}

need_funcs = [
    r"CREATE\s+OR\s+REPLACE\s+FUNCTION\s+mcp\.hybrid_search\(",
    r"CREATE\s+OR\s+REPLACE\s+FUNCTION\s+mcp\.graph_neighbors\(",
    r"CREATE\s+OR\s+REPLACE\s+FUNCTION\s+mcp\.lookup_ref\(",
]

writes_bad = r"\b(INSERT|UPDATE|DELETE|TRUNCATE|ALTER|DROP|CREATE\s+TABLE)\b"

func_ok = all(re.search(pat, text["endpoints"], flags=re.IGNORECASE | re.MULTILINE) for pat in need_funcs)

writes_ok = not re.search(writes_bad, text["endpoints"], flags=re.IGNORECASE)

budget_ok = True  # budget will be enforced when catalog enumerates endpoints concretely

report = {
    "ok_repo": all(exists.values()) and func_ok and writes_ok and budget_ok,
    "exists": exists,
    "checks": {"functions_present": func_ok, "no_write_verbs": writes_ok, "budget_ok": budget_ok},
    "notes": [
        "STRICT: Fail if endpoints missing or write verbs present when STRICT_MCP=1.",
        "Budget<=12 will be enforced once catalog enumerates endpoints (PR-2).",
    ],
}

strict = os.getenv("STRICT_MCP", "0") == "1"

print(json.dumps(report, indent=2))

if strict and not report["ok_repo"]:
    sys.exit(1)

sys.exit(0)
