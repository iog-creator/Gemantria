"""Math agent client for gematria calculations verification."""

from __future__ import annotations

from src.services.lmstudio_client import MATH_MODEL, chat_completion


def verify_gematria_calculation(noun: dict, calculated_value: int) -> dict:
    """Verify gematria calculation using math model."""
    prompt = (
        f"Verify the gematria calculation for '{noun.get('hebrew', '')}' "
        f"({noun.get('name', '')}). Calculated value: {calculated_value}. "
        "Return JSON: {'verified': bool, 'confidence': float, 'reason': str}"
    )
    results = chat_completion([{"role": "user", "content": prompt}], model=MATH_MODEL)
    if results:
        return {"text": results[0].text, "model": MATH_MODEL}
    return {"text": "", "model": MATH_MODEL}
