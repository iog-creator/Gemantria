from __future__ import annotations
from types import SimpleNamespace
from typing import Any, Dict

"""
SSOT adapter for noun objects coming from different agents.
Canonical internal noun shape (pipeline-wide).

Related Rules: Rule-048 (Organic AI Discovery), Rule-019 (Data Contracts)
Related ADRs: ADR-032 (Organic AI Discovery), ADR-019 (Data Contracts)
"""

CANONICAL_NOUN_SHAPE = {
    "noun_id": str,
    "surface": str,  # Hebrew surface
    "hebrew_text": str,  # == surface (alias, kept for older callers)
    "letters": list[str],
    "gematria_value": int,
    "class": str,  # person|place|thing|other
    "semantic_features": dict,  # optional computed bits
    "analysis": dict,  # enrichment notes live under analysis.theology
    "sources": list[dict],  # {ref, offset?}
}

_CLASS_MAP = {
    "person": "person",
    "place": "place",
    "thing": "thing",
    "other": "other",
    # tolerant fallbacks
    "entity": "thing",
    "object": "thing",
}


def _coerce_text(x: Any) -> str:
    # LLM clients sometimes return SimpleNamespace with .text; or raw strings
    if isinstance(x, SimpleNamespace) and hasattr(x, "text"):
        return str(x.text)
    return str(x) if x is not None else ""


def adapt_ai_noun(n: Dict[str, Any]) -> Dict[str, Any]:
    """
    Accepts variants like:
      {"hebrew": "...", "gematria": 123, "classification": "...", "letters":[...]}
      {"hebrew_text": "...", "gematria_value": 123, "class": "..."}
    Returns canonical internal noun shape (above).

    Rejects nouns with empty/null surface or "Unknown" placeholder.
    """
    # ids
    noun_id = n.get("noun_id") or n.get("id") or n.get("concept_id")
    # text - handle null explicitly
    surface_raw = n.get("surface") or n.get("hebrew") or n.get("hebrew_text")
    if surface_raw is None:
        surface_raw = ""
    surface = _coerce_text(surface_raw)

    # Reject nouns with empty surface or "Unknown" placeholder
    if not surface or surface.strip() == "" or surface == "Unknown":
        # Return a marker that validation should filter this out
        # (validate_batch_node will handle filtering)
        surface = ""  # Empty surface will be caught by validate_batch_node

    hebrew_text = surface  # alias for older callers
    # letters
    letters = n.get("letters") or []
    # gematria
    gem = n.get("gematria_value", n.get("gematria", 0))
    try:
        gem = int(gem or 0)
    except Exception:
        gem = 0
    # class
    cls_in = n.get("class") or n.get("classification") or "other"
    cls = _CLASS_MAP.get(str(cls_in).lower().strip(), "other")
    # semantic features & analysis
    sem = n.get("semantic_features") or {}
    analysis = n.get("analysis") or {}
    # sources
    sources = n.get("sources") or []

    return {
        "noun_id": noun_id,
        "surface": surface,
        "hebrew_text": hebrew_text,
        "letters": letters,
        "gematria_value": gem,
        "class": cls,
        "semantic_features": sem,
        "analysis": analysis,
        "sources": sources,
    }
