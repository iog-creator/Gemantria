#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
ALLOW = {
    "scripts/config/env.py",
}
EXCLUDE_DIRS = {".venv", "webui", "archive", "node_modules"}  # third-party code
WARN_ONLY_DIRS = {"scripts/smokes", "tests"}  # allow smokes/tests to evolve without blocking merges
PATTERNS = [re.compile(r"\bos\.getenv\b"), re.compile(r"\bos\.environ\b")]


def main() -> int:
    hits: list[tuple[str, int, str]] = []
    for p in ROOT.rglob("*.py"):
        rel = p.relative_to(ROOT).as_posix()
        # Skip allowed files
        if any(rel == a for a in ALLOW):
            continue
        # Skip excluded directories (third-party code)
        if any(rel.startswith(d + "/") or rel.startswith(d + "\\") for d in EXCLUDE_DIRS):
            continue
        text = p.read_text(errors="ignore")
        for i, line in enumerate(text.splitlines(), start=1):
            # Skip comments and docstrings
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            for rx in PATTERNS:
                if rx.search(line):
                    hits.append((rel, i, line.strip()))
    if not hits:
        print("ok: no direct env access outside scripts/config/env.py")
        return 0
    warn_only = all(any(h[0].startswith(d) for d in WARN_ONLY_DIRS) for h in hits)
    level = "HINT" if warn_only else "FAIL"
    print(f"{level}: direct env access detected (use scripts.config.env.env())")
    for rel, ln, line in hits:
        print(f"  {rel}:{ln}: {line}")
    return 0 if warn_only else 1


if __name__ == "__main__":
    raise SystemExit(main())
