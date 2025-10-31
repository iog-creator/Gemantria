#!/usr/bin/env python3
"""
Mechanical quick fixes:
- E722: replace bare 'except:' with 'except Exception:' preserving indentation
- E402: mark late imports with '# noqa: E402' (heuristic after first def/class)
- SIM108: handled by 'ruff --fix'
- B904: chain exceptions 'raise X(...) from e' when inside 'except ... as e:' blocks
  (only when 'raise' appears directly under the same indentation level)
"""

import re
import subprocess
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

RE_BARE_EXCEPT = re.compile(r"^(\s*)except\s*:\s*$")
RE_IMPORT = re.compile(r"\s*(from\s+\S+\s+import\s+\S+|import\s+\S+)")
RE_EXCEPT_AS = re.compile(r"^(\s*)except\s+[^\n]+?\s+as\s+([A-Za-z_]\w*)\s*:\s*$")
RE_RAISE_SIMPLE = re.compile(r"^(\s*)raise\s+([A-Za-z_][\w\.]*)\((.*)\)\s*$")


def fix_e722(lines: list[str]) -> list[str]:
    out = []
    for line in lines:
        m = RE_BARE_EXCEPT.match(line)
        if m:
            indent = m.group(1)
            out.append(f"{indent}except Exception:")
        else:
            out.append(line)
    return out


def fix_e402(lines: list[str]) -> list[str]:
    out = []
    seen_def_or_class = False
    for line in lines:
        if line.strip().startswith(("def ", "class ")):
            seen_def_or_class = True
        if seen_def_or_class and RE_IMPORT.match(line) and "noqa: E402" not in line:
            out.append(line + "  # noqa: E402")
        else:
            out.append(line)
    return out


def fix_b904(lines: list[str]) -> list[str]:
    """
    Within 'except ... as e:' blocks, convert 'raise X(...)' to 'raise X(...) from e'
    for the first raise at the same indentation level. Avoids touching multiline raise.
    """
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        m = RE_EXCEPT_AS.match(line)
        if not m:
            out.append(line)
            i += 1
            continue
        indent = m.group(1)
        exc_var = m.group(2)
        out.append(line)  # keep the except line
        i += 1
        while i < n:
            cur = lines[i]
            if cur.startswith(indent + "    "):  # inside block
                mr = RE_RAISE_SIMPLE.match(cur)
                if mr and mr.group(1) == indent + "    " and f" from {exc_var}" not in cur:
                    # Don't modify if 'from' already present
                    out.append(f"{mr.group(1)}raise {mr.group(2)}({mr.group(3)}) from {exc_var}")
                else:
                    out.append(cur)
                i += 1
            else:
                break  # block ended
        continue
    return out


def fix_file(p: Path) -> None:
    s = p.read_text(encoding="utf-8", errors="ignore")
    orig = s
    lines = s.splitlines()

    lines = fix_e722(lines)
    lines = fix_e402(lines)
    lines = fix_b904(lines)

    s2 = "\n".join(lines)
    if s2 != orig:
        p.write_text(s2 + ("\n" if not s2.endswith("\n") else ""), encoding="utf-8")
        print("[quickfix] updated:", p)


def main() -> None:
    for p in ROOT.rglob("**/*.py"):
        if any(seg in SKIP_DIRS for seg in p.parts):
            continue
        fix_file(p)
    # Let ruff apply SIM108 and other safe autofixes
    print("[quickfix] invoking ruff --fix on src/ and scripts/")
    subprocess.call("ruff check --fix src scripts", shell=True)


if __name__ == "__main__":
    main()
