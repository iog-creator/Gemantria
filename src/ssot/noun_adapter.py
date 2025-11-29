# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

"""
SSOT Noun Adapter

Adapts AI-discovered nouns to internal pipeline format.
Enforces Ketiv-primary policy per ADR-002: Ketiv (written form) is primary for gematria calculations.
"""

import uuid
from typing import Any, Dict


def adapt_ai_noun(ai_noun: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adapt an AI-discovered noun to internal pipeline format.

    Converts from AI discovery format to standardized internal representation.
    Enforces Ketiv-primary policy: surface field contains Ketiv (written form),
    which is used for gematria calculations. Qere (read form) is stored as variant.

    Args:
        ai_noun: Dictionary with noun data from AI discovery
            - hebrew: Primary Hebrew text (should be Ketiv if variant exists)
            - variant_type: Optional, "ketiv" or "qere"
            - variant_surface: Optional, alternative form (Qere if this is Ketiv)
            - span_start, span_end: Optional, character positions in source text

    Returns:
        Adapted noun dictionary with Ketiv-primary fields
    """
    # Generate deterministic noun_id from hebrew text if not present
    noun_id = ai_noun.get("noun_id")
    if not noun_id:
        # Use hebrew text as stable identifier (Ketiv if available)
        hebrew = ai_noun.get("hebrew", "")
        noun_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"noun:{hebrew}"))

    # Ketiv-primary policy: surface contains Ketiv (written form)
    # This is the form used for gematria calculations per ADR-002
    surface = ai_noun.get("hebrew", "")
    variant_type = ai_noun.get("variant_type", "ketiv")
    variant_surface = ai_noun.get("variant_surface", "")
    is_ketiv = variant_type == "ketiv" or not variant_surface

    # If variant_surface is provided and this is marked as Qere,
    # swap so that Ketiv is in surface
    if variant_type == "qere" and variant_surface:
        # Qere provided as primary, swap to make Ketiv primary
        surface, variant_surface = variant_surface, surface
        is_ketiv = True

    adapted = {
        "noun_id": noun_id,
        "surface": surface,  # Ketiv (written form) - primary for gematria
        "hebrew_text": surface,  # Alias for compatibility
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
        # Phase 2: Ketiv/Qere variant tracking
        "variant_type": variant_type if variant_surface else None,
        "variant_surface": variant_surface if variant_surface else None,
        "span_start": ai_noun.get("span_start"),
        "span_end": ai_noun.get("span_end"),
        "is_ketiv": is_ketiv,
    }

    return adapted
