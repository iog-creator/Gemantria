# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
Add '# noqa: E501' to truly non-wrappable long lines:
- URLs / curl commands
- SQL keywords (SELECT/INSERT/UPDATE/DELETE/WITH) inside string literals
- Compiled regex patterns (re.compile(...)) where pattern literal is long
- Structured payload dumps (json.dumps, or large dict/array literals on one line)
- Logging calls (logger.debug/info/warning/error) with long f-strings or % formatting
Skips venv/.git/.ruff_cache and already-noqa'd lines.
Prefers a higher threshold (110) to let black wrap what it can.
"""

import re
from pathlib import Path

ROOT = Path(".").resolve()
SKIP_DIRS = {
    ".git",
    ".ruff_cache",
    ".venv",
    "venv",
    "node_modules",
    ".tox",
    ".pytest_cache",
}

# crude string-literal finder on a single line
PAT_STR = re.compile(r'(["\'])(?:(?=(\\?))\2.)*?\1')
KW_SQL = ("SELECT ", "INSERT ", "UPDATE ", "DELETE ", "WITH ")
LOG_PREFIXES = (
    "logger.debug(",
    "logger.info(",
    "logger.warning(",
    "logger.error(",
    "logger.exception(",
)
PAYLOAD_HINTS = (
    "json.dumps(",
    "json.loads(",
    "payload=",
    "headers=",
    "params=",
    "data=",
)


def has_sql_literal(line: str) -> bool:
    for m in PAT_STR.finditer(line):
        s = m.group(0).strip("\"'")
        if any(kw in s.upper() for kw in KW_SQL):
            return True
    return False


def has_regex_literal(line: str) -> bool:
    return "re.compile(" in line and bool(PAT_STR.search(line))


def is_url(line: str) -> bool:
    return "http://" in line or "https://" in line or "curl " in line


def is_logging(line: str) -> bool:
    return line.lstrip().startswith(LOG_PREFIXES)


def is_payload_like(line: str) -> bool:
    return any(h in line for h in PAYLOAD_HINTS) or line.strip().startswith(("{", "["))


def should_tag(line: str) -> bool:
    if len(line) <= 110:  # slightly higher bar
        return False
    if "noqa" in line:
        return False
    if is_url(line):
        return True
    if has_sql_literal(line):
        return True
    if has_regex_literal(line):
        return True
    if is_logging(line):
        return True
    return bool(is_payload_like(line))


def main() -> None:
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
