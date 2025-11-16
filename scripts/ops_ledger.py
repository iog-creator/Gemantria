#!/usr/bin/env python3
"""OPS Command Ledger helper.

Minimal, file-based ledger that records successful command bundles used in OPS blocks.
This is intentionally simple; the goal is to seed a corpus that later DSPy/agents can mine.
"""

import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict

LEDGER_PATH = Path("share/ops_command_ledger.jsonl")


def append_entry(entry: Dict[str, Any]) -> None:
    """Append an OPS command ledger entry as JSONL.

    Caller is responsible for providing a unique 'id'.
    This function will add 'created_at' if missing.

    Args:
        entry: Dictionary with ledger entry fields:
            - id: Unique identifier (required)
            - phase: Phase identifier (e.g., "Phase-7B")
            - plan_ref: Plan reference (e.g., "PLAN-077")
            - category: Category (e.g., "lm_config")
            - description: Human-readable description
            - commands: List of command strings
            - status: Status (e.g., "success")
            - created_at: ISO timestamp (auto-added if missing)
    """
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)

    entry = dict(entry)
    entry.setdefault("created_at", datetime.now(tz=UTC).isoformat().replace("+00:00", "Z"))

    with LEDGER_PATH.open("a", encoding="utf-8") as f:
        json.dump(entry, f, ensure_ascii=False)
        f.write("\n")
