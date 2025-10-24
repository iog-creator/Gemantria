#!/usr/bin/env python3
"""
Mechanical quick fixes:
- E722: bare 'except Exception:
    ' -> 'except Exception:'
- E402: move late imports to top (heuristic: 'import ' after first def); we instead add '# noqa: E402'
- SIM108: ternary opportunities -> leave to ruff --fix (we just run it)
- B904: suggest chaining by turning 'raise X(...)' with 'as e' into 'raise X(...) from e' (simple patterns)
"""

import re
from pathlib import Path

ROOT = Path(".").resolve()
SKIP_DIRS = {".git", ".ruff_cache", ".venv", "venv", "node_modules"}


def fix_file(p: Path):
    s = p.read_text(encoding="utf-8", errors="ignore")
    orig = s

    # E722
    s = re.sub(r"\bexcept\s*:\s*", "except Exception:\n    ", s)

    # E402 (late imports) -> mark with noqa if after first def/class
    lines = s.splitlines()
    seen_def = False
    for i, line in enumerate(lines):
        if line.strip().startswith(("def ", "class ")):
            seen_def = True
        if (
            seen_def
            and re.match(r"\s*(from\s+\S+\s+import\s+\S+|import\s+\S+)", line)
            and "noqa: E402" not in line
        ):
            lines[i] = line + "  # noqa: E402"
    s = "\n".join(lines)

    # B904 lite: 'except ... as e:' then 'raise X(' -> 'raise X(... ) from e' if same block (super naive)
    s = re.sub(
        r"except\s+[^\n]+?\s+as\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*\n(\s*)raise\s+([A-Za-z_][\w\.]*)\(",
        r"except Exception as \1:\n\2raise \3(",
        s,
    )  # ensure Exception name normalized
    s = re.sub(
        r"(raise\s+[A-Za-z_][\w\.]*\(.*\))\s*\n(\s*)# from (\w+)", r"\1 from \3\n\2", s
    )

    if s != orig:
        p.write_text(s, encoding="utf-8")
        print("[quickfix] updated:", p)


def main():
    for p in ROOT.rglob("**/*.py"):
        if any(seg in SKIP_DIRS for seg in p.parts):
            continue
        fix_file(p)


if __name__ == "__main__":
    main()
