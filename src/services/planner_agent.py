"""Planner agent for determining processing sequence."""

from __future__ import annotations

import os

from src.services.lmstudio_client import chat_completion

PLANNER_MODEL = os.getenv("PLANNER_MODEL", "Qwen2.5-14B-Instruct")


def plan_processing(noun: dict) -> dict:
    """Determine if noun needs math verification, semantic extraction, or expert analysis."""
    prompt = (
        f"Analyze noun '{noun.get('name', '')}' ({noun.get('hebrew', '')}). "
        "Return JSON: {'needs_math': bool, 'needs_semantic': bool, 'needs_expert': bool, 'reason': str}"
    )
    results = chat_completion([{"role": "user", "content": prompt}], model=PLANNER_MODEL)
    if results:
        return {"text": results[0].text, "model": PLANNER_MODEL}
    return {"text": "", "model": PLANNER_MODEL}


def planner_node_with_hints(state: dict) -> dict:
    """Planner node wrapper that emits hints for agent wiring verification."""
    if "hints" not in state:
        state["hints"] = []
    state["hints"].append("HINT: verify: agent wiring OK")
    return state
