#!/usr/bin/env python3
"""
Smart mode decider for smoke + schema validation.
Picks STRICT or SOFT automatically and *emits guidance messages* for Cursor.

Decision rules (first true wins; can be manually overridden):
1) If CI=true or GITHUB_ACTIONS=true -> STRICT.
2) If current branch in ('main','master') or running on a tag -> STRICT.
3) If staged/changed files touch critical paths -> STRICT:
   - src/**, api_server.py, exports/*.json, docs/SSOT/*.json, .cursor/rules/**
4) If required services reachable (API:8000, LM chat:9991, embed:9994) -> STRICT.
5) Else -> SOFT (but emit [guide] instructions to bring services up).

The script executes the chosen targets:
- STRICT:  make test.smoke.strict && make schema.validate.temporal.strict
- SOFT:    make test.smoke && make schema.validate.temporal

Exit code mirrors downstream targets (non-zero on STRICT failure).
"""

from __future__ import annotations

import os
import re
import socket
import subprocess
import sys

RE_CRITICAL = re.compile(
    r"^(src/|api_server\.py$|exports/.*\.json$|docs/SSOT/.*\.json$|\.cursor/rules/)",
    re.I,
)


def _is_open(host: str, port: int, timeout: float = 0.6) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _changed_files() -> list[str]:
    cmds = [
        ["git", "diff", "--name-only"],
        ["git", "diff", "--name-only", "--cached"],
    ]
    changed: set[str] = set()
    for c in cmds:
        try:
            out = subprocess.check_output(c, text=True, stderr=subprocess.DEVNULL).strip().splitlines()
            changed.update([x.strip() for x in out if x.strip()])
        except Exception:
            pass
    return sorted(changed)


def _current_ref() -> tuple[str, bool]:
    # returns (branch_or_ref, is_tag)
    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()
    except Exception:
        branch = "unknown"
    is_tag = False
    try:
        desc = subprocess.check_output(
            ["git", "describe", "--tags", "--exact-match"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        is_tag = bool(desc)
        if is_tag:
            branch = desc
    except Exception:
        pass
    return branch, is_tag


def decide_mode() -> tuple[str, list[str]]:
    notes: list[str] = []
    # 0) Manual override knob for automation / CI debug
    override = os.getenv("AUTO_MODE", "").upper()
    if override in {"STRICT", "SOFT"}:
        notes.append(f"[guide] AUTO_MODE={override} → forcing {override} mode.")
        return override, notes

    # 1) CI signals
    if os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true":
        notes.append("[guide] CI detected → STRICT mode.")
        return "STRICT", notes

    # 2) Branch/tag
    branch, is_tag = _current_ref()
    if is_tag or branch in {"main", "master"}:
        notes.append(f"[guide] Protected ref ({branch}) → STRICT mode.")
        return "STRICT", notes

    # 3) Changed files
    changed = _changed_files()
    if any(RE_CRITICAL.search(p) for p in changed):
        crit = [p for p in changed if RE_CRITICAL.search(p)]
        notes.append(
            f"[guide] Critical changes detected ({', '.join(crit[:5])}"
            + ("…" if len(crit) > 5 else "")
            + ") → STRICT mode."
        )
        return "STRICT", notes

    # 4) Service reachability implies we can be strict
    api_host, api_port = (
        os.getenv("API_HOST", "127.0.0.1"),
        int(os.getenv("API_PORT", "8000")),
    )
    chat_host, chat_port = (
        os.getenv("LM_CHAT_HOST", "127.0.0.1"),
        int(os.getenv("LM_CHAT_PORT", "9991")),
    )
    emb_host, emb_port = (
        os.getenv("LM_EMBED_HOST", "127.0.0.1"),
        int(os.getenv("LM_EMBED_PORT", "9994")),
    )
    api_up = _is_open(api_host, api_port)
    chat_up = _is_open(chat_host, chat_port)
    emb_up = _is_open(emb_host, emb_port)
    if api_up and chat_up and emb_up:
        notes.append("[guide] All local services reachable (API:8000, chat:9991, embed:9994) → STRICT mode.")
        return "STRICT", notes

    # 5) Default soft with instructions
    notes.append("[guide] Services not detected → SOFT mode to keep dev flow unblocked.")
    notes.append("[guide] For STRICT locally: make test.smoke.strict && make schema.validate.temporal.strict")
    notes.append("[guide] Start services for STRICT: API :8000, LM chat :9991, LM embed :9994")
    return "SOFT", notes


def main() -> int:
    mode, notes = decide_mode()
    for n in notes:
        print(n)
    if mode == "STRICT":
        return subprocess.call("make test.smoke.strict && make schema.validate.temporal.strict", shell=True)
    else:
        # SOFT: allow skips/||true behavior
        return subprocess.call("make test.smoke && make schema.validate.temporal", shell=True)


if __name__ == "__main__":
    sys.exit(main())
