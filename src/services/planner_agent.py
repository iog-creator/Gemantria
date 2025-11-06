"""Planning agent for noun processing strategy."""

from logging import getLogger
from types import SimpleNamespace
from typing import Any, Dict, List

from src.services.lmstudio_client import chat_completion
from src.ssot.noun_adapter import adapt_ai_noun

logger = getLogger(__name__)


def _text(x: Any) -> str:
    return x.text if isinstance(x, SimpleNamespace) and hasattr(x, "text") else (x or "")


def plan_from_ai_nouns(ai_nouns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Normalize AI nouns to SSOT and build a deterministic plan."""
    canon = [adapt_ai_noun(n) for n in ai_nouns]
    return {"nouns": canon, "count": len(canon)}


def plan_processing(noun: Dict[str, Any]) -> Dict[str, str]:
    """Plan processing strategy for a noun using LLM analysis.

    Args:
        noun: Noun dictionary with Hebrew text, gematria values, etc.

    Returns:
        Dictionary with 'text' key containing planning analysis.
    """
    # Handle both dict and object formats for noun fields
    if isinstance(noun, dict):
        hebrew_text = noun.get("hebrew", noun.get("hebrew_text", ""))
        gematria_value = noun.get("gematria", noun.get("gematria_value", 0))
    else:
        hebrew_text = getattr(noun, "hebrew", getattr(noun, "hebrew_text", ""))
        gematria_value = getattr(noun, "gematria", getattr(noun, "gematria_value", 0))

    # Create planning prompt
    messages = [
        {
            "role": "system",
            "content": """You are a biblical Hebrew expert analyzing nouns for gematria processing.
            Determine what types of analysis this noun needs:

            - needs_math: true if complex gematria calculations or mathematical patterns are required
            - needs_semantic: true if theological or semantic analysis would be valuable
            - needs_expert: true if this requires specialized biblical knowledge

            Return only valid JSON with these boolean fields.""",
        },
        {
            "role": "user",
            "content": f"Analyze this Hebrew noun for processing needs:\n\nHebrew: {hebrew_text}\nGematria: {gematria_value}\n\nReturn JSON with needs_math, needs_semantic, needs_expert fields.",
        },
    ]

    try:
        # Use the THEOLOGY_MODEL for planning
        model = "christian-bible-expert-v2.0-12b"  # Default theology model
        results = chat_completion([messages], model, temperature=0.0)
        if results and len(results) > 0:
            # Extract text from SimpleNamespace object
            text_content = results[0].text if hasattr(results[0], "text") else str(results[0])
            return {"text": text_content}
        else:
            # Fallback if no result
            return {"text": '{"needs_math": false, "needs_semantic": false, "needs_expert": false}'}
    except Exception:
        # Fail gracefully with default planning
        return {"text": '{"needs_math": false, "needs_semantic": false, "needs_expert": false}'}
