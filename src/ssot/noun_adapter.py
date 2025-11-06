"""
SSOT Noun Adapter

Adapts AI-generated nouns to SSOT format for downstream processing.
"""

from typing import Any, Dict
from src.infra.structured_logger import get_logger, log_json

LOG = get_logger("gematria.ssot.noun_adapter")


def adapt_ai_noun(raw_noun: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adapt an AI-generated noun to SSOT format.

    Ensures the noun has all required fields for downstream processing,
    normalizing field names and structures as needed.

    Args:
        raw_noun: Raw noun dictionary from AI processing

    Returns:
        Adapted noun in SSOT format
    """
    try:
        # Ensure basic required fields
        adapted = {
            "noun_id": raw_noun.get("noun_id", raw_noun.get("id", "")),
            "surface": raw_noun.get("surface", ""),
            "hebrew_text": raw_noun.get("surface", ""),  # Default to surface if no separate hebrew
            "class": raw_noun.get("class", "thing"),
            "book": raw_noun.get("book", ""),
            "confidence": raw_noun.get("confidence", 0.0),
        }

        # Copy over analysis if present
        if "analysis" in raw_noun:
            adapted["analysis"] = raw_noun["analysis"]

        # Copy over enrichment if present
        if "enrichment" in raw_noun:
            adapted["enrichment"] = raw_noun["enrichment"]

        # Copy over insights if present
        if "insights" in raw_noun:
            adapted["insights"] = raw_noun["insights"]

        # Copy over sources if present
        if "sources" in raw_noun:
            adapted["sources"] = raw_noun["sources"]

        log_json(LOG, 10, "noun_adapted", noun_id=adapted.get("noun_id", ""))
        return adapted

    except Exception as e:
        log_json(
            LOG,
            40,
            "noun_adaptation_failed",
            error=str(e),
            raw_keys=list(raw_noun.keys()) if isinstance(raw_noun, dict) else "non-dict",
        )
        # Return a minimal valid structure on error
        return {
            "noun_id": "",
            "surface": "",
            "hebrew_text": "",
            "class": "thing",
            "book": "",
            "confidence": 0.0,
        }
