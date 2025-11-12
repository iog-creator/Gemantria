#!/usr/bin/env python3
"""Minimal query roundtrip for MCP catalog (E04)."""

from __future__ import annotations

import json
import pathlib
import sys

envdir = pathlib.Path("share/mcp/envelopes")
envdir.mkdir(parents=True, exist_ok=True)

items = sorted(envdir.glob("*.json"))
res = {"count": len(items), "first": None}

if items:
    data = json.loads(items[0].read_text())
    res["first"] = {"id": data["stamp"]["id"], "size": data["stamp"]["size"]}

out = pathlib.Path("share/mcp/query_result.json")
out.write_text(json.dumps(res, indent=2))

print(json.dumps(res))
