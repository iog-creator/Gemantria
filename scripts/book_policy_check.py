#!/usr/bin/env python3
"""Quick policy check for chapter-mode governance gates."""

import os
import sys
from pathlib import Path

import yaml


def main():
    print("[policy] checking command_template placeholders and Rule003 append...")

    p = Path("config/book_plan.yaml")
    if not p.exists():
        print("[policy] error: config/book_plan.yaml not found")
        return 1

    cfg = yaml.safe_load(p.read_text())
    tmpl = cfg.get("command_template") or os.environ.get(
        "BOOK_EXTRACT_CMD_TEMPLATE", ""
    )

    missing = [ph for ph in ("{book}", "{chapter}", "{seed}") if ph not in tmpl]
    print(f"[policy] command_template: {tmpl if tmpl else '<unset>'}")
    print(f"[policy] missing placeholders: {missing or '<none>'}")

    if missing:
        return 2

    if "--noun-min" not in tmpl:
        print("[policy] runner will append: --noun-min 50")
    print("[policy] Rule003: NOUN_MIN will be set to 50 via env")

    return 0


if __name__ == "__main__":
    sys.exit(main())
