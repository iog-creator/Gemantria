# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

"""
SSOT Noun Adapter

Adapts AI-discovered nouns to internal pipeline format.
"""

import uuid
from typing import Any, Dict


def adapt_ai_noun(ai_noun: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adapt an AI-discovered noun to internal pipeline format.

    Converts from AI discovery format to standardized internal representation.
    """
    # Generate deterministic noun_id from hebrew text if not present
    noun_id = ai_noun.get("noun_id")
    if not noun_id:
        # Use hebrew text as stable identifier
        hebrew = ai_noun.get("hebrew", "")
        noun_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"noun:{hebrew}"))

    adapted = {
        "noun_id": noun_id,
        "surface": ai_noun.get("hebrew", ""),
        "hebrew_text": ai_noun.get("hebrew", ""),
        "letters": ai_noun.get("letters", []),
        "gematria_value": ai_noun.get("gematria", 0),
        "gematria": ai_noun.get("gematria", 0),  # For compatibility
        "value": ai_noun.get("gematria", 0),  # For compatibility
        "class": ai_noun.get("classification", "unknown"),
        "classification": ai_noun.get("classification", "unknown"),
        "meaning": ai_noun.get("meaning", ""),
        "primary_verse": ai_noun.get("primary_verse", ""),
        "freq": ai_noun.get("freq", 0),
        "book": ai_noun.get("book", ""),
        "ai_discovered": ai_noun.get("ai_discovered", True),
        "sources": [],  # Will be populated during enrichment
    }

    return adapted
