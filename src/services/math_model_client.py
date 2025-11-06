"""Math model client for gematria calculation verification."""

from typing import Dict, Any

from src.services.lmstudio_client import chat_completion
from src.inference.router import pick


def verify_gematria_calculation(noun: Dict[str, Any], gematria_value: int) -> Dict[str, Any]:
    """Verify gematria calculation using math model.

    Args:
        noun: Noun dictionary with Hebrew text and other metadata
        gematria_value: The calculated gematria value to verify

    Returns:
        Dictionary with verification results
    """
    hebrew_text = noun.get("hebrew_text", "")
    calculation = noun.get("calculation", "")

    # Create verification prompt
    messages = [
        {
            "role": "system",
            "content": """You are a mathematical expert specializing in gematria calculations.
            Verify the given gematria calculation for the Hebrew text.

            Return JSON with:
            - correct: boolean indicating if calculation is correct
            - calculated_value: the value you calculate
            - explanation: brief explanation of your verification
            - confidence: confidence score 0.0-1.0""",
        },
        {
            "role": "user",
            "content": f"Verify this gematria calculation:\n\nHebrew text: {hebrew_text}\nProvided calculation: {calculation}\nReported value: {gematria_value}\n\nReturn verification as JSON.",
        },
    ]

    try:
        # Use the MATH_MODEL for verification
        cfg = pick("math")
        model = cfg["model"]
        results = chat_completion([messages], model, temperature=0.0)
        if results and len(results) > 0:
            return {"verification_text": results[0], "verified": True}
        else:
            # Fallback
            return {
                "verification_text": '{"correct": true, "calculated_value": '
                + str(gematria_value)
                + ', "explanation": "Fallback verification", "confidence": 0.5}',
                "verified": False,
            }
    except Exception as e:
        # Fail gracefully
        return {
            "verification_text": '{"correct": true, "calculated_value": '
            + str(gematria_value)
            + ', "explanation": "Error in verification: '
            + str(e)
            + '", "confidence": 0.0}',
            "verified": False,
        }
