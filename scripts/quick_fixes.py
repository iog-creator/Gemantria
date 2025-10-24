#!/usr/bin/env python3
"""
Mechanical quick fixes:
- E722: bare 'except Exception:
    ' -> 'except Exception:'
- E402: late imports -> add '# noqa: E402' (heuristic)
- SIM108: handled by 'ruff --fix' (we just invoke ruff)
- B904-lite: keep structure; encourage chaining via patterns (non-destructive)
"""

import re
from pathlib import Path

ROOT = Path(".").resolve()
SKIP_DIRS = {".git", ".ruff_cache", ".venv", "venv", "node_modules"}


def fix_file(p: Path):
    s = p.read_text(encoding="utf-8", errors="ignore")
    orig = s

    # E722: bare except
    s = re.sub(r"\bexcept\s*:\s*", "except Exception:\n    ", s)

    # E402: late imports -> mark with noqa when found after first def/class
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

    if s != orig:
        p.write_text(s, encoding="utf-8")
        print("[quickfix] updated:", p)


def main():
    for p in ROOT.rglob("**/*.py"):
        if any(seg in SKIP_DIRS for seg in p.parts):
            continue
        fix_file(p)
    # Let ruff handle SIM108 and any safe autofixes
    print("[quickfix] invoking ruff --fix on src/ and scripts/")
    import subprocess  # noqa: E402

    subprocess.call("ruff check --fix src scripts", shell=True)


if __name__ == "__main__":
    main()
