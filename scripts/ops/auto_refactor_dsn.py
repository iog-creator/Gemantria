#!/usr/bin/env python3
"""
Refactors Python files to use centralized DSN loader:

- dsn_rw() -> dsn_rw()
- dsn_rw() -> dsn_rw()
- ... for RO side -> dsn_ro()

Also ensures: from gemantria.dsn import dsn_ro, dsn_rw, dsn_atlas

Usage: auto_refactor_dsn.py file1.py file2.py ...
"""

import re, sys, pathlib as p

RW_KEYS = ["GEMATRIA_DSN", "RW_DSN", "AI_AUTOMATION_DSN", "ATLAS_DSN_RW", "ATLAS_DSN"]
RO_KEYS = ["BIBLE_RO_DSN", "RO_DSN", "ATLAS_DSN_RO", "ATLAS_DSN"]


def replace_env(text: str, keys, repl: str) -> str:
    # os.getenv("KEY") or os.environ.get("KEY")
    for k in keys:
        text = re.sub(rf'\bos\.getenv\(\s*"{re.escape(k)}"\s*\)', repl, text)
        text = re.sub(rf'\bos\.environ\.get\(\s*"{re.escape(k)}"\s*\)', repl, text)
    return text


def ensure_import(text: str) -> str:
    if "from gemantria.dsn import dsn_ro, dsn_rw, dsn_atlas" in text:
        return text
    # Insert after last import block or at top
    lines = text.splitlines(True)
    insert_at = 0
    for i, line in enumerate(lines[:50]):
        if line.lstrip().startswith("import ") or line.lstrip().startswith("from "):
            insert_at = i + 1
    lines.insert(insert_at, "from gemantria.dsn import dsn_ro, dsn_rw, dsn_atlas\n")
    return "".join(lines)


def process(path: p.Path) -> bool:
    src = path.read_text(encoding="utf-8")
    out = src
    out = replace_env(out, RW_KEYS, "dsn_rw()")
    out = replace_env(out, RO_KEYS, "dsn_ro()")
    if out != src:
        out = ensure_import(out)
        path.write_text(out, encoding="utf-8")
        return True
    return False


def main():
    changed = []
    for arg in sys.argv[1:]:
        fp = p.Path(arg)
        if fp.suffix != ".py" or not fp.exists():
            continue
        if process(fp):
            changed.append(str(fp))
    print("\n".join(changed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
