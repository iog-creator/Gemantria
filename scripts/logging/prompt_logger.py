#!/usr/bin/env python3
"""
Prompt archiving logger for LLM interactions.

Logs all LLM prompts and responses to prompts/run_<timestamp>.jsonl for
reproducibility, debugging, and STRICT compliance.

Usage:
    from scripts.logging.prompt_logger import log_prompt
    log_prompt("enrich_nouns", prompt_text, response_text)
"""

from __future__ import annotations

import datetime
import json
import os
import pathlib
from typing import Any

LOG_DIR = pathlib.Path("prompts")
LOG_DIR.mkdir(exist_ok=True)
LOG_ENV = os.environ.get("ENABLE_PROMPT_LOGGING", "0") == "1"


def log_prompt(agent: str, input: str, response: str) -> None:
    """
    Log a prompt and response to a timestamped JSONL file.

    Args:
        agent: Agent name (e.g., "enrich_nouns", "score_graph")
        input: The prompt/input text sent to the LLM
        response: The response text received from the LLM

    The log file is named prompts/run_YYYY-MM-DD.jsonl and contains one
    JSON object per line with timestamp, agent, input, and response fields.
    """
    if not LOG_ENV:
        return

    ts = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    trace: dict[str, Any] = {
        "timestamp": ts,
        "agent": agent,
        "input": input,
        "response": response,
    }

    fname = LOG_DIR / f"run_{ts[:10]}.jsonl"
    with open(fname, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(trace, ensure_ascii=False) + "\n")
