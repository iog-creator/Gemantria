#!/usr/bin/env python3
"""
Add '# noqa: E501' to truly non-wrappable long lines:
- URLs / curl commands
- SQL keywords (SELECT/INSERT/UPDATE/DELETE) within string literals
Skips files in venv/.git/.ruff_cache and already-noqa'd lines.
"""

import re
from pathlib import Path

ROOT = Path(".").resolve()
SKIP_DIRS = {".git", ".ruff_cache", ".venv", "venv", "node_modules"}
PAT_SQL = re.compile(r'(["\'])(?:(?=(\\?))\2.)*?\1')  # crude string-literal finder
KW_SQL = ("SELECT ", "INSERT ", "UPDATE ", "DELETE ", "WITH ")


def is_sql_literal(line: str) -> bool:
    for m in PAT_SQL.finditer(line):
        s = m.group(0).strip("\"'")
        if any(kw in s.upper() for kw in KW_SQL):
            return True
    return False


def should_tag(line: str) -> bool:
    if len(line) <= 100:
        return False
    if "noqa" in line:
        return False
    if "http://" in line or "https://" in line:
        return True
    if is_sql_literal(line):
        return True
    return False


def main():
    for p in ROOT.rglob("**/*.py"):
        if any(seg in SKIP_DIRS for seg in p.parts):
            continue
        txt = p.read_text(encoding="utf-8", errors="ignore").splitlines()
        changed = False
        for i, line in enumerate(txt):
            if should_tag(line):
                txt[i] = line + "  # noqa: E501"
                changed = True
        if changed:
            p.write_text("\n".join(txt) + "\n", encoding="utf-8")
            print("[longline] tagged:", p)


if __name__ == "__main__":
    main()
