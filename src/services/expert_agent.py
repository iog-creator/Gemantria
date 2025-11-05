"""Expert agent for theological analysis."""

from __future__ import annotations

from src.services.lmstudio_client import THEOLOGY_MODEL, chat_completion


def analyze_theological(noun: dict) -> dict:
    """Provide expert theological analysis."""
    prompt = (
        f"Provide theological insight (150-250 words) for {noun.get('hebrew', '')} "
        f"({noun.get('name', '')}). Include scriptural context and significance."
    )
    results = chat_completion([{"role": "user", "content": prompt}], model=THEOLOGY_MODEL)
    if results:
        return {"text": results[0].text, "model": THEOLOGY_MODEL}
    return {"text": "", "model": THEOLOGY_MODEL}
