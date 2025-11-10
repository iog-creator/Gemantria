#!/usr/bin/env python3
"""
Normalize env loader imports in Python files changed by DSN burndown:

- Move `from scripts.config.env import get_rw_dsn, get_bible_db_dsn` to the top
  import block (never inside try/except).
- Drop `get_bible_db_dsn` from the import if it's unused in the file.
- Deduplicate multiple occurrences.
"""

import sys, re, pathlib as p

IMPORT_LINE_FULL = "from scripts.config.env import get_rw_dsn, get_bible_db_dsn"
IMPORT_RW_ONLY = "from scripts.config.env import get_rw_dsn"


def normalize(path: p.Path) -> bool:
    if not path.exists() or path.suffix != ".py":
        return False
    text = path.read_text(encoding="utf-8")
    orig = text

    # Remove any occurrences of the full import anywhere; we will reinsert normalized.
    text = re.sub(
        r"^\s*from\s+scripts\.config\.env\s+import\s+get_rw_dsn,\s*get_bible_db_dsn\s*$",
        "",
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(
        r"^\s*from\s+scripts\.config\.env\s+import\s+get_rw_dsn\s*$",
        "",
        text,
        flags=re.MULTILINE,
    )

    uses_rw = re.search(r"\bget_rw_dsn\s*\(", text) is not None
    uses_ro = re.search(r"\bget_bible_db_dsn\s*\(", text) is not None
    if not (uses_rw or uses_ro):
        # Nothing to add; just write back if we removed duplicates.
        if text != orig:
            path.write_text(text, encoding="utf-8")
            return True
        return False

    # Find insertion point after the last top import line (first 80 lines heuristic).
    lines = text.splitlines(True)
    insert_at = 0
    for i, line in enumerate(lines[:80]):
        s = line.lstrip()
        if s.startswith("import ") or s.startswith("from "):
            insert_at = i + 1
        elif s and not s.startswith(("#", '"""', "'''")):
            # First non-import, non-comment line: stop scanning.
            break

    import_line = IMPORT_LINE_FULL if uses_ro else IMPORT_RW_ONLY
    lines.insert(insert_at, import_line + "\n")
    new = "".join(lines)
    if new != orig:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def main(argv):
    changed = []
    for a in argv[1:]:
        fp = p.Path(a)
        if normalize(fp):
            changed.append(str(fp))
    print("\n".join(changed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
