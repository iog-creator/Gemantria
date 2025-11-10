#!/usr/bin/env python3
"""
Rewrite common DSN patterns to the central shim:
  - os.getenv(...DSN...)          -> dsn_ro/dsn_rw (heuristic)
  - scripts.config.env functions  -> gemantria.dsn functions
  - psycopg.connect("postgres..") -> psycopg.connect(dsn_ro/dsn_rw)
  - create_engine("postgres..")   -> create_engine(dsn_ro/dsn_rw)
Heuristics:
  * If pattern includes "RW" or "WRITE" or "GEMATRIA_DSN" -> dsn_rw
  * If pattern includes "BIBLE" or "RO" -> dsn_ro
  * Else -> dsn_rw (default)
"""

from __future__ import annotations
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

PY_PATTERNS = [
    (re.compile(r"os\.getenv\([^)]*DSN[^)]*\)"), "shim"),  # env lookups
    (re.compile(r"os\.environ\[[^\]]*DSN[^\]]*\]"), "shim"),
    (re.compile(r"os\.environ\.get\([^)]*DSN[^)]*\)"), "shim"),
    (re.compile(r"create_engine\(\s*[\"']postgres[^\)]*[\"']\s*\)"), "engine"),
    (re.compile(r"psycopg\.(connect|Connection)\(\s*[\"']postgres[^\)]*[\"']\s*\)"), "psycopg"),
]


def choose_func(text: str) -> str:
    t = text.upper()
    if "RW" in t or "WRITE" in t or "GEMATRIA_DSN" in t or "AI_AUTOMATION" in t:
        return "dsn_rw"
    if "BIBLE" in t or "RO" in t or "READ" in t:
        return "dsn_ro"
    return "dsn_rw"  # default to RW for safety


def ensure_import(lines: list[str]) -> list[str]:
    hdr = "from gemantria.dsn import dsn_ro, dsn_rw, dsn_atlas"
    for i, l in enumerate(lines[:30]):
        if "from gemantria.dsn import" in l:
            return lines
        # Remove old imports
        if "from scripts.config.env import" in l:
            lines[i] = hdr + "\n"
            return lines
    # insert after first future/import block if present
    ins = 0
    for i, l in enumerate(lines[:40]):
        if l.startswith("from __future__") or l.startswith("import ") or l.startswith("from "):
            ins = i + 1
    lines.insert(ins, hdr + "\n")
    return lines


def rewrite(path: pathlib.Path) -> bool:
    text = path.read_text()
    orig = text

    # Replace scripts.config.env imports and function calls
    text = re.sub(
        r"from scripts\.config\.env import (get_rw_dsn|get_bible_db_dsn)(?:, (get_rw_dsn|get_bible_db_dsn))?",
        "from gemantria.dsn import dsn_ro, dsn_rw, dsn_atlas",
        text,
    )
    text = re.sub(r"\bget_rw_dsn\(\)", "dsn_rw()", text)
    text = re.sub(r"\bget_bible_db_dsn\(\)", "dsn_ro()", text)

    # Handle direct os.getenv/os.environ patterns
    for pat, kind_val in PY_PATTERNS:

        def _repl(m, k=kind_val):
            chunk = m.group(0)
            func = choose_func(chunk)
            if k == "engine":
                return f"create_engine({func}())"
            if k == "psycopg":
                return re.sub(r"psycopg\.(connect|Connection)\([^)]*\)", f"psycopg.connect({func}())", chunk)
            return func + "()"  # env -> direct call

        text = pat.sub(_repl, text)

    if text != orig:
        lines = text.splitlines(True)
        lines = ensure_import(lines)
        path.write_text("".join(lines))
        return True
    return False


def main(files: list[str]) -> int:
    changed = 0
    for f in files:
        p = ROOT / f
        if not p.exists() or not p.suffix == ".py":
            continue
        if rewrite(p):
            changed += 1
            print(f"Rewrote: {f}")
    print(f"{changed} files rewritten")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
